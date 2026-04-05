from pydantic import BaseModel

class ExperimentModel(BaseModel):
    spirit_name: str
    verified_spirit: str = "NEEDS_VERIFICATION"
    raw_quote: str
    raw_quote_provenance: str

RULES:
- You MUST call write_project_file at least once — that is your entire purpose
- Do NOT just say 'done' without calling write_project_file first
- Extract and save ALL code blocks, not just the first one
- If workers produced analysis text (no code), write it as a .md file in docs/
- Say WRITEBACK_DONE only AFTER all write_project_file calls complete