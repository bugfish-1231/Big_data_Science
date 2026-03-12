# Import two modules from my_utility
from my_utility import password_checker
from my_utility import string_process

# Test the password checker (Module 1)
password = "Hello123"

print(f"Password Check ('{password}'): {password_checker.check_password(password)}")

# Test string processing (Module 2)
text = "level" 

print(f"Word count of 'Hello world': {string_process.word_count('Hello world')}")

print(f"Reverse of 'Python': {string_process.reverse_text('Python')}")

print(f"Is '{text}' a palindrome ?: {string_process.is_palindrome(text)}")