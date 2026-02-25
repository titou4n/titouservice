from werkzeug.security import generate_password_hash
from hashlib import blake2b

class HashManager():
    def __init__(self):
        pass

    def generate_password_hash(self, password:str):
        #return generate_password_hash(str(password))
        return self.hashlib_blake2b(str(password))

    def hashlib_blake2b(self, password:str):
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