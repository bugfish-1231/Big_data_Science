def word_count(text):
    # Use `split()` to split the string into a list of individual words, then calculate the length.
    words = text.split()
    return len(words)

def reverse_text(text):
    # Use Python's slice syntax [::-1] to reverse the string.
    return text[::-1]

def is_palindrome(text):
    # Check if the string reads the same forwards and backwards (e.g., "level")
    reversed_text = reverse_text(text)
    return text.lower() == reversed_text.lower()