import streamlit as st
import pandas as pd
import numpy as np

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

# Variable to track session status TODO: fix
# if "is_running" not in st.session_state:
#     st.session_state.is_running = False

with header: 
    st.title("Welcome")


with user_input:    
    input_search_terms = st.multiselect(label='Choose diseases for Text Mining', options=['avian influenza', 'ehec','q-fever'])
    input_no_of_results = st.number_input("Number of articles", min_value=1, step=1, disabled=st.session_state.is_running)
    mode = st.radio('Choose mode', options=['spaCy-Mode (abstract-only)', 'spaCy-Mode (abstract + fulltext)', 'LLM-Mode'], help='spaCy offers two modes: abstract-only and abstract + fulltext. Abstract only is faster and more precise but only analyses limited text input. LLM-Mode will search for outbreak info in the abstract. This might be more precise but will take longer.')
    output_format = st.radio('Choose output', options=['ORKG-Upload', 'Raw'], help='ORKG-Upload formats the data so it can be downloaded and uploaded per CSV to ORGK. Raw-format is ideal for bugfixing and understanding how the process works.')    

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

                while number > 0:
                    term_list.append(term)
                    pubmed_search_list.append(actual_search)
                    number = number - 1

            pubmed_search_list_unique = list(dict.fromkeys(pubmed_search_list))
            pmids_list = []

            for term in pubmed_search_list_unique:
                list_pmid_search_term = get_pmids(term, input_no_of_results)
                for i in list_pmid_search_term:
                    pmids_list.append(i)
                
            df = pd.DataFrame(zip(term_list, pubmed_search_list, pmids_list), columns=['search_term', 'pubmed_search_term', 'pubmed_id'])
            df['pubmed_central_id'] = df['pubmed_id'].apply(translate_pmid_to_pmcid) 


            df_full_texts = pd.DataFrame(columns=['pmid', 'doi', 'title', 'abstract', 'full_text', 'authors'])
            for pmcid in df['pubmed_central_id']:
                df_temp = extract_article_data(get_full_xml(pmcid))
                df_full_texts = pd.concat([df_full_texts, df_temp], ignore_index=True)

            df = pd.merge(
                df, 
                df_full_texts, 
                how='left', 
                left_on='pubmed_id', 
                right_on='pmid' 
                # , validate='one_to_one'
                )
            df.drop(columns={'pmid'}, inplace=True)
            # df.dropna(subset=['abstract', 'full_text'], inplace=True, thresh=2, ignore_index=True)
            df.fillna(value='no text available', axis=0, inplace=True)

            if mode == 'spaCy-Mode (abstract-only)':
                df = extract_outbreak_info(df, 'abstract')
            elif mode == 'spaCy-Mode (abstract + fulltext)':
                df['combined_text'] = df['abstract'] + ' ' + df['full_text']
                df = extract_outbreak_info(df, 'combined_text')
                df = df.drop(columns={'combined_text'})
            elif mode == 'LLM-Mode':
                df['summary_llm'] = df['abstract'].apply(summarize_outbreak)
                df['outbreak_locations'] = df['summary_llm'].apply(extract_location)
                df['outbreak_dates'] = df['summary_llm'].apply(extract_date)
                # df = df.drop(columns={'summary_llm'})


            st.write("### Output:")

            if output_format == 'ORKG-Upload':

                for column in ['authors', 'publication_month', 'publication_year', 'published_in', 'url', 'research_problem']:
                    df[column] = np.nan

                df['research_field'] = 'R677193'
                df['extraction_method'] = 'AUTOMATIC'

                df = df[['title', 'authors', 'publication_month', 'publication_year', 'published_in', 'research_field', 'doi', 'url', 'research_problem', 'extraction_method', 'outbreak_locations', 'outbreak_dates']]
                df = df.rename(columns={'outbreak_locations':'location', 'outbreak_dates':'Dates'}) 
            else: 
                df = df

            st.dataframe(df, hide_index=True)

