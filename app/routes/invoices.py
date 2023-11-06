from flask import Blueprint, render_template, request, jsonify, make_response
from ..helpers.hubspot import create_client
from ..auth import auth_required
import os
import requests
import json
import logging
import datetime

module = Blueprint("invoices", __name__)

@module.route("/")
@auth_required
def list():
    hubspot = create_client()
    invoices_page = hubspot.crm.contacts.basic_api.get_page()
    return render_template("invoices/list.html", invoices=invoices_page.results)

@module.route('/company', methods=['GET'])
def company():
    logging.info("Company")
    userId = request.args.get('userId', default = 1, type = int)
    userEmail = request.args.get('userEmail', default = '*', type = str)
    associatedObjectId = request.args.get('associatedObjectId', default = 1, type = int)
    associatedObjectType = request.args.get('associatedObjectType', default = '*', type = str)
    associatedcompanyid = request.args.get('associatedcompanyid', default = 1, type = int)
    portalId = request.args.get('portalId', default=1, type=int)
    
    try:
        if associatedObjectType == 'COMPANY':
            associatedObjectId = associatedObjectId
        else:
            if associatedObjectType == 'CONTACT':
                associatedObjectId = associatedcompanyid
        hubspot = create_client(portalId)
        companyDetail = hubspot.crm.companies.basic_api.get_by_id(company_id=associatedObjectId, properties=["idKometSales"], archived=False)
        results = []

        if companyDetail.properties.get('idkometsales') is None:
            result = {
                "objectId": 1,
                "title": "It is not associated with the Komet system",
                }
            results.append(result)
        else:
            idCompanyKS = companyDetail.properties['idkometsales']
            komet_token= os.getenv("KOMET_TOKEN")
            komet_uri=os.getenv("KOMET_URI")
            server_url = os.getenv("URL_SERVER")
            fecha_actual = datetime.datetime.now().date()
            fecha_anterior = (datetime.datetime.now() - datetime.timedelta(days=60)).date()
            uri=komet_uri+'invoice.list?authenticationToken='+komet_token+'&orderDateFrom='+str(fecha_anterior)+'&orderDateTo='+str(fecha_actual)+'&customerId='+idCompanyKS
            r = requests.get(uri)
            cadena_json = json.loads(r.content)
            
            if cadena_json['message'] != 'Orders not found.':
                for invoice in cadena_json['invoices']:
                    linkPDF = str(server_url) + \
                        'invoices/pdfInvoice?invoiceId=' + str(invoice['id'])
                    result = {
                        "objectId": invoice['id'],
                        "title": "Invoice "+str(invoice['number']),
                        "link": linkPDF,
                        "created": invoice['createdOn'],
                        "total": {
                            "label": "Resolution impact",
                            "dataType": "CURRENCY",
                            "value": invoice['total'],
                            "currencyCode": "USD"
                        },
                        "salesPersonName": invoice['salesPersonName'],
                        "invoiceNotes": invoice['invoiceNotes'],
                        "status": invoice['status'],
                        "carrierName": invoice['carrierName'],
                        "updatedOn": invoice['updatedOn'],
                        }
                    results.append(result)
            else:         
                result = {
                    "objectId": 1,
                    "title": "There are no invoices in the last 60 days",
                    }
                results.append(result)

        respuesta = {}
        respuesta['primaryAction'] = {
                "type": "IFRAME",
                "width": 890,
                "height": 748,
                "uri": "https://app.kometsales.com/",
                "label": "Create Invoice"
                }
        respuesta['results'] = results

    except Exception as inst:
        print(type(inst))    # the exception instance
        print(inst.args)     # arguments stored in .args
        print(inst)          # __str__ allows args to be printed directly,
                            # but may be overridden in exception subclasses
        x, y = inst.args     # unpack args
        print('x =', x)
        print('y =', y)
        logging.exception('Excepcion en consulta de hubspot company')
        print('Error en consulta de hubspot company')
        raise
    return jsonify(respuesta)


@module.route('/pdfInvoice', methods=['GET'])
def pdfInvoice():
    logging.info("pdfInvoice")
    invoiceId = request.args.get('invoiceId', default=1, type=int)
    komet_token = os.getenv("KOMET_TOKEN")

    try:
        #Llamada a Komet para generar la factura
        url = 'https://api.kometsales.com/api/invoice.pdf.get'
        myobj = {
            "authenticationToken": komet_token,
            "invoiceId": invoiceId
        }
        x = requests.post(url, json=myobj)
        dataStr = json.loads(x.text)
        #Datos del archivo generado
        listData = dataStr['file']
        #Convierte a lista de enteros
        delim = ','
        l3 = listData.split(delim)
        l3 = [int(i) for i in l3]
        l1 = []
        #cambia de tipo de dato
        for x in l3:
            if(x<0):
                aux=256+x
            else:
                aux=x
            l1.append(aux)
        #Cast a bytearray
        x1 = bytearray(l1)
        #Se hace el response para devolver el archivo
        response = make_response(x1)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = \
            'inline; filename=%s.pdf' % 'yourfilename'
        return response
    
    except Exception as inst:
        print(type(inst))    # the exception instance
        print(inst.args)     # arguments stored in .args
        print(inst)          # __str__ allows args to be printed directly,
        raise
