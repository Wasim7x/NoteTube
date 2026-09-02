import re

def clean_text(text: str) -> str:
    """
    Basic text cleaning to remove obvious issues in transcripts
    like multiple spaces, newlines, etc.
    """
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Remove HTML tags if any slipped through
    text = re.sub(r'<[^>]+>', '', text)
    return text.strip()
