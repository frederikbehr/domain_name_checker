
import socket
from django.core.validators import URLValidator
import requests
import time
import sys

domain_names = [
   
]

top_level_domains = [
   "com"
]

def prepare():
   # runs before it checks

   # example checking fruits
   with open('data/fruits.txt', 'r') as file:
    for line in file.readlines():
       domain_names.append(line.strip()) if line != "" else None

def run():
  prepare() # loads data

  # track the loading
  total = len(domain_names) * len(top_level_domains)  # number of domain name checks
  counter = 0

  # collect the results
  available = []
  not_available = []
  for j in range(len(top_level_domains)):
    for i in range(len(domain_names)):
      domain_name = (domain_names[i] + f".{top_level_domains[j]}").lower()
      in_use = check(f'https://www.{domain_name}/')
      available.append(domain_name) if in_use else not_available.append(domain_name)
      counter += 1
      print(f"\rChecking domain {counter}/{total}: {domain_name}", end='')
      sys.stdout.flush()
      time.sleep(0.5)

  # display the results
  print(f"AVAILABLE: {available}")
  print(f"NOT AVAILABLE: {not_available}")

def check(url):
    try:
        validate = URLValidator()
        validate(url)
    except:
        # not valid url
        print("Not valid domain name. Possibly written incorrectly.")
        return False
    
    # check if the url exists on the internet
    try:
        requests.get(url, timeout=3)
        return False
    except requests.ConnectionError:
        return True
    except socket.gaierror:
        print(f"Invalid domain: {url} (hostname could not be resolved)")
        return False  # invalid domain
    except requests.RequestException as e:
        print(f"An error occurred when trying to reach {url}: {e}")
        return False  # catch any other error as not available

run()