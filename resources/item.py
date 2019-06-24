from flask_restful import Resource, reqparse
from flask_jwt_extended import (
	create_access_token,
	create_refresh_token,
	jwt_required,
	jwt_refresh_token_required,
	get_jwt_identity,
    fresh_jwt_required
)
from models.item import ItemModel

class Item(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('price',
        type=float,
        required=True,
        help='This field cannot be left blank'
    )
    parser.add_argument('store_id',
        type=int,
        required=True,
        help='Every item needs a store id'
    )

    @fresh_jwt_required
    def get(self, name):
        try:
            item = ItemModel.find_by_name(name)
        except:
            return {'message': 'An internal error has occurred.'}, 500

        if item:
            return item.json()
        return {'message': 'Item not found'}, 404

    @fresh_jwt_required
    def post(self, name):
        if ItemModel.find_by_name(name):
            return {"error": "Item '{}' already exists".format(name)}, 400

        data = Item.parser.parse_args()
        item = ItemModel(name, data['price'], data['store_id'])
        try:
            item.save_to_db()
        except:
            return {'message': 'An error occurred inserting the item.'}, 500

        return item.json(), 201

    @fresh_jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {'message': 'User must be admin to delete items'}, 404
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {'message': 'Item deleted.'}, 200
        return {'message': 'Item does not exist.'}, 404

    @fresh_jwt_required
    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)

        if item:
            item.price = data['price']
        else:
            item = ItemModel(name, **data)

        item.save_to_db()
        return item.json()


class ItemList(Resource):
    @fresh_jwt_required
    def get(self):
        return {'items': [item.json() for item in ItemModel.find_all()]}
