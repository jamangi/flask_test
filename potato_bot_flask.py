from decouple import config
from flask import Flask, render_template, request, session, redirect
from zenora import APIClient
from datetime import datetime
import potato_functions
from potato_functions import database_filename

all_potatoes = []
try:
    all_potatoes = potato_functions.load_potatoes(database_filename)
except:
    pass

TOKEN = config("TOKEN")
CLIENT_SECRET = config("CLIENT_SECRET")
REDIRECT_URI = config("REDIRECT_URI")
OAUTH_URL = config("OAUTH_URL").format(REDIRECT_URI)

app = Flask(__name__)
app.config["SECRET_KEY"] = config("SECRET_KEY")
client = APIClient(TOKEN, client_secret=CLIENT_SECRET)




@app.route('/')
def hello_world():
    return 'go to /potato_bot'


@app.route('/potato_bot', methods=["GET"])
def home():
    if 'token' in session:
        bearer_client = APIClient(session.get('token'), bearer=True)
        current_user = bearer_client.users.get_current_user()
        user_id = current_user.id
        potatoes = potato_functions.read_potatoes_by_discord_id(all_potatoes, user_id)
        return render_template('index.html', current_user=current_user, potatoes=potatoes)
    return render_template('index.html', oauth_uri=OAUTH_URL)


@app.route('/oauth/callback')
def login():
    code = request.args['code']
    access_token = client.oauth.get_access_token(code, REDIRECT_URI).access_token
    session['token'] = access_token
    return redirect("/potato_bot")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/potato_bot')


@app.route('/potato_bot/create', methods=["GET", "POST"])
def create():
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    user_id = current_user.id
    return redirect('/potato_bot')


@app.route('/potato_bot/delete', methods=["GET"])
def delete():
    global all_potatoes
    bearer_client = APIClient(session.get('token'), bearer=True)
    current_user = bearer_client.users.get_current_user()
    user_id = current_user.id
    potato_date = request.args.get('date')
    potatoes_to_delete = potato_functions.find_potato(potato_date, user_id, all_potatoes)
    all_potatoes = potato_functions.delete_potato(potatoes_to_delete, all_potatoes)
    potato_functions.save_potatoes(all_potatoes, potato_functions.database_filename)
    return redirect('/potato_bot')





if __name__ == '__main__':
    app.run(host='0.0.0.0')
