
# def pubmed_api_pull(term_input, result_no_input):
#     df = create_df_pmcids(search_terms=term_input, no_of_results=result_no_input)
#     df["has_result"] = df["PMCID"].apply(check_if_pmcid_is_available)
#     df_filtered = df[df['has_result'] == True]
#     final_df = pd.DataFrame(columns=['pmid', 'title', 'abstract', 'full_text', 'authors'])
#     for index, row in df_filtered.iterrows():
#         df_temp = extract_article_data(get_full_xml(row['PMCID']))
#         final_df = pd.concat([final_df, df_temp], ignore_index=True)
#     return final_df

# def extract_article_data(xml):
#     soup = BeautifulSoup(xml, features="xml")  # Verwende den XML-Parser von lxml

#     data = pd.DataFrame(columns=['pmid', 'title', 'abstract', 'full_text', 'authors'])

#     pmid = soup.select_one('[pub-id-type="pmid"]').text.strip() if soup.select_one('[pub-id-type="pmid"]') else "N/A"
#     title = soup.select_one("article-title").text.strip() if soup.select_one("article-title") else "N/A"
#     abstract = soup.select_one("abstract").text.strip() if soup.select_one("abstract") else "N/A"

#     full_text = "\n".join(
#         sec.get_text(strip=True, separator=" ") for sec in soup.select("body sec")
#     )
#     authors = ", ".join(
#         a.get_text(strip=True, separator=" ") for a in soup.select('[contrib-type="author"]')
#     )

#     temp_df = pd.DataFrame([{"pmid": pmid, "title": title, "abstract": abstract, "full_text": full_text, "authors": authors}])
#     data = pd.concat([data, temp_df], ignore_index=True)

#     return data

# Not needed anymore 
# def create_df_pmcids(search_terms, no_of_results):
    # """
    # takes a list input, returns a dataframe
    # """
#     df = pd.DataFrame(columns=['PMCID', 'search_term'])

#     for term in search_terms:
#         pmcids = get_pmcids(term, no_of_results) 
#         temp_df = pd.DataFrame({"PMCID": pmcids, "search_term": term}) 
#         df = pd.concat([df, temp_df], ignore_index=True)
#     df["PMCID"] = "PMC" + df["PMCID"].astype(str)
#     return df

# def get_call_link(pmcid):
#     search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
#     params = {
#         "db": "pmc", 
#         "id": "open access[filter]+" + pmcid, 
#         "retmode": "xml"
#     }
#     response = requests.get(search_url, params=params)
#     time.sleep(0.34)

#     return response.url


# def check_if_pmcid_is_available(pmcid):
#     search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
#     params = {
#         "db": "pmc", 
#         "id": pmcid, 
#         "retmode": "xml"
#     }
#     response = requests.get(search_url, params=params)
#     time.sleep(0.34)
    
#     if response.status_code == 200:
#         try:
#             xml_content = response.content.decode('utf-8').strip()
            
#             if xml_content.startswith("<article"):
#                 return True
            
#             root = ET.fromstring(xml_content)
#             return root.find("article") is not None
#         except ET.ParseError:
#             return False
#     return False

# # Lade das spaCy-Modell nur einmal
# nlp = spacy.load("en_core_web_sm")
# # nlp = spacy.load("en_core_web_md")
# # nlp = spacy.load("en_core_web_trf")

# # Initialisiere PhraseMatcher mit relevanten Phrasen
# matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
# phrases = [
#     "outbreak", "epidemic", "cases reported in", "first detected",
#     "incidence in", "occurred in", "emerged in", "infection reported"
# ]
# patterns = [nlp.make_doc(p) for p in phrases]
# matcher.add("OUTBREAK", patterns)

# # Die Hauptfunktion
# def extract_outbreak_info(df, text_column="full-text"):
#     outbreak_locations = []
#     outbreak_dates = []

#     for text in df[text_column]:
#         doc = nlp(text)
#         locations = set()
#         dates = set()

#         matches = matcher(doc)
#         for match_id, start, end in matches:
#             sent = doc[start:end].sent
#             for ent in sent.ents:
#                 if ent.label_ == "GPE":
#                     locations.add(ent.text)
#                 elif ent.label_ == "DATE":
#                     dates.add(ent.text)

#         # Füge erkannte Infos zum Ergebnis hinzu (leere Strings, falls nichts gefunden)
#         outbreak_locations.append(", ".join(locations) if locations else "")
#         outbreak_dates.append(", ".join(dates) if dates else "")

#     # Neue Spalten zum DataFrame hinzufügen
#     df["outbreak_locations"] = outbreak_locations
#     df["outbreak_dates"] = outbreak_dates
#     return df

# def check_if_text_has_outbreak(text):
#     response = requests.post(
#         "http://localhost:11434/api/generate",
#         json={
#             "model": "phi4-mini",
#             "prompt": 
#         f"""
#         Analysiere den folgenden Text sehr genau:

#         {text}

#         Frage: Beschreibt der Text einen Krankheitsausbruch, bei dem sowohl ein konkreter Ort (z.B. Ländername, Stadt) als auch ein konkreter Zeitpunkt (z.B. Datum, Monat/Jahr) genannt werden?

#         Antworte ausschließlich mit:
#         True  --> falls sowohl Ort als auch konkreter Zeitpunkt des Ausbruchs im Text genannt werden
#         False --> falls Ort oder konkreter Zeitpunkt fehlen oder kein Ausbruch beschrieben wird

#         Antwort:""",
#             "stream": False
#         }

#         )
#     return response.json()["response"]

# def regex_check_if_text_has_outbreak(text):
#     pattern = r"\b(outbreak\b|epidemic\b|cases (have been|were|are)? reported in|first (was )?detected|incidence in|occurred in|emerged in|infection (has been|was)? reported)\b"
#     if re.search(pattern, text, flags=re.IGNORECASE):
#         return True
#     else:
#         return False

# def parse_outbreak(value):
#     if isinstance(value, str):
#         val = value.lower()
#         if 'true' in val:
#             return True
#         elif 'false' in val:
#             return False
#     return np.nan