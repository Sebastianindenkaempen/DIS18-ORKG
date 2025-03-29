import requests
import time
import pandas as pd
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
# import pytest

# https://www.ncbi.nlm.nih.gov/books/NBK25499/#chapter4.ESearch

def get_pmcids(search_term, no_of_results):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    params = {
        "db": "pmc",                                    # Source: https://www.ncbi.nlm.nih.gov/books/NBK25497/table/chapter2.T._entrez_unique_identifiers_ui/?report=objectonly
        "term": "open access[filter]+" + search_term,    # Source: https://pmc.ncbi.nlm.nih.gov/tools/openftlist/
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


def create_df_pmcids(search_terms, no_of_results):
    df = pd.DataFrame(columns=['PMCID', 'search_term'])

    for term in search_terms:
        pmcids = get_pmcids(term, no_of_results) 
        temp_df = pd.DataFrame({"PMCID": pmcids, "search_term": term}) 
        df = pd.concat([df, temp_df], ignore_index=True)
    df["PMCID"] = "PMC" + df["PMCID"].astype(str)
    return df


def check_if_pmcid_is_available(pmcid):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pmc", 
        "id": pmcid, 
        "retmode": "xml"
    }
    response = requests.get(search_url, params=params)
    time.sleep(0.5)
    
    if response.status_code == 200:
        try:
            xml_content = response.content.decode('utf-8').strip()
            
            if xml_content.startswith("<article"):
                return True
            
            root = ET.fromstring(xml_content)
            return root.find("article") is not None
        except ET.ParseError:
            return False
    return False


def get_full_xml(pmcid):
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
    params = {
        "db": "pmc", 
        "id": pmcid, 
        "retmode": "xml"
    }
    response = requests.get(search_url, params=params)
    time.sleep(0.5)

    if response.status_code == 200:
        return response.content
    else:
        return "error"
    

def extract_article_data(xml):
    soup = BeautifulSoup(xml, features="xml")  # Verwende den XML-Parser von lxml

    data = pd.DataFrame(columns=['pmid', 'title', 'abstract', 'full_text', 'authors'])

    pmid = soup.select_one('[pub-id-type="pmid"]').text.strip() if soup.select_one('[pub-id-type="pmid"]') else "N/A"
    title = soup.select_one("article-title").text.strip() if soup.select_one("article-title") else "N/A"
    abstract = soup.select_one("abstract").text.strip() if soup.select_one("abstract") else "N/A"

    full_text = "\n".join(
        sec.get_text(strip=True, separator=" ") for sec in soup.select("body sec")
    )
    authors = ", ".join(
        a.get_text(strip=True, separator=" ") for a in soup.select('[contrib-type="author"]')
    )

    temp_df = pd.DataFrame([{"pmid": pmid, "title": title, "abstract": abstract, "full_text": full_text, "authors": authors}])
    data = pd.concat([data, temp_df], ignore_index=True)

    return data


def pubmed_api_pull(search_terms, no_of_results):
    df = create_df_pmcids(search_terms=search_terms, no_of_results=no_of_results)
    df["has_result"] = df["PMCID"].apply(check_if_pmcid_is_available)
    df_filtered = df[df['has_result'] == True]
    final_df = pd.DataFrame(columns=['pmid', 'title', 'abstract', 'full_text', 'authors'])
    for index, row in df_filtered.iterrows():
        df_temp = extract_article_data(get_full_xml(row['PMCID']))
        final_df = pd.concat([final_df, df_temp], ignore_index=True)
    return final_df