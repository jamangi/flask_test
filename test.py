from decouple import config
from flask import Flask, render_template, request, session, redirect
from zenora import APIClient

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


@app.route('/potato_bot')
def home():
    if 'token' in session:
        bearer_client = APIClient(session.get('token'), bearer=True)
        current_user = bearer_client.users.get_current_user()
        return render_template('index.html', current_user=current_user)
    return render_template('index.html', oauth_uri=OAUTH_URL)


@app.route('/oauth/callback')
def callback():
    code = request.args['code']
    access_token = client.oauth.get_access_token(code, REDIRECT_URI).access_token
    session['token'] = access_token
    return redirect("/potato_bot")


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/potato_bot')


if __name__ == '__main__':
    app.run()
