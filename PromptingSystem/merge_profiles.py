import json

# Load the first file (synthetic QA/BA profiles)
with open('synthetic_qa_ba_profiles.json', 'r', encoding='utf-8') as f1:
    data1 = json.load(f1)

# Load the second file (previously merged profiles)
with open('merged_profiles.json', 'r', encoding='utf-8') as f2:
    data2 = json.load(f2)

# Merge the lists
merged_data = data1 + data2

# Save to a new file (do not overwrite existing files)
with open('merged_profiles_all.json', 'w', encoding='utf-8') as fout:
    json.dump(merged_data, fout, indent=2)

print(f"Merged {len(data1)} + {len(data2)} profiles into merged_profiles_all.json") 