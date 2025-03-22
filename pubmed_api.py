import requests
import time
import pandas as pd

search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

search_terms = ["Avian influenza outbreak", "EHEC outbreak"]

def get_pmids(search_term, no_of_results):
    params = {
        "db": "pubmed",            
        "term": search_term, 
        "retmode": "json",                  # Return format. Could be XML as well
        "retmax": no_of_results             # Number of results
    }
    response = requests.get(search_url, params=params)
    time.sleep(0.5)                         # Wait after request to respect API limit of 3 requests per second

    if response.status_code == 200:
        data = response.json()
        return data["esearchresult"]["idlist"]
    else:
        print(f"Fehler bei der Anfrage für '{search_term}': {response.status_code}")
        return []

df = pd.DataFrame(columns=['PMID', 'search_term'])

for term in search_terms:
    pmids = get_pmids(term, 3) 
    temp_df = pd.DataFrame({"PMID": pmids, "search_term": term}) 
    df = pd.concat([df, temp_df], ignore_index=True)

print(df)