# Wikidata Orcid Scraper
This tool helps scrape DOIs from https://orcid.org/ and curate them using Scholia

![image](https://github.com/dpriskorn/WikidataOrcidScraper/assets/68460690/33e917a1-09f8-4e22-8830-85b178964c58)

## Features
* lookup on works on orcid.org and extraction of work with DOIs
* lookup of DOIs on Wikidata to determine if it has been imported or not
* presenting a table with information to the user and helping them import missing articles
* lookup of citation count in OpenCitations and linking to the result

## Documentation
https://www.wikidata.org/wiki/Wikidata:Tools/Wikidata_Orcid_Scraper

## Choice of SPARQL endpoint
This tool uses the QLever Wikidata SPARQL 
endpoint to detect if a DOI is missing in Wikidata. 
The endpoint is currently updated weekly from the official Wikidata dumps. 

The QLever endpoint was chosen because it is faster and more 
reliable than current available alternatives, see 
https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/WDQS_backend_update/WDQS_backend_alternatives#A_performance_evaluation_of_QLever,_Virtuoso,_Blazegraph,_GraphDB,_Stardog,_Jena,_and_Oxigraph.

## Development
Run it like so outside Docker:
`$ gunicorn app:app`

## License
GPLv3+