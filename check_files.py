import os

expected_count = 39
expected_files = [f"necro_chunk_{str(i).zfill(2)}.json" for i in range(1, expected_count + 1)]
found_files = [f for f in os.listdir(r"E:\munich_handbook_research\distilled") if f.startswith("necro_chunk_")]

missing_files = set(expected_files) - set(found_files)
small_files = [f for f in found_files if os.path.getsize(os.path.join(r"E:\munich_handbook_research\distilled", f)) < 5 * 1024]

print(f"Missing files: {missing_files}")
print(f"Small files: {small_files}")