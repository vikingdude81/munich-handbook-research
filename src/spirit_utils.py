def parse_spirit_records(jsons):
    unified_list = []
    for json in jsons:
        record = {
            'spirit_name': json.get('spirit_name', None),
            'rank': json.get('rank', 'unknown'),
            'function': json.get('function', ''),
            'appearance': json.get('appearance', ''),
            'legion_count': json.get('legion_count', None),
            'conjuration_method': json.get('conjuration_method', ''),
            'experiment_refs': json.get('experiment_refs', []),
            'page_folio': json.get('page_folio', ''),
            'raw_quote': json.get('raw_quote', '')
        }
        
        if not record['spirit_name']:
            record['status'] = 'NEEDS_VERIFICATION'
        elif not record['raw_quote']:
            record['status'] = 'NEEDS_VERIFICATION'
        
        unified_list.append(record)
    return unified_list