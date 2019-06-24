import os

from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import (
	UserRegister,
	UserList,
	User,
	UserAuth,
	TokenRefresh
)
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from models.user import UserModel
from blacklist import BLACKLIST

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_SECRET_KEY'] = "234uhfaf8923hfvaor2@r34jfa4#v234j!"
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['access', 'refresh']
api = Api(app)

jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
	check_identity = UserModel.find_by_id(identity).json()
	if check_identity['permissions'] == "admin":
		return {'is_admin': True}
	return {'is_admin': False}

@jwt.expired_token_loader
def expired_token_callback():
	return jsonify({
		'description': 'The token has expired',
		'error': 'token_expired'
	}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
	return jsonify({
		'description': 'Signature verification failed',
		'error': 'invalid_token'
	}), 401

@jwt.unauthorized_loader
def unauthorized_callback(error):
	return jsonify({
		'description': 'Request does not contain an access token',
		'error': 'authorization_required'
	}), 401

@jwt.needs_fresh_token_loader
def token_not_fresh_callback():
	return jsonify({
		'description': 'The token is not fresh, please refresh your token',
		'error': 'fresh_token_required'
	}), 401

@jwt.revoked_token_loader
def revoked_token_callback():
	return jsonify({
		'description': 'The token as been revoked, please create a new token',
		'error': 'token_revoked'
	}), 401

@jwt.token_in_blacklist_loader
def check_blacklist(decrypted_token):
	return decrypted_token['identity'] in BLACKLIST

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<string:username>')
api.add_resource(UserRegister, '/register')
api.add_resource(UserAuth, '/auth')
api.add_resource(TokenRefresh, '/refresh')


if __name__ == '__main__':
	from db import db
	db.init_app(app)
	app.run(port=5000, debug=True)
