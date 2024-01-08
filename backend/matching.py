from re import match, fullmatch

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
 
 
def check_email(email: str) -> [bool]:
    if(fullmatch(regex, email)):
        print("Valid Email")
    else:
        print("Invalid Email")

def check_password_strength(password: str) -> [bool]:
    return match(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)\w{8,}$", password) is not None