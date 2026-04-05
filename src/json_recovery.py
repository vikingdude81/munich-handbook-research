import os
import re
import json
import logging

# Set up logging
log_dir = "E:\\munich_handbook_research\\src\\distillations_recovered\\"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(filename=log_dir + "recovery_logs.txt", level=logging.INFO)

def extract_json_from_chunk(chunk_content):
    try:
        return json.loads(chunk_content)
    except json.JSONDecodeError:
        # Fallback to regex
        match = re.search(r'\{.*?\}', chunk_content, re.DOTALL)
        if match:
            recovered = match.group(0)
            return json.loads(recovered)
        else:
            logging.warning("No valid JSON found in chunk")
            return None

def process_chunk(file_path):
    with open(file_path, 'r') as f:
        content = f.read()
    
    json_data = extract_json_from_chunk(content)
    if json_data:
        logging.info(f"Recovered JSON from {file_path}")
        with open(os.path.join(log_dir, f"{os.path.basename(file_path).split('.')[0]}_recovered.json"), 'w') as out:
            json.dump(json_data, out, indent=2)
    else:
        logging.warning(f"No valid JSON found in {file_path}")

# Process all chunk.json files
for filename in os.listdir("E:\\munich_handbook_research\\src\\distillations"):
    if filename.endswith(".json"):
        process_chunk(os.path.join("E:\\munich_handbook_research\\src\\distillations", filename))