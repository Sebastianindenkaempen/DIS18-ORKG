import requests
import time

search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

search_terms = ["Avian influenza outbreak", "EHEC outbreak"]

def get_pmids(search_term, no_of_results):
    params = {
        "db": "pubmed",            
        "term": search_term, 
        "retmode": "json",                  # Datentyp der Antwort der API. Kann auch xml sein
        "retmax": no_of_results             # Anzahl der Ergebnisse
    }
    response = requests.get(search_url, params=params)
    time.sleep(0.5)                         # Wait after request to respect API limit of 3 requests per second

    if response.status_code == 200:
        data = response.json()
        return data["esearchresult"]["idlist"]
    else:
        print(f"Fehler bei der Anfrage für '{search_term}': {response.status_code}")
        return []

get_pmids(search_terms[0], 3)