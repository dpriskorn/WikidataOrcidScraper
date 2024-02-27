import logging
from pprint import pprint
from typing import Any

import requests
from pydantic import BaseModel

from models.work import Work

logger = logging.getLogger(__name__)


class Orcid(BaseModel):
    """This models and Orcid and handles lookup of works"""

    string: str
    work_ids: list[int] = list()
    data: dict[str, Any] = dict()
    works: list[Work] = list()
    size: int = 10

    def fetch_works(self) -> None:
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:122.0) Gecko/20100101 Firefox/122.0",
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            # 'Accept-Encoding': 'gzip, deflate, br',
            "DNT": "1",
            "Connection": "keep-alive",
            "Referer": f"https://orcid.org/{self.string}",
            # 'Cookie': 'OptanonConsent=isGpcEnabled=0&datestamp=Tue+Feb+27+2024+14%3A44%3A07+GMT%2B0100+(Central+European+Standard+Time)&version=202310.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A0%2CC0002%3A0%2CC0004%3A0&geolocation=SE%3BAB&AwaitingReconsent=false; OptanonAlertBoxClosed=2023-09-29T06:15:47.379Z; AWSELB=CBD1D7FF1216388FA48838CBCA4774FD22800B8FB545D06FEB9283714EEA743BF0AEC8577FE0987F26953880E03BEBC61E2D483454FC30309233403CE21DC641E9CE0FEC59; AWSELBCORS=CBD1D7FF1216388FA48838CBCA4774FD22800B8FB545D06FEB9283714EEA743BF0AEC8577FE0987F26953880E03BEBC61E2D483454FC30309233403CE21DC641E9CE0FEC59; locale_v3=en; JSESSIONID=C9B1BD81591B298C5D8FB6D5124BA3AF; XSRF-TOKEN=c03a1a36-a005-41b3-90d9-0b955b867819',
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            # Requests doesn't support trailers
            # 'TE': 'trailers',
        }
        url = f"https://orcid.org/{self.string}/worksExtendedPage.json?offset=0&sort=date&sortAsc=false&pageSize={self.size}"
        logger.debug(f"url: {url}")
        # exit()
        response = requests.get(
            url,
            headers=headers,  # cookies=cookies
        )
        if response.status_code == 200:
            logger.debug("got 200")
            self.data = response.json()
            # pprint(self.data)
        else:
            raise Exception(f"got {response.status_code} from ORCID, {response.text}")

    @staticmethod
    def get_doi(work: dict[str, Any]) -> str:
        """Extract the first DOI found"""
        external_ids = work.get("externalIdentifiers", [])
        if external_ids:
            for id_ in external_ids:
                type_ = id_.get("externalIdentifierType", None)
                value = ""
                if type_ is not None:
                    value = type_.get("value")
                if value == "doi":
                    normalized_doi = id_.get("normalized")
                    if normalized_doi:
                        doi = normalized_doi.get("value")
                        # there is a doi url also, but we ignore it for now
                        return doi
        return ""

    @staticmethod
    def get_title(work: dict[str, Any]) -> str:
        """Extract the first DOI found"""
        works = work.get("works", [])
        if works:
            first_work = works[0]
            first_title = first_work.get("title", None)
            if first_title is not None:
                title = first_title.get("value")
                return title
        return ""

    def parse_data(self):
        """Parse DOIs from ORCID public API
        the data looks like this:
        {'groups': [{'activePutCode': 145170415,
                     'activeVisibility': 'PUBLIC',
                     'defaultPutCode': 145170415,
                     'externalIdentifiers': [{'errors': [],
                                              'externalIdentifierId': {'errors': [],
                                                                       'getRequiredMessage': None,
                                                                       'required': True,
                                                                       'value': '10.5281/zenodo.10022068'},
                                              'externalIdentifierType': {'errors': [],
                                                                         'getRequiredMessage': None,
                                                                         'required': True,
                                                                         'value': 'doi'},
                                              'normalized': {'errors': [],
                                                             'getRequiredMessage': None,
                                                             'required': False,
                                                             'value': '10.5281/zenodo.10022068'},
                                              'normalizedUrl': {'errors': [],
                                                                'getRequiredMessage': None,
                                                                'required': False,
                                                                'value': 'https://doi.org/10.5281/zenodo.10022068'},
                                              'relationship': {'errors': [],
                                                               'getRequiredMessage': None,
                                                               'required': True,
                                                               'value': 'self'},
                                              'url': None}],
                     'groupId': 0,
                     'userVersionPresent': False,
                      'works': [{'assertionOriginClientId': None,
                        'assertionOriginName': None,
                        'assertionOriginOrcid': None,
                        'citation': None,
                        'contributors': None,
                        'contributorsGroupedByOrcid': [{'contributorAttributes': None,
                                                        'contributorEmail': None,
                                                        'contributorOrcid': {'host': 'orcid.org',
                                                                             'path': '0000-0003-0997-367X',
                                                                             'uri': 'https://orcid.org/0000-0003-0997-367X'},
                                                        'creditName': {'content': 'Olga '
                                                                                  'Lopopolo'},
                                                        'rolesAndSequences': []},
                                                       {'contributorAttributes': None,
                                                        'contributorEmail': None,
                                                        'contributorOrcid': {'host': 'orcid.org',
                                                                             'path': '0000-0002-5732-3957',
                                                                             'uri': 'https://orcid.org/0000-0002-5732-3957'},
                                                        'creditName': {'content': 'Arianna '
                                                                                  'Bienati'},
                                                        'rolesAndSequences': []},
                                                       {'contributorAttributes': None,
                                                        'contributorEmail': None,
                                                        'contributorOrcid': {'host': 'orcid.org',
                                                                             'path': '0000-0003-2471-7797',
                                                                             'uri': 'https://orcid.org/0000-0003-2471-7797'},
                                                        'creditName': {'content': 'Paolo '
                                                                                  'Brasolin'},
                                                        'rolesAndSequences': []},
                                                       {'contributorAttributes': None,
                                                        'contributorEmail': None,
                                                        'contributorOrcid': {'host': 'orcid.org',
                                                                             'path': '0000-0002-9570-294X',
                                                                             'uri': 'https://orcid.org/0000-0002-9570-294X'},
                                                        'creditName': {'content': 'Elena '
                                                                                  'Ferrato'},
                                                        'rolesAndSequences': []},
                                                       {'contributorAttributes': None,
                                                        'contributorEmail': None,
                                                        'contributorOrcid': {'host': 'orcid.org',
                                                                             'path': '0000-0002-7008-6394',
                                                                             'uri': 'https://orcid.org/0000-0002-7008-6394'},
                                                        'creditName': {'content': 'Jennifer-Carmen '
                                                                                  'Frey'},
                                                        'rolesAndSequences': []},
                                                       {'contributorAttributes': None,
                                                        'contributorEmail': None,
                                                        'contributorOrcid': {'host': 'orcid.org',
                                                                             'path': '0000-0003-1357-1702',
                                                                             'uri': 'https://orcid.org/0000-0003-1357-1702'},
                                                        'creditName': {'content': 'Aivars '
                                                                                  'Glaznieks'},
                                                        'rolesAndSequences': []},
                                                       {'contributorAttributes': None,
                                                        'contributorEmail': None,
                                                        'contributorOrcid': {'host': 'orcid.org',
                                                                             'path': '0000-0002-1768-5662',
                                                                             'uri': 'https://orcid.org/0000-0002-1768-5662'},
                                                        'creditName': {'content': 'Marta '
                                                                                  'Guarda'},
                                                        'rolesAndSequences': []},
                                                       {'contributorAttributes': None,
                                                        'contributorEmail': None,
                                                        'contributorOrcid': {'host': 'orcid.org',
                                                                             'path': '0000-0002-7655-5526',
                                                                             'uri': 'https://orcid.org/0000-0002-7655-5526'},
                                                        'creditName': {'content': 'egon '
                                                                                  'stemle'},
                                                        'rolesAndSequences': []},
                                                       {'contributorAttributes': None,
                                                        'contributorEmail': None,
                                                        'contributorOrcid': {'host': 'orcid.org',
                                                                             'path': '0000-0001-5183-9613',
                                                                             'uri': 'https://orcid.org/0000-0001-5183-9613'},
                                                        'creditName': {'content': 'Fabio '
                                                                                  'Zanda'},
                                                        'rolesAndSequences': []}],
                        'countryCode': None,
                        'countryName': None,
                        'createdDate': {'day': '24',
                                        'errors': [],
                                        'getRequiredMessage': None,
                                        'month': '10',
                                        'required': True,
                                        'year': '2023'},
                        'dateSortString': None,
                        'errors': [],
                        'journalTitle': {'errors': [],
                                         'getRequiredMessage': None,
                                         'required': True,
                                         'value': 'LCRGradConf23 organizing '
                                                  'commitee'},
                        'languageCode': None,
                        'languageName': None,
                        'lastModified': {'day': '24',
                                         'errors': [],
                                         'getRequiredMessage': None,
                                         'month': '10',
                                         'required': True,
                                         'year': '2023'},
                        'numberOfContributors': 9,
                        'publicationDate': {'day': '25',
                                            'errors': [],
                                            'getRequiredMessage': None,
                                            'month': '10',
                                            'required': True,
                                            'year': '2023'},
                        'putCode': {'errors': [],
                                    'getRequiredMessage': None,
                                    'required': True,
                                    'value': '145170415'},
                        'shortDescription': None,
                        'source': '0000-0001-8099-6984',
                        'sourceName': 'DataCite',
                        'subtitle': None,
                        'title': {'errors': [],
                                  'getRequiredMessage': None,
                                  'required': True,
                                  'value': 'Book of abstracts of The Graduate '
                                           'Student Conference in Learner '
                                           'Corpus Research 2023'},
                        'translatedTitle': None,
                        'url': None,
                        'visibility': {'errors': [],
                                       'getRequiredMessage': None,
                                       'required': True,
                                       'visibility': 'PUBLIC'},
                        'workCategory': None,
                        'workExternalIdentifiers': [{'errors': [],
                                                     'externalIdentifierId': {'errors': [],
                                                                              'getRequiredMessage': None,
                                                                              'required': True,
                                                                              'value': '10.5281/zenodo.10022068'},
                                                     'externalIdentifierType': {'errors': [],
                                                                                'getRequiredMessage': None,
                                                                                'required': True,
                                                                                'value': 'doi'},
                                                     'normalized': {'errors': [],
                                                                    'getRequiredMessage': None,
                                                                    'required': False,
                                                                    'value': '10.5281/zenodo.10022068'},
                                                     'normalizedUrl': {'errors': [],
                                                                       'getRequiredMessage': None,
                                                                       'required': False,
                                                                       'value': 'https://doi.org/10.5281/zenodo.10022068'},
                                                     'relationship': {'errors': [],
                                                                      'getRequiredMessage': None,
                                                                      'required': True,
                                                                      'value': 'self'},
                                                     'url': None}],
                        'workType': {'errors': [],
                                     'getRequiredMessage': None,
                                     'required': True,
                                     'value': 'other'}}]},

        """
        for work in self.data.get("groups"):
            doi = self.get_doi(work=work)
            if doi:
                title = self.get_title(work=work)
                work = Work(title=title, doi=doi)
                pprint(work.model_dump())
                # exit()
                self.works.append(work)

    @property
    def get_works_html(self) -> str:
        self.fetch_works()
        self.parse_data()
        return self.generate_html_rows

    @property
    def generate_html_rows(self):
        rows = []
        for work in self.works:
            rows.append(work.row_html)
        return "\n".join(rows)
