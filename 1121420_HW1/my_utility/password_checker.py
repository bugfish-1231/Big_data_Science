def has_uppercase(password):
    # Check if any character in the string is uppercase.
    for char in password:
        if char.isupper():
            return True
    return False

def has_number(password):
    # Check if any character in the string is a number.
    for char in password:
        if char.isdigit():
            return True
    return False

def is_long_enough(password):
    # Check if the length reaches 8 characters. 
    return len(password) >= 8

def check_password(password):
    # Combine the results of the above three functions
    cond1 = has_uppercase(password)
    cond2 = has_number(password)
    cond3 = is_long_enough(password)
    
    # All conditions must be met
    if cond1 and cond2 and cond3:
        return "password is valid"
    else:
        return "password is not valid" 