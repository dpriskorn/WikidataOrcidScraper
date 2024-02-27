from typing import Any

import requests
from pydantic import ConfigDict
from requests import Session

from models.exceptions import QleverError

from models.wos_base_model import WosBaseModel


class QleverIntegrator(WosBaseModel):
    endpoint: str = "https://qlever.cs.uni-freiburg.de/api/wikidata"
    session: Session = requests.session()
    model_config = ConfigDict(  # dead:disable
        arbitrary_types_allowed=True, extra="forbid"
    )
    action: str = "json_export"

    def execute_qlever_sparql_query(
        self,
        query: str,
    ) -> dict[str, Any]:
        if self.action not in ["tsv_export", "json_export"]:
            raise QleverError(f"Action {self.action} is not supported")
        params = {
            "query": query,
            "action": "json_export",
        }
        try:
            response = self.session.get(
                self.endpoint,
                params=params,
                headers=self.headers,
            )
        except requests.exceptions.ConnectionError:
            raise QleverError(
                "ConnectionError"
            ) from requests.exceptions.ConnectionError
        return response.json()
