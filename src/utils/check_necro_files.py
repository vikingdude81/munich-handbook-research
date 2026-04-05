import os

def check_necro_files(folder_path):
    necro_files = [f for f in os.listdir(folder_path) if f.startswith("necro") and f.endswith(".chunk")]
    
    print(f"Found {len(necro_files)} 'necro' chunk files:")
    for file in necro_files:
        file_path = os.path.join(folder_path, file)
        try:
            with open(file_path, 'rb') as f:
                data = f.read(1024)  # Read first 1024 bytes to check if file is empty
                size = os.path.getsize(file_path)
                encoding = "UTF-8"  # Default text encoding for .chunk files
            print(f"Filenames: {file}, Size: {size} bytes, Encoding: {encoding}")
        except FileNotFoundError:
            print(f"Filenames: {file}, Status: Missing")
        except PermissionError:
            print(f"Filenames: {file}, Status: Permission Denied")
        except Exception as e:
            print(f"Filenames: {file}, Error: {e}")

check_necro_files("E:\\munich_handbook_research\\src\\necro_chunks")
