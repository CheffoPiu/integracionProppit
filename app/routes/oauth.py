import json
from flask import Blueprint, render_template, redirect, request
from hubspot.utils.oauth import get_auth_url
import os

import requests
from ..helpers.oauth import save_tokens, get_redirect_uri
from ..helpers.hubspot import create_client

module = Blueprint("oauth", __name__)


@module.route("/login")
def login():
    return render_template("oauth/login.html")


@module.route("/authorize")
def authorize():
    auth_url = get_auth_url(
        scopes=("crm.objects.contacts.read",),
        client_id = os.getenv("HUBSPOT_CLIENT_ID"),
        redirect_uri=get_redirect_uri(),
    )

    return redirect(auth_url)


@module.route("/callback")
def callback():
    hubspot = create_client()
    redirect_uri_s = get_redirect_uri()
    #cambio para que funcione en railway
    redirect_uri_s = redirect_uri_s.replace("http", "https", 1)
    tokens_response = hubspot.auth.oauth.tokens_api.create_token(
        grant_type="authorization_code",
        code=request.args.get("code"),
        redirect_uri=redirect_uri_s,#get_redirect_uri(),
        client_id = os.getenv("HUBSPOT_CLIENT_ID"),
        client_secret= os.getenv("HUBSPOT_CLIENT_SECRET"),
    )
    refresh = tokens_response.__getattribute__('refresh_token')
    url = 'https://api.hubapi.com/oauth/v1/refresh-tokens/' + str(refresh)
    uri = requests.get(url)
    cadena_json = json.loads(uri.content)
    portalId=cadena_json['hub_id']
    save_tokens(tokens_response, portalId)


    return redirect("/")
