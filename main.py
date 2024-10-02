import socket
from django.core.validators import URLValidator
import requests
import time
import sys
import re

domain_names = []
top_level_domains = ["com"]

def prepare():
    #with open('data/fruits.txt', 'r') as file:
    #   for line in file.readlines():
    #      domain_names.append(line.strip().replace(" ", "")) if line != "" else None
    with open('data/1000_most_used_words.txt', 'r') as file:
        for line in file.readlines():
            line = re.sub(r'[^a-zA-Z0-9 ]', '', line)
            domain_names.append(line.strip().replace(" ", "")) if line != "" else None

def run():
    prepare()
    total = len(domain_names) * len(top_level_domains)
    counter = 0
    available = []
    not_available = []
    
    for j in range(len(top_level_domains)):
        for i in range(len(domain_names)):
            domain_name = (domain_names[i] + f".{top_level_domains[j]}").lower()
            in_use = check(f'https://www.{domain_name}/')

            if in_use:
                available.append(domain_name)
            else:
                not_available.append(domain_name)

            counter += 1
            status_message = f"Checking domain {counter}/{total}: {domain_name}"
            print(status_message.ljust(70), end='\r')
            sys.stdout.flush()
            time.sleep(0.5)

    print("\n" + "=" * 80)
    print(f"AVAILABLE: {available}")
    print(f"NOT AVAILABLE: {not_available}")
    with open('output/domain_check_results.txt', 'w') as result_file:
        result_file.write("AVAILABLE:\n")
        for domain in available:
            result_file.write(f"{domain}\n")
        result_file.write("\n\nNOT AVAILABLE:\n")
        for domain in not_available:
            result_file.write(f"{domain}\n")

def check(url):
    try:
        validate = URLValidator()
        validate(url)
    except:
        print("\nNot valid domain name. Possibly written incorrectly.\n")
        return False

    try:
        requests.get(url, timeout=5)
        return False
    except requests.ConnectionError:
        return True
    except socket.gaierror:
        print(f"\nInvalid domain: {url} (hostname could not be resolved)\n")
        return False
    except requests.RequestException as e:
        print(f"\nAn error occurred when trying to reach {url}: {e}\n")
        return False

run()
