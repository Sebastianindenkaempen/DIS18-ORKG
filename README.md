## How to use this repository
1. Clone this repository
2. Navigate into this repository using the command line `cd ./DIS18-ORKG`
3. Build the docker image by running: `docker build -t outbreak-analyzer .` (If it does not work, try `docker build --platform linux/amd64 -t outbreak-analyzer .`)
4. Start the container by using `docker run -p 8501:8501 -p 11434:11434 outbreak-analyzer`


## Table of Contents
* [Problem statement](#problem-statement)
* [The user Interface](#the-user-interface)
* [PubMed extraction process](#pubmed-extraction-process)
* [Text Mining](#text-mining)
* [Output](#output)
* [Known issues](#known-issues)
* [Sources](#sources)

## Problem statement
The code in this repository aims to make it as easy as possible for users to automatically or semi-automatically
extract data (location, time) related to outbreaks of specific diseases from articles listed in PubMed and upload them back to ORKG.

## The User Interface
To give the user of this repository an easy entry to the topic we created a user interface. To create the interface we used the python package streamlit. <br>
In case you want to understand the code further, you also can use the provided jupyter notebooks which contain the same code as the user interface but obviously shown more in depth. 

## PubMed extraction process
To automatically get all the date we need, we used the PubMed api, which is provided by Entrez. The API is actually divided into three main components: esearch, esummary and efetch. [[1]](#[1]) <br>
We are also using two different Entrez Databases: PubMed for sending the search request to and pubmed central to retrieve the fulltexts from. <br>

To send a specific search request to pubmed and receive the pubmed ids, we are using the esearch part. This is done using the function get_pmids (TODO: Link to code). <br> This function uses the pubmed database as it is slightly easier to query. <br> 
During the project we noticed that only using a free text query term does provide a few problems. Most important, a lot of the retrieved articles did not exactly did not contain information about concrete outbreaks. Therefore we included a preprocessing of the search terms, which translates the term into meSH-Terms (TODO: Link to Code)  

As the pubmed database does not offer fulltexts for the articles we have to translate the received pubmed ids into pubmed central (pmc) ids. We are doing this by using the function translate_pmid_to_pmcid (TODO: Link to code) and the esummary api components as it provides meta data from articles. 

To extract the full text and further metadata about the articles we are using the esummary api components as well as the pubmed central database. We use the earlier retrieved pmc ids to query this database. Therefore we also use the function get_full_xml (TODO: Link to code) <br>
This only returns a xml sceleton from which we extract all necessary information by using the function extract_article_data (TODO: Link to code). This returns the information in a structured dataframe format. 

## Text Mining
For the Text Mining, we tried a lot of approaches and included the most promising into the user interface. 

#### SpaCy Modes
As stated in the name, this approach uses the python package spaCy to find the relevant outbreak data. Therefore we use a PhraseMatcher. This PhraseMatcher extracts all sentences from a text, which contain a predefined pattern. We defined a few patterns that we found in the text, but please be aware that this list is not nearly complete. <br>
After extracting the sentences that match the phrases we are using NER (names entity recognition) from spaCy to extract place and time of the outbreak. <br>
The user interface let's you choose between abstract-only and abstract + full text mode. As the names suggest, the first mode only applies the process to the abstract, the second approach first combines the texts from abstract and fulltext and then applies the process. Abstract-only is of course (much) faster but may also miss some information as they may be mentioned in the fulltext only. 

#### LLM Mode
The large language model (LLM) Mode uses a local language model hosted in ollama to extract the relevant information. We decided to go for the phi4-mini model as it seemed to deliver a sweet spot of performance and accuracy during our testing. Using the summarize_outbreak (TODO: LINK) function we ask the LLM to summarize all relevant information from the abstract. Afterwards we apply the named entity recognition from spaCy to systematically extract the place and time information from this summary. <br>
We decided to only use the abstract in this approach as analysing the fulltext took way to long on our machines. If you have access to more computing power feel free to also include the full text to this approach.

## Output
The user interface lets you choose which kind of outout you prefer. In any case you can download the result of the process by klicking the download symbol on the top right corner of the output table. 

#### ORKG Format
This format is specifically prepared to be uploaded to ORKG by using the CSV upload function. Therefore all the columns are specifically named so that ORKG can find the matches right away. In some cases the data format of specific cells or rows is not compatible with ORKG. In these cases the output can be manually corrected either directly in ORKG or in the user interface. 

#### Raw Format
This format is ideal for bugfixing or understanding exactly how the process works. It also offers a possibility to download the data and apply other use cases but to upload to ORKG. 

## Known Issues
For all known issues, there are issues created directly in github. Feel free to create your own branch to assess a certain issue or to open your own issue. As this project is part of an university exam in the bachelors degree of Data and Information Science at the University of applied science cologne it is unlikely that there will be a lot of further development from the creators of this repository. 

## Sources

#### [1]


- PubMed: https://www.ncbi.nlm.nih.gov/books/NBK25501/ 
- PubMed Central: https://pmc.ncbi.nlm.nih.gov/tools/developers/

### PubMed API
The pubmed api contains three different components:
- **ESearch:** searches articles and returns pubmed article ids URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
- **ESummary:** finds and returns metadata for articles. Input could be the article IDs from ESearch. URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi
- **EFetch:** returns abstracts and full texts. URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi

Source: https://www.ncbi.nlm.nih.gov/books/NBK25500/

Sources Text Mining: https://pmc.ncbi.nlm.nih.gov/tools/textmining/ 



### ORKG 
- CSV Upload: https://orkg.org/help-center/article/16/Import_CSV_files_in_ORKG 

## Repo structure 
### Folder final_code    
Contains tested functions, that can be called
### Folder playground
Contains code that is in developement or not yet tested

