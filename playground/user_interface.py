import streamlit as st

# creating containers to group elements
header = st.container()
user_input = st.container() 

with header: 
    st.title("Welcome")

with user_input:
    st.file_uploader("Upload search terms")
    st.text("or type your search terms")
    list_input = st.text_input("Enter search term")
    
    search_terms = []
    
    if list_input:
        search_terms.extend([term.strip() for term in list_input.split(",")])
    st.write("### Extracted Search Terms:")
    for term in search_terms:
        st.write(f"- {term}")