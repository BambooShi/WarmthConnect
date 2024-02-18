import json
import os
from os import environ as env
from urllib.parse import quote_plus, urlencode

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, send_from_directory

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

app = Flask(__name__)
# app.config["IMAGE_UPLOADS"] = "C:/Flask/Upload/"
app.secret_key = env.get("APP_SECRET_KEY")

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

oauth = OAuth(app)

oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

def search(category):
    clothes = {('a', 'Socks'), ('b', 'Mittens'), ('c', 'Boots'), ('d', 'Jacket'), ('e', 'Winter Hat')}
    lstOfClothes = []
    for i in clothes:
        if i[1] == category:
            lstOfClothes.append(i)

    return render_template("browse,html", clothes = lstOfClothes)



@app.route("/")
def root():
    return render_template("index.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/browse")
def browse():
    droplst = ['Winter Hat', 'Jacket', 'Snowpants', 'Boots', 'Mittens', 'Gloves', 'Socks', 'Scarfs', 'Ear Muffs', 'Sweater', 'Other']
    return render_template("browse.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4), droplst = droplst)

@app.route("/donate")
def about():
    droplst = ['Winter Hat', 'Jacket', 'Snowpants', 'Boots', 'Mittens', 'Gloves', 'Socks', 'Scarfs', 'Ear Muffs', 'Sweater', 'Other']
    return render_template("donate.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4), droplst = droplst)

@app.route("/user")
def account():
    return render_template("user.html", session=session.get('user'), pretty=json.dumps(session.get('user'), indent=4))

@app.route("/login")
def login():
    return oauth.auth0.authorize_redirect(
        redirect_uri=url_for("callback", _external=True)
    )

@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    session["user"] = token
    return redirect("/")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        "https://" + env.get("AUTH0_DOMAIN")
        + "/v2/logout?"
        + urlencode(
            {
                "returnTo": url_for("root", _external=True),
                "client_id": env.get("AUTH0_CLIENT_ID"),
            },
            quote_via=quote_plus,
        )
    )

@app.route('/upload', methods=['POST'])
def upload_file():
    # clothes = {('a.png', 'Socks'), ('b.png', 'Mittens'), ('c.png', 'Boots'), ('d.png', 'Jacket'), ('e.png', 'Winter Hat')}
    droplst = ['Winter Hat', 'Jacket', 'Snowpants', 'Boots', 'Mittens', 'Gloves', 'Socks', 'Scarfs', 'Ear Muffs', 'Sweater', 'Other']
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        # Save the uploaded file to the UPLOAD_FOLDER
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return render_template('donate.html', filename=file.filename, droplst = droplst)

@app.route('/uploads/<filename>')
def display_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# def stored_info(img_name, category, categories):
    
#     for i in categories:
#         if category == i:
#             #store into database
#             pass
#     return 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=env.get("PORT", 3000))