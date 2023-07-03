import hashlib
import base64
from django.conf import settings


def get_hashed_password(password):
    m = hashlib.sha256()
    m.update(settings.PASSWORD_SALT)
    m.update(password.encode('utf-8'))
    hash = m.digest()
    pwdHash = base64.b64encode(hash).decode('utf-8')
    return pwdHash

def get_subscriber_hashed(email):
    m = hashlib.sha256()
    m.update(settings.PASSWORD_SALT)
    m.update(email.encode('utf-8'))
    hash = m.digest()
    pwdHash = base64.b64encode(hash).decode('utf-8')
    #remove special characters form the hash
    special_characters=['@','#','$','*','&','?','/','+','-','_','=','^','<','>','|','~','!','%']
    normal_string=pwdHash
    for i in special_characters:
# Replace the special character with an empty string
        normal_string=normal_string.replace(i,"")
    return normal_string