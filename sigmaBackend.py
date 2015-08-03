from flask import Flask, jsonify, make_response, abort, request, redirect, url_for, get_flashed_messages, render_template
from flask_security.forms import RegisterForm
from wtforms import Form, BooleanField, StringField, validators
from flask.ext.mongoengine import MongoEngine
from flask.ext.security import Security, MongoEngineUserDatastore, \
    UserMixin, RoleMixin, login_required, roles_required
from flask.ext.login import LoginManager, UserMixin, current_user, login_user, logout_user
from flask_security.forms import RegisterForm
from pymongo import MongoClient
from sigmaDataClasses import SigmaClient, ActiveClients
from flask.ext.security.utils import encrypt_password, verify_password
import datetime
import random
import string



#############################
### Sigma Application API ###
#############################

app = Flask(__name__)

# Security Config
app.config['SECRET_KEY'] = 'super-secret'
app.config['SECURITY_PASSWORD_HASH'] = 'sha512_crypt'
app.config['SECURITY_PASSWORD_SALT'] = 'sigmaSports'
app.config['SECURITY_REGISTER_URL'] = '/create_account'

# MongoDB Config
app.config['MONGODB_DB'] = 'sigma_database'
app.config['MONGODB_HOST'] = 'localhost'
app.config['MONGODB_PORT'] = 27017

# Mail Config
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

# Login/Logout Config
app.config['SECURITY_POST_LOGOUT_VIEW'] = '/login'

# Create database connection object
db = MongoEngine(app)

# Registration criteria
class Role(db.Document, RoleMixin):
	name = db.StringField(max_length=80, unique=True)
	description = db.StringField(max_length=255)

	def __str__(self):
	    return self.name

	def __hash__(self):
	    return hash(self.name)

class User(db.Document, UserMixin):
	email = db.StringField(max_length=255)
	password = db.StringField(max_length=255)
	active = db.BooleanField(default=True)
	confirmed_at = db.DateTimeField(default=None)
	roles = db.ListField(db.ReferenceField(Role), default=[])
	team = db.StringField(max_length=50)
	username = db.StringField(max_length=50)

# Open Data Clients
activeSigmaClients = ActiveClients()

activeMongoClients = ActiveClients()

# Setup Flask-Security
user_datastore = MongoEngineUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Create a user to test with
@app.before_first_request
def create_user():
	user_datastore.find_or_create_role(name='admin', description='Administrator')
	
	user_datastore.create_user(email='arjungupta291@gmail.com', 
		username='aj', password=encrypt_password('sigma'), team='sigmasports')

	user_datastore.add_role_to_user('arjungupta291@gmail.com', 'admin')

@app.route('/create_account', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        team = request.form['team']
        user_datastore.create_user(email=email, username=username, password=encrypt_password(password), team=team)
        user = User(username, email, password, team)
        login_user(user)
        return "User Created and logged in!"
    else:
        return render_template('/security/register_user.html')

@app.route('/hello')
@login_required
def hello():
	return "hello " + current_user.username

@app.route('/view_users')
@login_required
@roles_required('admin')
def view():
	client = MongoClient('localhost:27017')
	db = client.sigma_database
	users = []
	result = list(db.user.find())
	for item in result:
		users.append(item["email"])
	client.close()
	return str(users)

### app_type refers to "realtime" or "database" to open relevant client ###
@app.route('/<string:username>/<string:app_type>/start_session')
@login_required
def openSigmaClient(username,app_type):
	if app_type == 'realtime':
		activeSigmaClients.newClient(username, 'realtime')
		return "New SigmaClient Session Started"
	elif app_type == 'database':
		activeMongoClients.newClient(username, 'database')
		return "New Database Session Started"

@app.route('/<string:username>/<string:app_type>/tags/coordinates', methods = ['GET'])
@login_required
def getTagCoordinates(username,app_type):
	if app_type == 'realtime':
		while True:
			try:
				result = activeSigmaClients.clients[username].listTags()
				break
			except KeyError:
				return "No open SigmaClient Connection Detected.\nNeed to login first."
		return jsonify({"result": result})
	else:
		return abort(400)

@app.route('/<string:username>/<string:app_type>/end_session')
@login_required
def closeSigmaclient(username,app_type):
	if app_type == 'realtime':
		activeSigmaClients.endSession(username, 'realtime')
		return """SigmaClient Session Closed\nList of open SigmaClients: {}\nGoodbye!\n""".format(activeSigmaClients.clients)
	elif app_type == 'database':
		activeMongoClients.endSession(username, 'database')
		return """MongoClient Session Closed\nList of open MongoClients: {}\nGoodbye!\n""".format(activeMongoClients.clients)


@app.errorhandler(404)
def not_found(error):
	return make_response(jsonify({'error': 'Not Found'}), 404)

@app.errorhandler(400)
def bad_request(error):
	return make_response(jsonify({'error': 'Bad Request'}), 400)

if __name__ == '__main__':
	app.run(debug = True)





