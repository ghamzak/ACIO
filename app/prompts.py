# Prompt template for zero-shot contract classification using LLMs
# Usage: Insert contract types and definitions, then append contract text and output instructions as needed.

ZERO_SHOT_CONTRACT_CLASSIFICATION_PROMPT = '''
You are a contract classification expert.
Given the following contract text, classify it as one of the contract types listed below.
For each type, a definition is provided.
Choose the single most appropriate type based on the contract’s content and the definitions.
Do not guess if the contract is incomplete or ambiguous; instead, return "Unknown".

Contract Types and Definitions:
{contract_types_and_definitions}

Instructions:
- Carefully read the contract text.
- Compare the contract’s content to the definitions provided.
- Select the best matching contract type from the list.
- Return only the contract type name as your answer.

Contract Text:
{contract_text}
'''
