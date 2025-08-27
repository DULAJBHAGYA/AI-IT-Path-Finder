import os
import subprocess
import sys

# Check if we're in Google Colab
try:
    from google.colab import drive
    IN_COLAB = True
    print("Running in Google Colab")
except ImportError:
    IN_COLAB = False
    print("Running locally - skipping Google Drive mount")

# Setup for local environment
if IN_COLAB:
    # Google Colab setup
    if not os.path.exists('/content/drive'):
        print("Mounting Google Drive...")
        drive.mount('/content/drive')
        print("Google Drive mounted.")
    else:
        print("Google Drive already mounted.")

    DRIVE_OUTPUT_DIR = "/content/drive/MyDrive/llm-cv-parser-v2"
    FINAL_MODEL_DIR = f"{DRIVE_OUTPUT_DIR}/final_merged_model_v2"
    os.makedirs(FINAL_MODEL_DIR, exist_ok=True)
    print(f"Ensured model directory exists: {FINAL_MODEL_DIR}")
else:
    # Local setup
    print("Setting up for local environment...")
    FINAL_MODEL_DIR = "./model"  # Local model directory
    os.makedirs(FINAL_MODEL_DIR, exist_ok=True)
    print(f"Local model directory: {FINAL_MODEL_DIR}")

print("Installing dependencies...")

# Install required packages
try:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-U", 
                          "transformers", "datasets", "accelerate", "peft", 
                          "bitsandbytes", "trl", "fastapi", "uvicorn", 
                          "pyngrok", "reportlab", "textblob", "python-multipart", 
                          "simplejson"])
    print("Dependencies installed successfully.")
except subprocess.CalledProcessError as e:
    print(f"Error installing dependencies: {e}")
    print("Please install manually: pip install transformers datasets accelerate peft bitsandbytes trl fastapi uvicorn pyngrok reportlab textblob python-multipart simplejson")

# Handle API keys
if IN_COLAB:
    # Google Colab secrets
    try:
        from google.colab import userdata
        ngrok_auth_token = userdata.get('NGROK_AUTH_TOKEN')
        if not ngrok_auth_token:
            raise ValueError("NGROK_AUTH_TOKEN secret not found or empty.")
        os.environ["NGROK_AUTH_TOKEN"] = ngrok_auth_token
        print("Ngrok authtoken confirmed from Colab secrets.")
    except Exception as e:
        print(f"Error setting Ngrok authtoken: {e}")
        print("Please ensure NGROK_AUTH_TOKEN is set in Colab Secrets and enabled for this notebook.")
        raise SystemExit("Ngrok authentication failed. Exiting.")

    try:
        groq_api_key = userdata.get('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY secret not found or empty.")
        os.environ["GROQ_API_KEY"] = groq_api_key
        print("GROQ_API_KEY confirmed from Colab secrets.")
    except Exception as e:
        print(f"Error setting GROQ_API_KEY: {e}")
        print("Please ensure GROQ_API_KEY is set in Colab Secrets and enabled for this notebook.")
        raise SystemExit("Groq API key not available. Exiting.")
else:
    # Local environment variables
    ngrok_auth_token = os.environ.get('NGROK_AUTH_TOKEN')
    if not ngrok_auth_token:
        print("Warning: NGROK_AUTH_TOKEN not found in environment variables.")
        print("Please set it: export NGROK_AUTH_TOKEN='your_token_here'")
        # You can still continue without ngrok for local testing
    else:
        print("Ngrok authtoken found in environment variables.")

    groq_api_key = os.environ.get('GROQ_API_KEY')
    if not groq_api_key:
        print("Warning: GROQ_API_KEY not found in environment variables.")
        print("Please set it: export GROQ_API_KEY='your_key_here'")
    else:
        print("Groq API key found in environment variables.")

print("All initial setup complete.") 