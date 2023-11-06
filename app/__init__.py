from flask import Flask, redirect, url_for

import app.routes as routes

app = Flask(__name__, template_folder="templates", static_folder="static")

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

app.register_blueprint(routes.oauth, url_prefix="/oauth")
app.register_blueprint(routes.contacts, url_prefix="/contacts")
app.register_blueprint(routes.companies, url_prefix="/companies")
app.register_blueprint(routes.invoices, url_prefix="/invoices")
app.register_blueprint(routes.webhooks, url_prefix="/webhooks")
#app.register_blueprint(routes.auth, url_prefix="/auth")

@app.route("/")
def contacts():
    return redirect(url_for("contacts.list"))
def companies():
    return redirect(url_for("companies.list"))
def invoices():
    return redirect(url_for("invoices.list"))
