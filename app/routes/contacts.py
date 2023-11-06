from flask import Blueprint, render_template

from ..auth import auth_required
from ..helpers.hubspot import create_client

module = Blueprint("contacts", __name__)


@module.route("/")
@auth_required
def list():
    hubspot = create_client()
    contacts_page = hubspot.crm.contacts.basic_api.get_page()

    return render_template("contacts/list.html", contacts=contacts_page.results)
