import requests
import time
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

def get_pmids(search_term: str, no_of_results: int) -> list[str]:
    
    """
    takes a string and integer as input, returns a list of pubmed IDs 
    """

    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pubmed",                                                 # Source: https://www.ncbi.nlm.nih.gov/books/NBK25497/table/chapter2.T._entrez_unique_identifiers_ui/?report=objectonly
        "term": "pubmed pmc open access[filter] AND " + search_term,    # Source: https://pmc.ncbi.nlm.nih.gov/tools/openftlist/
        "retmode": "json",                                              # Return format. Changed from XML
        "retmax": no_of_results,                                        # Number of results
        "sort": "relevance"
    }
    response = requests.get(search_url, params=params)
    time.sleep(0.34)                                     # Wait after request to respect API limit of 3 requests per second TODO: Add Source
    if response.status_code == 200:
        data = response.json()
        return data["esearchresult"]["idlist"]
    else:
        print(f"Fehler bei der Anfrage für '{search_term}': {response.status_code}")
        return []
    

def translate_pmid_to_pmcid(pmid: str) -> str | None:

    """
    Converts a PubMed ID (PMID) to a PubMed Central ID (PMCID) using the NCBI API.

    Returns the PMCID as a string or None if not found or request fails.
    """

    url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    params = {
        "db": "pubmed",
        "id": pmid,
        "retmode": "json"
    }
    response = requests.get(url, params=params)

    # Falls die Antwort leer oder fehlerhaft ist
    if response.status_code != 200:
        print(f"Fehler beim Abruf: {response.status_code}")
        return None
    
    try:
        data = response.json()
    except Exception as e:
        print("JSON konnte nicht geladen werden:", e)
        print("Antwortinhalt:", response.text)
        return None

    doc = data["result"].get(pmid)
    if not doc:
        print("Keine Daten für PMID gefunden.")
        return None

    article_ids = doc.get("articleids", [])
    for id_obj in article_ids:
        if id_obj["idtype"] == "pmc":
            return id_obj["value"]
    print("Kein PMCID gefunden.")
    return None

def get_full_xml(pmcid: str) -> bytes | str:

    """
    Fetches the full XML of an article from PMC by its PMCID.

    Returns the XML content as bytes if successful, otherwise "error".
    """

    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pmc", 
        "id": pmcid, 
        "retmode": "xml"
    }
    response = requests.get(search_url, params=params)
    time.sleep(0.34)

    if response.status_code == 200:
        return response.content
    else:
        return "error"
    

def extract_article_data(xml: str) -> pd.DataFrame:
    
    """
    extracts data from a pmc style article
    """

    soup = BeautifulSoup(xml, features="xml")

    data = pd.DataFrame(columns=['pmid', 'doi', 'title', 'abstract', 'full_text', 'authors'])

    pmid = soup.select_one('[pub-id-type="pmid"]')
    pmid = pmid.text.strip() if pmid else np.nan

    doi = soup.select_one('[pub-id-type="doi"]')
    doi = doi.text.strip() if doi else np.nan

    title = soup.select_one("article-title")
    title = title.text.strip() if title else np.nan

    abstract_elem = soup.select_one("abstract")
    abstract = abstract_elem.text.strip() if abstract_elem and abstract_elem.text.strip() else np.nan

    body_sections = soup.select("body sec")
    full_text = "\n".join(sec.get_text(strip=True, separator=" ") for sec in body_sections).strip()
    full_text = full_text if full_text else np.nan

    authors = ", ".join(
        a.get_text(strip=True, separator=" ") for a in soup.select('[contrib-type="author"]')
    )

    temp_df = pd.DataFrame([{
        "pmid": pmid,
        "doi": doi, 
        "title": title,
        "abstract": abstract,
        "full_text": full_text,
        "authors": authors
    }])

    data = pd.concat([data, temp_df], ignore_index=True)

    return data

