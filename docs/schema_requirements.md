# Schema Requirements

## Project Structure

```yaml
project:
  name: ProjectName
  description: Description of the project

schema_requirements:
  spirit_vectors.py:
    provenance: string
    source_chunk: integer
    raw_quote: string

experiment_structure:
  experiments:
    - id: experiment1
      data_sources:
        - id: ds1
          type: text_file
          path: /path/to/file.txt
        - id: ds2
          type: database_query
          query: SELECT * FROM table WHERE condition
      results_storage:
        - id: rs1
          type: csv_file
          path: /results.csv

  experiments:
    - id: experiment2
      data_sources:
        - id: ds3
          type: api_call
          endpoint: https://api.example.com/data
      results_storage:
        - id: rs2
          type: database_table
          table_name: result_table
```

> Note: This is a simplified example and actual project structure may vary.