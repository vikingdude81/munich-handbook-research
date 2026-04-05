import pandas as pd

# Load the dataframes
df_0 = pd.read_csv('distillation_chunk_0.csv')
df_10 = pd.read_csv('distillation_chunk_10.csv')
df_20 = pd.read_csv('distillation_chunk_20.csv')
df_30 = pd.read_csv('distillation_chunk_30.csv')
df_38 = pd.read_csv('distillation_chunk_38.csv')

# Initialize counters
total_entries = 59 + 17 + 46 + 45 + 44  # Assuming total entries per chunk
spirit_name_count = 0
raw_quote_count = 0

# Validate schema and count valid entries
for df in [df_0, df_10, df_20, df_30, df_38]:
    for index, row in df.iterrows():
        if 'spirit_name' in row and pd.notna(row['spirit_name']):
            spirit_name_count += 1
        if 'raw_quote' in row and pd.notna(row['raw_quote']):
            raw_quote_count += 1

# Calculate coverage percentage
coverage = (spirit_name_count + raw_quote_count) / total_entries * 100

print(f"Schema Coverage: {coverage:.2f}%")
incomplete_entries = [index for index, row in df_0.iterrows() if not ('spirit_name' in row or 'raw_quote' in row)]
if incomplete_entries:
    print("Incomplete entries:")
    for entry in incomplete_entries:
        print(entry)
else:
    print("No incomplete entries found.")