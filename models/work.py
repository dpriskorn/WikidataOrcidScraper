import logging
from pprint import pprint

from pydantic import BaseModel

from models.item import Item
from models.qlever import QleverIntegrator

logger = logging.getLogger(__name__)


class Work(BaseModel):
    title: str
    doi: str
    # session: Session = requests.session()

    # query = 'select ?work where {{ ?work wdt:P356 "{doi}" }}'.format(
    #     doi=escape_string(doi.upper()))

    @staticmethod
    def escape_string(string: str):
        """This prepares the string for sparql
        Borrowed from Scholia at
        https://github.com/WDscholia/scholia/blob/058cf03b76eb45548928a169fe063586ce9db6de/scholia/query.py#L161C5-L161C60"""
        return string.replace('\\', '\\\\').replace('"', r'\"')

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
            qid = first_binding.get("item").get("value")[31:]
            logger.debug(f"qid found: {qid}")
            return qid
        else:
            return ""

    @property
    def row_html(self):
        """Lookup and return row"""
        qid = self.lookup_qid_using_qlever
        if not qid:
            qid_html = f"<td><a href='{self.scholia_link}'>Missing</a></td>"
        else:
            qid_html = f"<td><a href='{Item(qid=qid).url}'>{qid}</td>"
        return f"""
        <tr>
            <td>{self.title}</td>
            <td>{self.doi}</td>
            {qid_html}
        </tr>
        """

    @property
    def scholia_link(self):
        return f"https://scholia.toolforge.org/doi/{self.doi}"
