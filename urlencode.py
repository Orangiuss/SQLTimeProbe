import urllib.parse
import argparse

def urlencode(string_to_encode, encode_param=True):
    """
    Encode une chaîne de caractères conformément aux spécifications URL.
    
    Args:
        string_to_encode (str): Chaîne de caractères à encoder.
        encode_param (bool): Indique si les caractères spéciaux doivent être encodés dans les paramètres de l'URL.
        
    Returns:
        str: Chaîne de caractères encodée.
    """
    if encode_param:
        return urllib.parse.quote(string_to_encode)
    else:
        return string_to_encode

# Analyse des arguments de la ligne de commande
parser = argparse.ArgumentParser(description="Encode une chaîne de caractères conformément aux spécifications URL.")
parser.add_argument("string_to_encode", help="Chaîne de caractères à encoder")
parser.add_argument("-d", "--disable-encode-param", action="store_false", help="Désactive l'encodage des caractères spéciaux dans les paramètres de l'URL")
args = parser.parse_args()

# Encode la chaîne de caractères
encoded_string = urlencode(args.string_to_encode, encode_param=args.disable_encode_param)

if not args.disable_encode_param:
    print("\033[91m[-] Encodage des paramètres désactivé\033[0m")
print("\033[91m[+] Chaine originale :\033[0m\n", args.string_to_encode)
print("\033[92m[+] Chaine encodée   :\033[0m\n", encoded_string)
