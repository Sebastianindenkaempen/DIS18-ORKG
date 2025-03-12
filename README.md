# DIS18-ORKG

## Topic
Extracting data about time and place of outbreaks from diseases e.g. ehec, avian influenza.

Source:
- PubMed: https://www.ncbi.nlm.nih.gov/books/NBK25501/ 
- PubMed Central: https://pmc.ncbi.nlm.nih.gov/tools/developers/

### PubMed API
The pubmed api contains three different components:
- **ESearch:** searches articles and returns pubmed article ids URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi
- **ESummary:** finds and returns metadata for articles. Input could be the article IDs from ESearch. URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi
- **EFetch:** returns abstracts and full texts. URL: https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi


### Text Mining Ideas

```
import nltk 
import spaCy

```




