import requests
from app.helpers.oauth import refresh_and_get_access_token
import hubspot
from hubspot.crm.companies import  ApiException
#from hubspot.crm.objects.emails import SimplePublicObjectInputForCreate, ApiException
import sys
from pprint import pprint
from flask import Blueprint, request,jsonify
import json
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from hubspot.crm.objects.emails import SimplePublicObjectInput, ApiException
import datetime
from app.helpers.hubspot import create_client

#from ..auth.auth import hubspot_signature_required

module = Blueprint("webhooks", __name__)

@module.route("/handle", methods=["POST"])
#@hubspot_signature_required
# def handle():
#     messages = json.loads(request.data)
#     print(messages)

#     #komet_token = os.getenv("KOMET_TOKEN")
#     #komet_uri=os.getenv("KOMET_URI")
#     for message in messages:

#         #CONSULTA DATOS DE COMPANÍA EN HUBSPOT
#         associatedObjectId=message["objectId"]
#         portalId = message['portalId']
#         hubspot = create_client(portalId)
#         contactDetail = hubspot.crm.contacts.basic_api.get_by_id(
#             contact_id=associatedObjectId, properties=["firstname","compartir_contacto_con","env__correo_por_producto","email"], archived=False)
#         nombreCliente = contactDetail.properties.get('firstname')
#         emailCliente = contactDetail.properties.get('email')
#         modelo = contactDetail.properties.get('env__correo_por_producto')
#         #print(contactDetail)
#         #print(modelo)

#         if not modelo:
#             print("The value is blank. Terminating the process.")
#             sys.exit()
#         else:
#             #Id de la plantilla a utilizar en brevo
#             if modelo == 'CAMION ELECTRICO N800':
#                 idPlantilla = 12
#             elif modelo == 'EASY AUTO ELECTRICO':
#                 idPlantilla = 13
#             elif modelo == 'CARRYING 3.2':
#                 idPlantilla = 7
#             elif modelo == 'CARRYING 3.45':
#                 idPlantilla = 9
#             elif modelo == 'FURGONETA ELECTRICA N520':
#                 idPlantilla = 11
#             elif modelo == 'CARRYING 2.9':
#                 idPlantilla = 10
#             elif modelo == 'CARRYING 5':
#                 idPlantilla = 6
#             elif modelo == 'CARRYING 6.5TN':
#                 idPlantilla = 5
#             elif modelo == 'VIGUS 4X2':
#                 idPlantilla = 4
#             elif modelo == 'VIGUS PRO':
#                 idPlantilla = 3
#             elif modelo == 'VIGUS WORK 4X4':
#                 idPlantilla = 1
#             else:
#                 idPlantilla = 1
        
#             ownerid = contactDetail.properties.get('compartir_contacto_con')
#             #print("Detalles del contacto: " + str(contactDetail))
#             #print("Detalles del contacto: ")

#             owner = hubspot.crm.owners.owners_api.get_by_id(ownerid, archived=False)
#             #print("Detalles del Usuario: " + str(owner))
#             correoAsesor = owner.email
#             firstNameAsesor = owner.first_name
#             lastNameAsesor = owner.last_name

#             if message["subscriptionType"] == "contact.propertyChange":

#                 configuration = sib_api_v3_sdk.Configuration()
#                 configuration.api_key['api-key'] = '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'

#                 #modelo = "VIGUS WORK"
#                 api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))
#                 subject = nombreCliente +" tú próximo vehículo " + modelo
#                 #idPlantilla = 1
#             #emailCliente = "carlos@evolutivos.net"
#             #nombreCliente = "Carlos"
#             #apellidoCliente = "Quillupangui"
#                 nombreAsesor = firstNameAsesor + lastNameAsesor
#                 sender = {"name":"JMC - Galmack","email":correoAsesor}
#                 to = [{"email":emailCliente,"name":nombreCliente}]
#                 reply_to = {"email":correoAsesor,"name":nombreAsesor}
#                 params = {"ASESOR": firstNameAsesor +" "+ lastNameAsesor , "NOMBRE": nombreCliente}
#                 send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(to=to, reply_to=reply_to, sender=sender, subject=subject, template_id=idPlantilla, params={"ASESOR": firstNameAsesor +" "+ lastNameAsesor , "NOMBRE": nombreCliente})
#                 datosEngagement = {
#                     "subject":subject,
#                     "ownerId":ownerid,
#                     "contactId":associatedObjectId,
#                 }
#                 try:
#                     api_response = api_instance.send_transac_email(send_smtp_email)
#                     pprint(api_response)
#                     engagement(datosEngagement)

#                 except ApiException as e:
#                     print("Exception when calling SMTPApi->send_transac_email: %s\n" % e)

#     return "", 204

def handle():
    try:
        contact_data = json.loads(request.data)
        hubspot = create_client()
        properties = contact_data.get("properties", {})
        print(properties)
        simple_public_object_input = SimplePublicObjectInput(properties=properties)
        contact = hubspot.crm.contacts.basic_api.create(simple_public_object_input=simple_public_object_input)
        return "", 200
    except ApiException as e:
        if e.status == 409 and "Contact already exists" in str(e):
            print("El contacto ya existe. Puedes manejarlo aquí.")
        else:
            print("Exception when creating contact: %s\n" % e)

    return "", 204


def engagement(datosEngagement):
    current_time = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")


    headers = {
        'authorization': 'Bearer pat-na1-963a84ec-b4c7-470e-b22e-aed1aca6345c',
        'content-type': 'application/json',
    }

    data = { "properties": { "hs_timestamp": current_time, "hubspot_owner_id": datosEngagement["ownerId"], "hs_email_direction": "EMAIL", "hs_email_status": "SENT", "hs_email_subject": datosEngagement["subject"], "hs_email_text": datosEngagement["subject"] }, "associations": [ { "to": { "id": datosEngagement["contactId"] }, "types": [ { "associationCategory": "HUBSPOT_DEFINED", "associationTypeId": 10 } ] } ] }
    data_json = json.dumps(data)
    response = requests.post('https://api.hubapi.com/crm/v3/objects/emails', headers=headers, data=data_json)