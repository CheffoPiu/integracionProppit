import logging
import time
import os
from flask import session, request
from hubspot import HubSpot
from .dbconection import get_colection, get_database

TOKENS_KEY = "tokens"

def save_tokens(tokens_response, idPortal):
    collection_name = get_colection("naranjodev")
    tokens = {
        "access_token": tokens_response.access_token,
        "refresh_token": tokens_response.refresh_token,
        "expires_in": tokens_response.expires_in,
        "expires_at": time.time() + tokens_response.expires_in * 0.95,
        "update": time.time(),
        "idPortal": idPortal,
    }
    collection_name.update_one({"idPortal": idPortal}, {
                               "$set": tokens}, upsert=True)
    return tokens


def is_authorized(portalId=4653202):
    collection_name = get_colection("naranjodev")
    item_details = collection_name.find_one({"idPortal": portalId})
    if item_details:
        tokens = {
        "access_token": item_details['access_token'],
        "refresh_token": item_details['refresh_token'],
        "expires_in": item_details['expires_in'],
        "expires_at": item_details['expires_at'],
        "idPortal": item_details['idPortal'],
        }
        # This does not give a very readable output
        TOKENS_KEY = tokens
    else:
        return False
    return TOKENS_KEY


def get_redirect_uri():
    return request.url_root + "oauth/callback"


def refresh_and_get_access_token(portalId=4653202):
    try:
        if not TOKENS_KEY:
            raise Exception("No refresh token is specified")
        tokens = is_authorized(portalId)
        collection_name = get_colection("naranjodev")
        if time.time() > tokens["expires_at"]:
            tokens = HubSpot().auth.oauth.tokens_api.create_token(
                grant_type="refresh_token",
                redirect_uri=get_redirect_uri(),
                refresh_token=tokens["refresh_token"],
                client_id= os.getenv("HUBSPOT_CLIENT_ID"),
                client_secret= os.getenv("HUBSPOT_CLIENT_SECRET"),
            )
            tokens = save_tokens(tokens, portalId)
            collection_name.update_one({"idPortal": portalId}, {
                                       "$set": tokens}, upsert=True)
            logging.debug("tokens2: %s", tokens)
            return tokens
    except Exception as inst:
            print(type(inst))    # the exception instance
            print(inst.args)     # arguments stored in .args
            print(inst)          # __str__ allows args to be printed directly,
            logging.exception('Excepcion en consulta de hubspot company')
            print('Error en consulta de hubspot company')
            raise
    return tokens["access_token"]

def access_token():
    return os.getenv['ACCESS_TOKEN']

def api_key():
  return os.getenv['HUBSPOT_API_KEY']