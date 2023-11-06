from flask import Blueprint, render_template
from ..helpers.hubspot import create_client
from ..auth import auth_required


module = Blueprint("companies", __name__)


@module.route("/")
@auth_required
def list():
    hubspot = create_client()
    companies_page = hubspot.crm.companies.basic_api.get_page()
    
    return render_template("companies/list.html", companies=companies_page.results)

