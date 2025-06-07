import streamlit as st
import pandas as pd

# Import the functions for the 'functions' folder within this repo. 
import importlib
import functions.pubmed_api
import functions.text_mining
importlib.reload(functions.pubmed_api)
importlib.reload(functions.text_mining)
from functions.pubmed_api import get_pmids, translate_pmid_to_pmcid, extract_article_data, get_full_xml
from functions.text_mining import extract_outbreak_info, summarize_outbreak, extract_location, extract_date

st.set_page_config(
    page_title="DIS18 - Project Dashboard", 
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/TH_Koeln_Logo.svg/768px-TH_Koeln_Logo.svg.png",
)


# creating containers to group elements
header = st.container()
user_input = st.container() 

# Variable to track session status
if "is_running" not in st.session_state:
    st.session_state.is_running = False

with header: 
    st.title("Welcome")
    st.write("""
            This interface aims to make it as easy as possible for you as a user users to automatically or semi-automatically extract data (location, time) related to outbreaks of specific diseases from articles listed in PubMed and upload them back to ORKG.
            """)

with user_input:
    st.markdown('### Enter user input')    
    input_search_terms = st.multiselect(label='Choose diseases for textmining', options=['avian influenza', 'ehec','q-fever'])
    input_no_of_results = st.number_input("Number of articles", min_value=1, step=1, disabled=st.session_state.is_running)
    mode = st.radio('Choose mode', options=['spaCy-Mode', 'LLM-Mode'], help='spaCy-mode will use Python package spaCy to search for outbreak information in the abstract. This is faster but might be not as precise. LLM-Mode will search for outbreak info in the abstract. This might be more precise but will take longer.')
        
    if st.button("Start Processing", disabled=st.session_state.is_running):

        with st.spinner("Processing... Please wait"):
            term_list = []
            pubmed_search_list = []
            

            for term in input_search_terms:
                number = input_no_of_results 

            # Translate the user given inputs into mesh terms to get more precise results from pubmed
                if term == 'avian influenza':
                    actual_search = '(avian influenza[MeSH Terms]) AND (disease outbreak[MeSH Terms])'
                elif term == 'ehec':
                    actual_search = '(ehec[MeSH Terms]) AND (disease outbreak[MeSH Terms])'
                elif term == 'q-fever':
                    actual_search = '(q fever[MeSH Terms]) AND (disease outbreak[MeSH Terms])'

            # The search term is appended to the list in for every article that will be pulled. 
            # That ensures that every document has the correct search term assigned
                while number > 0:
                    term_list.append(term)
                    pubmed_search_list.append(actual_search)
                    number = number - 1

            # get the terms unique so they only get queries once per term to pubmed
            pubmed_search_list_unique = list(dict.fromkeys(pubmed_search_list))
            
            # create a list for the pubmed ids and append every id retrieved to it. 
            pmids_list = []
            for term in pubmed_search_list_unique:
                list_pmid_search_term = get_pmids(term, input_no_of_results)
                for i in list_pmid_search_term:
                    pmids_list.append(i)

            # build the dataframe from the lists created before    
            df = pd.DataFrame(zip(term_list, pubmed_search_list, pmids_list), columns=['search_term', 'pubmed_search_term', 'pubmed_id'])
            
            # get the corresponding pmc id to every pubmed id. That ensures that we can retrieve the full texts later on
            df['pubmed_central_id'] = df['pubmed_id'].apply(translate_pmid_to_pmcid) 

            # create the dataframe for the full text that will be pulled from pubmed central. 
            df_full_texts = pd.DataFrame(columns=['pmid', 'doi', 'title', 'abstract', 'full_text', 'authors'])
            for pmcid in df['pubmed_central_id']:
                df_temp = extract_article_data(get_full_xml(pmcid))
                df_full_texts = pd.concat([df_full_texts, df_temp], ignore_index=True)

            # merge the full text to the dataframe which contains the metadata from before
            df = pd.merge(df, df_full_texts, how='left', left_on='pubmed_id', right_on='pmid', validate='one_to_one')
            df.drop(columns={'pmid'}, inplace=True)
            df.fillna(value='no text available', axis=0, inplace=True)

            # Do the textmining according to user selected mode. 
            if mode == 'spaCy-Mode':
                df = extract_outbreak_info(df, 'abstract')
            elif mode == 'LLM-Mode':
                df['summary_llm'] = df['abstract'].apply(summarize_outbreak)
                df['outbreak_locations'] = df['summary_llm'].apply(extract_location)
                df['outbreak_dates'] = df['summary_llm'].apply(extract_date)

            st.write("### Output:")
            st.write(df)
