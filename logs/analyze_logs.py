import os

def analyze_logs():
    log_files = [f for f in os.listdir('E:\\munich_handbook_research\\logs') if f.endswith('.log')]
    
    result_table = {}
    
    for file in log_files:
        with open(os.path.join('E:\\munich_handbook_research\\logs', file), 'r') as f:
            for line_no, line in enumerate(f, 1):
                try:
                    data = eval(line)  # Simplified example: assume JSON format
                except (SyntaxError, NameError, ValueError, TypeError) as e:
                    result_table[file] = {str(chunk_id): 'failed' for chunk_id in range(1, line_no)}
                    break
    return result_table

analyze_logs()
