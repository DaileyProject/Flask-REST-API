from flask_restful import Resource, reqparse
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token, create_refresh_token,jwt_required
from models.user import UserModel

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username',
					type=str,
					required=True,
					help='This field cannot be blank'
				)
_user_parser.add_argument('password',
					type=str,
					required=True,
					help='This field cannot be blank'
				)


class UserRegister(Resource):
	def post(self):
		data = _user_parser.parse_args()
		if UserModel.find_by_username(data['username']):
			return {'error': 'This username already exists'}, 400

		user = UserModel(**data)
		user.save_to_db()

		return {"message": "User created successfully"}, 201

class User(Resource):
	@jwt_required
	def delete(self, username):
		store = UserModel.find_by_username(username)
		if store:
			store.delete_from_db()
			return {'message': 'User deleted successfully'}, 200
		return {'message': 'User does not exist'}, 404


class UserList(Resource):
	@jwt_required
	def get(self):
		return {'users': [user.json() for user in UserModel.find_all()]}

class UserAuth(Resource):
	@classmethod
	def post(cls):
		data = _user_parser.parse_args()
		user = UserModel.find_by_username(data['username'])

		if user and safe_str_cmp(user.password, data['password']):
			access_token = create_access_token(identity=user.id, fresh=True)
			refresh_token = create_refresh_token(user.id)
			return {
				'access_token': access_token,
				'refresh_token': refresh_token
			}, 200

		return {'message': 'Invalid credentials'}, 404
