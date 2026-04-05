import json
from requests import Session
from time import sleep

def batch_distill_source(pipeline, sources):
    results = []
    for source in sources:
        try:
            response = pipeline(source)
            parsed_response = parse_json(response.text)
            results.append(parsed_response)
        except Exception as e:
            print(f"Failed to process {source}: {e}")
            # Retry with exponential backoff
            sleep(2 ** len(results))
            response = pipeline(source)
            parsed_response = parse_json(response.text)
            results.append(parsed_response)
    return results

def parse_json(json_str):
    json_data = json.loads(json_str.strip())
    return json_data