import requests
import time

# PubMed ESearch API URL
search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"

# Parameter für die Anfrage
params = {
    "db": "pubmed",            # PubMed-Datenbank
    "term": "Avian influenza",  # Suchbegriff (z. B. Vogelgrippe)
    "retmode": "json",         # Antwort im JSON-Format
    "retmax": "2"              # Nur ein Ergebnis zurück

}

# Anfrage senden und warten, um Rate Limit zu respektieren
response = requests.get(search_url, params=params)
time.sleep(0.5)  # Warten, um Rate Limit von max 3 Anfragen pro Sekunde zu respektieren

# Wenn die Antwort erfolgreich war (HTTP Status 200)
if response.status_code == 200:
    data = response.json()  # Antwort als JSON parsen
    pmid = data["esearchresult"]["idlist"][0:]
    print(f"Gefundene PMID: {pmid}")
else:
    print(f"Fehler bei der Anfrage: {response.status_code}")
