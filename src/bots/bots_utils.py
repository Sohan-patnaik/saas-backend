import yaml
from rapidfuzz import process, fuzz

def load_bot(yml_content: str) -> dict:
    """
    Load YAML content and return a dict of question: answer.
    """
    data = yaml.safe_load(yml_content)
    conversations = data.get("conversations", [])
    qa_pairs = {q.strip(): a for q, a in conversations if q and a}
    return qa_pairs

def get_bot_response(user_input: str, qa_pairs: dict, threshold: int = 75) -> str:
    """
    Find the closest matching question to user_input and return its answer.
    Returns a default message if no match exceeds the threshold.
    """
    if not qa_pairs:
        return "I don't have any answers yet."

    questions = list(qa_pairs.keys())
    
    # Extract best match using token_sort_ratio for better accuracy
    match, score, _ = process.extractOne(
        user_input, 
        questions, 
        scorer=fuzz.token_sort_ratio  # handles reordering & minor differences
    )

    if score < threshold:
        return "I’m not sure about that."

    return qa_pairs[match]
