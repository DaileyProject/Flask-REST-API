import os

from flask import Flask
from flask_restful import Api
from flask_jwt_extended import JWTManager

from resources.user import UserRegister, UserList, User, UserAuth
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from models.user import UserModel

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_SECRET_KEY'] = "234uhfaf8923hfvaor2@r34jfa4#v234j!"
api = Api(app)

jwt = JWTManager(app)

@jwt.user_claims_loader
def add_claims_to_jwt(identity):
	check_identity = UserModel.find_by_id(identity).json()
	if check_identity['permissions'] == "admin":
		return {'is_admin': True}
	return {'is_admin': False}

api.add_resource(Item, '/item/<string:name>')
api.add_resource(ItemList, '/items')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(UserList, '/users')
api.add_resource(User, '/users/<string:username>')
api.add_resource(UserRegister, '/register')
api.add_resource(UserAuth, '/auth')


if __name__ == '__main__':
	from db import db
	db.init_app(app)
	app.run(port=5000, debug=True)
