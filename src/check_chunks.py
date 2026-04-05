import os

def check_chunks():
    json_files = [f for f in os.listdir("E:\\munich_handbook_research\\distilled\\necro") if f.endswith('.json')]
    total_chunks = len(json_files)
    
    chunk_ids_complete = set()
    missing_chunks = []

    for file in json_files:
        with open(os.path.join("E:\\munich_handbook_research\\distilled\\necro", file), 'r') as f:
            data = f.read().strip()
            if "chunk_id" in data:
                chunk_ids_complete.add(data.split("\n")[0].split(": ")[1])
            else:
                missing_chunks.append(file)
    
    print(f"Total JSON files: {total_chunks}")
    print("Chunks complete:")
    for id in sorted(chunk_ids_complete):
        print(id)

check_chunks()
