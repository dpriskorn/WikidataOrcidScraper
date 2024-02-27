import logging
from pprint import pprint

from pydantic import BaseModel

from models.qlever import QleverIntegrator

logger = logging.getLogger(__name__)


class Item(BaseModel):
    qid: str

    @property
    def lookup_orcid_using_qlever(self):
        logger.debug("lookup_doi_using_qlever: running")
        query = f"""
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            PREFIX wd: <http://www.wikidata.org/entity/>
            SELECT ?orcid
            WHERE
            {{
              wd:{self.qid} wdt:P496 ?orcid.
            }}
        """
        qi = QleverIntegrator()
        result = qi.execute_qlever_sparql_query(query=query)
        # pprint(result)
        # empty result
        # {'head': {'vars': ['item']}, 'results': {'bindings': []}}
        bindings = result.get("results").get("bindings")
        if bindings:
            first_binding = bindings[0]
            # pprint(first_binding)
            orcid = first_binding.get("orcid").get("value")
            logger.debug(f"orcid found: {orcid}")
            return orcid
        else:
            return ""

    @property
    def orcid(self) -> str:
        """Return string if an orcid is found, else empty string"""
        return self.lookup_orcid_using_qlever

    # @property
    # def row_html(self):
    #     raise NotImplementedError()
    #     # return

    @property
    def url(self):
        return f"https://www.wikidata.org/wiki/{self.qid}"
