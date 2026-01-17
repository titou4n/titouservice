from socket import *

#Je récupère l'adresse ip

def ipv4_address():
    return gethostbyname(gethostname())