"""
pseudo code
let user type in an orcid, accept orcid-parameter
lookup and parse all DOIs from the orcid page
lookup each doi in Wikidata using HUB
present the dois to the user and clickable links to scholia for those not found in wikidata
"""
import logging
import os

from flask import request, render_template, Flask, jsonify
from flask.typing import ResponseReturnValue
from markupsafe import escape

from models.item import Item
from models.orcid import Orcid

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
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
    label = escape(request.args.get("label", ""))
    description = escape(request.args.get("description", ""))
    size = escape(request.args.get("size", 10))
    offset = escape(request.args.get("offset", 0))
    # if not str(qid) and not str(raw_orcid):
    #     return jsonify("Error: We need either a QID or ORCID")
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
            return jsonify(f"Error: No ORCID found on {qid}, see {item.url}")
    else:
        return jsonify("Error: We need either a QID or ORCID")
    return render_template(
        "results.html",
        qid=qid,
        orcid=raw_orcid,
        label=label,
        description=description,
        rows=rows,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
