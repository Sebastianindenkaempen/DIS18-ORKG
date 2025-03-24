import requests
import time
import pandas as pd
import xml.etree.ElementTree as ET


def get_full_text(pmcid):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pmc", 
        "id": "open access[filter]+" + pmcid, 
        "retmode": "xml"
    }
    response = requests.get(search_url, params=params)
    time.sleep(0.5)

    return response.url

# # PMCID = "PMC8994043"
PMCID = "PMC11915822" 

print(get_full_text(PMCID))

# Available: 11900536
# Not Available: 11915822
# Warum ist das so??