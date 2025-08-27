# =====================================================================================
# TinyLlama Fine-Tuning Script for CV Parsing
# =====================================================================================
#
# INSTRUCTIONS:
#
# 1. Open Google Colab (colab.research.google.com).
# 2. Go to File -> New notebook.
# 3. Go to Runtime -> Change runtime type, and select "T4 GPU" as the hardware accelerator.
# 4. Copy and paste this ENTIRE script into the first cell of the notebook.
# 5. Fill in your details in the CONFIGURATION section below.
# 6. Click the "Play" button to run the cell.
#
# The process will take 1-3 hours. Do not close the browser tab.
#
# =====================================================================================

# ------------------------------------------------------------------
# 1. CONFIGURATION - FILL IN YOUR DETAILS HERE
# ------------------------------------------------------------------
HF_USERNAME = "Dulaj98"  # Your Hugging Face username
HF_DATASET_NAME = "cv-parsing-dataset" # The name of the dataset you created
HF_TOKEN = "your-hf-write-token" # The WRITE access token you generated
NEW_MODEL_NAME = "tinyllama-cv-parser-v1" # The name for your new, fine-tuned model
# ------------------------------------------------------------------

# ------------------------------------------------------------------
# 2. INSTALL DEPENDENCIES
# ------------------------------------------------------------------
print("Installing dependencies...")
!pip install -q -U transformers datasets accelerate peft bitsandbytes trl

import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    pipeline,
)
from peft import LoraConfig, PeftModel, get_peft_model
from trl import SFTTrainer
import json

print("Dependencies installed.")

# ------------------------------------------------------------------
# 3. LOGIN TO HUGGING FACE
# ------------------------------------------------------------------
print("Logging in to Hugging Face...")
from huggingface_hub import login
login(token=HF_TOKEN)
print("Login successful.")

# ------------------------------------------------------------------
# 4. LOAD DATASET AND MODEL
# ------------------------------------------------------------------
# Base model to be fine-tuned
base_model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# Load the dataset from your Hugging Face Hub repository
dataset_id = f"{HF_USERNAME}/{HF_DATASET_NAME}"
print(f"Loading dataset from: {dataset_id}")
dataset = load_dataset(dataset_id, split="train")
print("Dataset loaded successfully.")
print(f"Dataset has {len(dataset)} examples.")

# Format the dataset
print("Applying formatting function to dataset...")
def format_instruction(example):
    # Convert the output to a string if it's not already
    output_json_string = json.dumps(example['output']) if isinstance(example['output'], dict) else example['output']
    
    # Format the prompt
    formatted_text = f"""<|system|>You are an expert resume parser that extracts information from CV text and returns it as JSON.</s>
<|user|>{example['text']}</s>
<|assistant|>{output_json_string}</s>"""
    
    return {"text": formatted_text}

# Format the dataset first
print("Formatting dataset...")
formatted_dataset = dataset.map(
    format_instruction,
    remove_columns=dataset.column_names  # Remove original columns
)
print("Dataset formatting completed.")

# --- Model and Tokenizer Configuration ---
print("Configuring model and tokenizer...")

# 4-bit quantization for memory efficiency
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16,
    bnb_4bit_use_double_quant=True,
)

# Load the base model
model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True,
)
model.config.use_cache = False
model.config.pretraining_tp = 1

# Load the tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right"

print("Model and tokenizer loaded successfully.")

# ------------------------------------------------------------------
# 5. CONFIGURE AND RUN TRAINING
# ------------------------------------------------------------------
print("Configuring training...")

# PEFT configuration
peft_config = LoraConfig(
    lora_alpha=16,
    lora_dropout=0.1,
    r=64,
    bias="none",
    task_type="CAUSAL_LM",
)

# Training arguments
training_arguments = TrainingArguments(
    output_dir="./results",
    num_train_epochs=3,
    per_device_train_batch_size=1,  # Reduced from 4 to 1
    gradient_accumulation_steps=8,  # Increased from 4 to 8
    optim="paged_adamw_32bit",
    save_steps=50,
    logging_steps=10,
    learning_rate=2e-4,
    weight_decay=0.001,
    fp16=False,
    bf16=True,
    max_grad_norm=0.3,
    max_steps=-1,
    warmup_ratio=0.03,
    group_by_length=True,
    lr_scheduler_type="constant",
    report_to=["none"],  # Disable wandb logging
    gradient_checkpointing=True  # Enable gradient checkpointing
)

# Add gradient checkpointing to the model
model.gradient_checkpointing_enable()

# Initialize the SFTTrainer
trainer = SFTTrainer(
    model=model,
    train_dataset=formatted_dataset,
    peft_config=peft_config,
    args=training_arguments
)

print("Starting fine-tuning...")
trainer.train()
print("Fine-tuning completed.")

# ------------------------------------------------------------------
# 6. SAVE AND UPLOAD THE FINAL MODEL
# ------------------------------------------------------------------
print("Saving the fine-tuned model...")

# Save the LoRA adapters
trainer.save_model("./results/final_adapters")

# --- Merge the base model with the LoRA adapters ---
print("Merging the base model with LoRA adapters...")
# Free up memory
del model
del trainer
torch.cuda.empty_cache()

# Reload the base model
base_model_reloaded = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    low_cpu_mem_usage=True,
    return_dict=True,
    torch_dtype=torch.float16,
    device_map="auto",
)

# Merge the adapters to create the full fine-tuned model
model = PeftModel.from_pretrained(base_model_reloaded, "./results/final_adapters")
model = model.merge_and_unload()

print("Model merged successfully.")

# --- Push to Hugging Face Hub ---
print(f"Uploading the final model to Hugging Face Hub as: {HF_USERNAME}/{NEW_MODEL_NAME}")

# This will create a new repository on your Hugging Face account
model.push_to_hub(f"{HF_USERNAME}/{NEW_MODEL_NAME}", use_temp_dir=False, private=True)
tokenizer.push_to_hub(f"{HF_USERNAME}/{NEW_MODEL_NAME}", use_temp_dir=False, private=True)

print("=====================================================================================")
print("✅ ✅ ✅ ALL DONE! ✅ ✅ ✅")
print(f"Your fine-tuned model has been successfully uploaded to: https://huggingface.co/{HF_USERNAME}/{NEW_MODEL_NAME}")
print("=====================================================================================") 