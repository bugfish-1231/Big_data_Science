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
    # 檢查長度是否達到 8 個字元 
    return len(password) >= 8

def check_password(password):
    # 綜合呼叫以上三個函數 
    cond1 = has_uppercase(password)
    cond2 = has_number(password)
    cond3 = is_long_enough(password)
    
    # 必須同時滿足所有條件
    if cond1 and cond2 and cond3:
        return "password is valid"
    else:
        return "password is not valid" 