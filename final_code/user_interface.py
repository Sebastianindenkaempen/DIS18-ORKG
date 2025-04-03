# import sys
# import os
# sys.path.append(os.path.abspath(".."))
# Above is only necessary as long as this is under development in playground folder

import streamlit as st
from final_code.pubmed_api import pubmed_api_pull

# creating containers to group elements
header = st.container()
user_input = st.container() 

# Variable to track session status
if "is_running" not in st.session_state:
    st.session_state.is_running = False

with header: 
    st.title("Welcome")


with user_input:
    st.file_uploader("Upload search terms (THIS DOES NOT WORK YET)")
    st.text("or type your search terms")
    input_search_terms = st.text_input("Enter search term", disabled=st.session_state.is_running)
    input_no_of_results = st.number_input("Enter the number of results you want to get", min_value=1, step=1, disabled=st.session_state.is_running)
    
    search_terms_list = []
    if input_search_terms:
        search_terms_list.extend([term.strip() for term in input_search_terms.split(",")])
    # st.write(search_terms_list)

    
    if st.button("Start Processing", disabled=st.session_state.is_running):
        st.session_state.is_running = True  # Deaktiviert die Inputs

        with st.spinner("Processing... Please wait"):
            result = pubmed_api_pull(term_input=search_terms_list, result_no_input=input_no_of_results)

            st.write("### Output:")
            st.write(result)

            st.session_state.is_running = False  # Reaktiviert die Inputs nach Fertigstellung