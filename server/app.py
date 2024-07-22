#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db, render_as_batch=True)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

@app.route('/restaurants', methods=['GET'])
def restaurants():
        restaurants = []
        for restaurant in Restaurant.query.all():
            restaurant_dict={
                'id':restaurant.id,
                'name':restaurant.name,
                'address':restaurant.address
            }
            restaurants.append(restaurant_dict)
            response= make_response(
                jsonify(restaurants),
                200
                 )
        return response
    
@app.route('/restaurants/<int:id>', methods=['GET'])
def get_restaurants_id(id):
    restaurant = Restaurant.query.filter(Restaurant.id == id).first()
    if restaurant:
       restaurant_dict = {
            'id': restaurant.id,
            'name': restaurant.name,
            'address': restaurant.address,
            'restaurant_pizzas': [
                {
                    'id': restaurant_pizza.id,
                    'restaurant_id': restaurant_pizza.restaurant_id,
                    'pizza_id': restaurant_pizza.pizza_id,
                    'price': restaurant_pizza.price,
                    'pizza': {
                        'id': restaurant_pizza.pizza.id,
                        'name': restaurant_pizza.pizza.name,
                        'ingredients': restaurant_pizza.pizza.ingredients
                    }
                }
                for restaurant_pizza in restaurant.pizzas
            ]
        }
       response= make_response(
        jsonify(restaurant_dict),
        200
        )
       return response
    
    else:
        response= make_response(
            jsonify({'error': 'Restaurant not found'}),
            404
        )
    return response
@app.route('/restaurant_pizzas',methods=['POST'])
def add_post():
    if request.method == 'POST':
       try:
            restaurants_pizzas= RestaurantPizza(
                 price = request.get_json()["price"],
                 restaurant_id= request.get_json()["restaurant_id"],
                 pizza_id= request.get_json()["pizza_id"]
            )
            db.session.add(restaurants_pizzas)
            db.session.commit()
            response= make_response(restaurants_pizzas.to_dict(),201,{"content-type":"application/json"})
            return response
       except ValueError as e:
            message={"errors":["validation errors"]}
            response= make_response(message,400)
            return response
            

            
@app.route('/restaurants/<int:id>',methods=['DELETE'])
def delete_restaurants(id):
    restaurant = Restaurant.query.filter_by(id=id).first()
    if restaurant:
       RestaurantPizza.query.filter_by(id=id).delete()
       db.session.delete(restaurant)
       db.session.commit()
       response= make_response(
             jsonify({'message': 'Restaurant deleted successfully'}),
             204
            )
       return response
    else:
        response= make_response(
             jsonify({  "error": "Restaurant not found"}),
             404
            )
        return response
@app.route('/pizzas', methods=['GET'])
def get_pizzas():
        pizza_menu=[]
        for pizzas in Pizza.query.all():
            pizza_dict={
                'id':pizzas.id,
                'ingredients': pizzas.ingredients,
                'name': pizzas.name,
            }
            pizza_menu.append(pizza_dict)
            response= make_response(
                jsonify(pizza_menu),
                200
            )
        return response


if __name__ == "__main__":
    app.run(port=5555, debug=True)
