from hashlib import blake2b

#J'encode en utf-8 le password le hash avec blake2b
#Je hash ce password autant qu'il y a de caractère dans le password de l'utilisateur

def hashlib_blake2b(password:str):
    '''
    La fonction permet de hacher un password
    haslib__blake2b(password:str)
    et retourne le nouveau password en string
    '''
    password = password.encode("utf-8")
    password_hash = 0
    password_hash = blake2b(password).hexdigest()
    for i in range(len(password)):
        password_hash = password_hash.encode("utf-8")
        password_hash = blake2b(password_hash).hexdigest()
    return password_hash