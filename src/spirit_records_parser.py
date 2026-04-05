import json

spirit_records = []

# Assume distillation is running in a loop
while distillation_running:
    try:
        for file in valid_json_files:
            with open(file, 'r') as f:
                data = json.load(f)
                if all(key in data for key in required_fields):
                    spirit_records.append({
                        'spirit_name': data['spirit_name'],
                        'rank': data['rank'],
                        'function': data['function'],
                        'appearance': data['appearance'],
                        'legion_count': data['legion_count'],
                        'conjuration_method': data['conjuration_method'],
                        'experiment_ref': data['experiment_ref'],
                        'page_folio': data['page_folio'],
                        'raw_quote': data['raw_quote']
                    })
    except json.JSONDecodeError:
        continue
