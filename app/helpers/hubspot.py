from hubspot import HubSpot
from .oauth import refresh_and_get_access_token, is_authorized
from urllib3.util.retry import Retry


def create_client(portalId=7563398):
    if is_authorized(portalId):
        return HubSpot(access_token=refresh_and_get_access_token(portalId))
    return HubSpot()
