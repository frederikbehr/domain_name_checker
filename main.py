import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
import whois
import time
import unicodedata
from datetime import datetime, timedelta


domain_names = []
top_level_domains = ["com"]
workers = 30 # how many threads will run. More is faster. 50 was problematic.

taken_but_free_soon = []

def run():
    print("Application started...")
    prepare_data = input("Do you want to pull the data folder (Y/n): ")
    check_checked_domains_using_api = input("Do you want to check the domains (Y/n): ")
    if prepare_data.lower() != "n":
      prepare()
      print("Data gotten")
    if check_checked_domains_using_api.lower() != "n":
      print("Checking availability...")
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
                line = remove_diacritics(line)
                cleaned_line = line.strip().replace(" ", "")
                #if len(domain_names) > 100:
                 # break
                if cleaned_line:
                  for top_level_domain in top_level_domains:
                    domain_names.append(f"{cleaned_line}.{top_level_domain}")
                    if cleaned_line.endswith("s") != True and cleaned_line.endswith("y"):
                      if cleaned_line.endswith("y") == True and cleaned_line.endswith("ey") != True and cleaned_line.endswith("ay") != True and cleaned_line.endswith("oy") != True:
                        domain_names.append(f"{cleaned_line[:-1]}ies.{top_level_domain}")
                      elif cleaned_line.endswith("ch") == True:
                        domain_names.append(f"{cleaned_line}es.{top_level_domain}")
                      else:
                        domain_names.append(f"{cleaned_line}s.{top_level_domain}")

def remove_diacritics(line):
  # Normalize the string to remove diacritics
  normalized_line = unicodedata.normalize('NFD', line)
  # Remove diacritic marks
  line_without_diacritics = ''.join(
    c for c in normalized_line if unicodedata.category(c) != 'Mn'
  )
  # Use regex to remove non-alphanumeric characters (except spaces)
  return re.sub(r'[^a-zA-Z0-9 ]', '', line_without_diacritics)

def check_domain_name_status():
  def is_available(domain):
    try:
      w = whois.whois(domain)

      if w.expiration_date:
        expiration_date = w.expiration_date
        # Handle case where expiration_date might be a list
        if isinstance(expiration_date, list):
          #print(f"{expiration_date} - {domain}")
          expiration_date = expiration_date[0] + timedelta(hours=1)
            
        # Calculate 4 weeks from today
        four_weeks_from_now = datetime.now() + timedelta(weeks=4)
            
        if expiration_date < four_weeks_from_now:
          taken_but_free_soon.append(f"{domain} - {expiration_date}")

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

  # Use ThreadPoolExecutor to check domain availability
  with ThreadPoolExecutor(max_workers=workers) as executor:
    futures = {executor.submit(is_available, domain): domain for domain in domain_names if domain}

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

    for domain in sorted(good_domains, key=len):
      result_file.write(f"{domain}\n") if domain != ".com" else None

  def parse_date(domain_info):
    date_str = domain_info.split(" - ")[1].strip()
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S") 
  
  with open('output/available_soon.txt', 'w') as result_file:
    result_file.write("EXPIRES SOON:\n")
    for domain in sorted(taken_but_free_soon, key=parse_date):
      result_file.write(f"{domain}\n") if domain != ".com" else None


run()
