from langchain_core.prompts import PromptTemplate

# Improved prompt template for batch_distill_source JSON output
BATCH_DISTILL_PROMPT = PromptTemplate(
    input_variables=["schema"],
    template="Output ONLY a JSON object matching this schema, no other text: \n{{ schema }}\n\n{schema}",
    output_variable="batch_data"
)
