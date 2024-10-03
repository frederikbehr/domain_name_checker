import socket
from django.core.validators import URLValidator
import requests
import sys
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import whois
import time

domain_names = []
top_level_domains = ["com"]
workers = 20 # how many threads will run. More is faster. 50 was problematic.

def run():
    print("Application started...")
    prepare_data = input("Do you want to prepare data first (Y/n): ")
    check_checked_domains_using_api = input("Do you want to safe check the domains (Y/n): ")
    if prepare_data.lower() != "n":
      prepare()
      check_domains()
      print("Quick check finished...")
      time.sleep(10)
    if check_checked_domains_using_api.lower() != "n":
      print("Checking these an extra time with whois...")
      check_domain_name_status()
    if (check_checked_domains_using_api.lower() == "n" and prepare_data.lower() == "n"):
       print("You said no to do all the tasks. Therefore, nothing was done.")
    print("Application finished...")

def prepare():
    data_directory = './data/'
    for root, dirs, files in os.walk(data_directory):
      for file in files:
        if file.endswith('.txt'):  # Check for text files
            file_path = os.path.join(root, file)
            with open(file_path, 'r') as f:
              for line in f:
                line = re.sub(r'[^a-zA-Z0-9 ]', '', line)
                cleaned_line = line.strip().replace(" ", "")
                if cleaned_line:  # Only append non-empty lines
                  domain_names.append(cleaned_line)

def check_domain_name_status():
  def is_available(domain):
    try:
      w = whois.whois(domain)
      if w.status is None and w.creation_date is None:  # Adjusted for thoroughness
        print(f"Domain available: {domain}")
        return True
      else:
        #print(f"Domain NOT available: {domain}")
        return False
    except Exception:
      print(f"Domain possibly available: {domain}")
      return True

  good_domains = []

  # Read domain names from the file
  with open('output/domain_check_results.txt', 'r') as file:
    domains_to_check = [re.sub(r'\s+', '', line.strip()) for line in file.readlines()]

  # Use ThreadPoolExecutor to check domain availability
  with ThreadPoolExecutor(max_workers=20) as executor:
    futures = {executor.submit(is_available, domain): domain for domain in domains_to_check if domain}

    for future in as_completed(futures):
      domain = futures[future]
      try:
        if future.result():  # If the domain is available
          good_domains.append(domain)
      except Exception as e:
        print(f"Error checking domain {domain}: {e}")

  # Write the available domains to the output file
  with open('output/free_domains.txt', 'w') as result_file:
    result_file.write("FREE DOMAINS:\n")
    for domain in good_domains:
      result_file.write(f"{domain}\n") if domain != ".com" else None

def check_domains():
    total = len(domain_names) * len(top_level_domains)
    counter = 0
    available = []
    not_available = []
    # remove domains that are for sure not available
    with ThreadPoolExecutor(max_workers=20) as executor:  # Adjust the number of threads as needed
      futures = {
        executor.submit(check, f'https://www.{domain_name}.{top_level_domain}'): f"{domain_name}.{top_level_domain}"
        for domain_name in domain_names 
        for top_level_domain in top_level_domains
      }

      for future in as_completed(futures):
        domain_name = futures[future]
        try:
            in_use = future.result()
            if in_use:
                available.append(domain_name)
            else:
                not_available.append(domain_name)
        except Exception as e:
            print(f"Error checking domain {domain_name}: {e}")

        counter += 1
        status_message = f"Checking domain {counter}/{total}: {domain_name}"
        print(status_message.ljust(70), end='\r')
        sys.stdout.flush()
    with open('output/domain_check_results.txt', 'w') as result_file:
        result_file.write("POSSIBLY AVAILABLE:\n")
        for domain in available:
            result_file.write(f"{domain}\n")


def check(url):
    try:
        validate = URLValidator()
        validate(url)
    except Exception:
        print("\nNot valid domain name. Possibly written incorrectly.\n")
        return False

    try:
        # Set connection and read timeouts
        requests.get(url, timeout=(3, 5))
        return False  # Domain is in use if we get a response
    except requests.ConnectionError:
        return True  # Domain is available
    except socket.gaierror:
        print(f"\nInvalid domain: {url} (hostname could not be resolved)\n")
        return False
    except requests.RequestException as e:
        print(f"\nAn error occurred when trying to reach {url}: {e}\n")
        return False
    except requests.Timeout:
        print(f"\nRequest timed out for domain: {url}\n")
        return False

run()
