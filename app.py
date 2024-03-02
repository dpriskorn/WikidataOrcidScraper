"""
pseudo code
let user type in an orcid, accept orcid-parameter
lookup and parse all DOIs from the orcid page
lookup each doi in Wikidata using QLever (its crazy fast compared to current Wikimedia services)
present the dois to the user and clickable links to scholia for those not found in wikidata
"""
import logging

from flask import request, render_template, Flask, jsonify
from flask.typing import ResponseReturnValue
from markupsafe import escape

import config
from models.item import Item
from models.orcid import Orcid

app = Flask(__name__)
if config.debug:
    logging.basicConfig(level=logging.DEBUG)
else:
    logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

invalid_format = "Not a valid QID, format must be 'Q[0-9]+'"
user_agent = "Wikidata Orcid Scraper (https://github.com/dpriskorn/WikidataOrcidScraper; User:So9q) python-requests/2.31.0"
documentation_url = (
    "https://www.wikidata.org/wiki/Wikidata:Tools/Wikidata_Orcid_Scraper"
)


@app.route("/", methods=["GET"])
def index() -> ResponseReturnValue:  # noqa: C901, PLR0911, PLR0912
    orcid = escape(request.args.get("orcid", ""))
    qid = escape(request.args.get("qid", ""))
    # if not str(qid) and not str(orcid):
    #     return jsonify("Error: Got no QID or ORCID")
    return render_template("index.html", qid=qid, orcid=orcid)


@app.route("/results", methods=["GET"])
def results() -> ResponseReturnValue:  # noqa: C901, PLR0911, PLR0912
    raw_orcid = escape(request.args.get("orcid", ""))
    qid = escape(request.args.get("qid", ""))
    # label = escape(request.args.get("label", ""))
    # description = escape(request.args.get("description", ""))
    size = escape(request.args.get("size", 10))
    offset = escape(request.args.get("offset", 0))
    # First get using orcid, fallback to looking up the orcid via the QID.
    if raw_orcid:
        orcid = Orcid(string=raw_orcid, size=size, offset=offset)
        rows = orcid.get_works_html
    elif qid and not raw_orcid:
        item = Item(qid=qid)
        item_orcid = item.orcid
        if item_orcid:
            orcid = Orcid(string=item_orcid, size=size, offset=offset)
            rows = orcid.get_works_html
        else:
            return render_template(
                "error.html", qid=qid, qid_url=item.url, query=item.orcid_query
            )
    else:
        return jsonify("Error: We need either a QID or ORCID")
    return render_template(
        "results.html",
        qid=qid,
        orcid=raw_orcid,
        # label=label,
        # description=description,
        rows=rows,
        offset=int(offset) + int(size),
        size=size,
    )
