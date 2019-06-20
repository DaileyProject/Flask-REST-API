from flask_restful import Resource, reqparse
from models.user import UserModel

class UserRegister(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument('username',
		type=str,
		required=True,
		help='This field cannot be blank'
	)
	parser.add_argument('password',
		type=str,
		required=True,
		help='This field cannot be blank'
	)

	def post(self):
		data = UserRegister.parser.parse_args()
		if UserModel.find_by_username(data['username']):
			return {'error': 'This username already exists'}, 400

		user = UserModel(**data)
		user.save_to_db()

		return {"message": "User created successfully"}, 201

class User(Resource):
	parser = reqparse.RequestParser()
	parser.add_argument('username',
		type=str,
		required=True,
		help='Username is required'
	)

	def delete(self, username):
		data = User.parser.parse_args()
		user = UserModel.find_by_username(*data)
		if user:
			user.delete_from_db(username)
			return {'message': 'User deleted successfully'}
		return {'message': 'User does not exist'}



class UserList(Resource):
	def get(self):
		return {'users': [user.json() for user in UserModel.find_all()]}
