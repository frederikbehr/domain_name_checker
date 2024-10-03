# How to use

### Directory overview
```
/data
  Your .txt files with domain name tries goes here.
/output
  available_soon.txt # Expires in less than 4 weeks
  free_domains.txt # Free domains
main.py # Code is here
```

### Data
You can add .txt files to the data directory with max. 2 sub folder down containing .txt files.

Example:

```
/data
  /food
    fruits.txt
    vegetables.txt
```

### Settings
There are a few settings that can be set:

- predefined domain names to be tried.
- top level domains (fx. ".com" or ".org")
- amount of worker threads

These are specified in the top of main.py