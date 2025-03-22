import requests
import time
import pandas as pd
# import json
import xml.etree.ElementTree as ET


search_terms = ["Avian influenza outbreak", "EHEC outbreak"]

def get_pmcids(search_term, no_of_results):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pmc",            
        "term": "open access[filter]" + search_term,    # Source: https://pmc.ncbi.nlm.nih.gov/tools/openftlist/
        "retmode": "json",                               # Return format. Changed to XML
        "retmax": no_of_results,                        # Number of results
    }
    response = requests.get(search_url, params=params)
    time.sleep(0.5)                                     # Wait after request to respect API limit of 3 requests per second TODO: Add Source
    
    if response.status_code == 200:
        data = response.json()
        return data["esearchresult"]["idlist"]
    else:
        print(f"Fehler bei der Anfrage für '{search_term}': {response.status_code}")
        return []


df = pd.DataFrame(columns=['PMCID', 'search_term'])

for term in search_terms:
    pmcids = get_pmcids(term, 3) 
    temp_df = pd.DataFrame({"PMCID": pmcids, "search_term": term}) 
    df = pd.concat([df, temp_df], ignore_index=True)

print(df)
