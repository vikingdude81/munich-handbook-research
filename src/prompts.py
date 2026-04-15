from langchain_core.prompts import PromptTemplate

# Prompt template for batch_distill_source JSON output
BATCH_DISTILL_PROMPT = PromptTemplate(
    input_variables=["schema"],
    template="Output ONLY a JSON object matching this schema, no other text:\n{schema}",
)
