import json
import os

def main():
    spirits = []
    for filename in os.listdir('.'):
        if filename.endswith('.json'):
            with open(filename, 'r') as f:
                data = json.load(f)
                if 'raw_quote' in data and 'chunk_id' in data:
                    spirits.append(data)
    
    code = """
class SpiritVector:
    def __init__(self):
        self.spirits = []
"""

    with open('src/spirit_vectors.py', 'a') as f:
        f.write(code)

if __name__ == "__main__":
    main()
