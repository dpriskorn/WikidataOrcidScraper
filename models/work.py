import logging
import timeit
from datetime import date
from urllib.parse import quote

import requests
from pydantic import BaseModel, ConfigDict

from models.item import Item
from models.qlever import QleverIntegrator

logger = logging.getLogger(__name__)


class Work(BaseModel):
    title: str
    doi: str
    date: date
    model_config = ConfigDict(  # dead:disable
        arbitrary_types_allowed=True, extra="forbid"
    )
    citation_count: int | None = None
    qid: str = ""
    # session: Session = requests.session()

    # query = 'select ?work where {{ ?work wdt:P356 "{doi}" }}'.format(
    #     doi=escape_string(doi.upper()))

    @staticmethod
    def escape_string(string: str):
        """This prepares the string for sparql
        Borrowed from Scholia at
        https://github.com/WDscholia/scholia/blob/
        058cf03b76eb45548928a169fe063586ce9db6de/scholia/query.py#L161C5-L161C60
        """
        return string.replace("\\", "\\\\").replace('"', r"\"")

    @property
    def lookup_qid_using_qlever(self):
        logger.debug("lookup_qid_using_qlever: running")
        query = f"""
            PREFIX wdt: <http://www.wikidata.org/prop/direct/>
            SELECT ?item
            WHERE
            {{
              ?item wdt:P356 "{self.escape_string(string=self.doi.upper())}".
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
            self.qid = first_binding.get("item").get("value")[31:]
            logger.debug(f"qid found: {self.qid}")
            return self.qid
        else:
            # logger.debug(f"query: {query}")
            # exit()
            return ""

    @property
    def row_html(self):
        """Lookup and return row"""
        self.fetch_citation_count()  # Fetch citation count
        qid = self.lookup_qid_using_qlever
        qid_html = (
            f"<td><a href='{self.scholia_link}'>Missing</a></td>"
            if not qid
            else f"<td><a href='{Item(qid=qid).url}' target='_blank'>{qid}</td>"
        )
        citation_link = (
            f"https://opencitations.net/index/search?text={self.qouted_doi}&rule=citeddoi"
        )
        citation_count_html = (
            f'<td><a href="{citation_link}" target="_blank">{self.citation_count}</a></td>'
            if self.citation_count is not None
            else "<td>N/A</td>"
        )
        return f"""
        <tr>
            <td>{self.date}</td>
            <td>{self.title}</td>
            <td><a href="{self.doi_link}" target="_blank">{self.doi}</a></td>
            {citation_count_html}
            {qid_html}
        </tr>
        """

    @property
    def scholia_link(self):
        return f"https://scholia.toolforge.org/doi/{self.doi}"

    @property
    def doi_link(self):
        return f"https://doi.org/{self.doi}"

    def fetch_citation_count(self):
        logger.debug("Fetching citation count from OpenCitations")
        start_time = timeit.default_timer()  # Start timing
        endpoint = (
            f"https://opencitations.net/index/"
            f"api/v2/citation-count/doi:{self.qouted_doi}"
        )
        try:
            response = requests.get(endpoint)
            response.raise_for_status()
            citation_data = response.json()
            if (
                citation_data
                and isinstance(citation_data, list)
                and "count" in citation_data[0]
            ):
                self.citation_count = int(citation_data[0]["count"])
            else:
                # We get empty list if no result is found and do nothing
                pass
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching citation count: {e}")
        elapsed_time = timeit.default_timer() - start_time  # Calculate elapsed time
        logger.debug(f"Time taken to fetch citation count: {elapsed_time} seconds")

    @property
    def qouted_doi(self):
        return quote(self.doi)
