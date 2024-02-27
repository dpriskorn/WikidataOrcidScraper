from pydantic import BaseModel


class WosBaseModel(BaseModel):
    @property
    def user_agent(self):
        return (
            "Wikidata Orcid Scraper (https://github.com/dpriskorn/WikidataOrcidScraper/; "
            "User:So9q) python-requests/2.31.0"
        )

    @property
    def headers(self):
        return {"User-Agent": self.user_agent}
