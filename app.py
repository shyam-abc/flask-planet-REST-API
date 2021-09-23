from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, Column, Integer, String, Float
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from flask_mail import Mail, Message
import os

app = Flask(__name__)
mail = Mail()
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'planets.db')
app.config["JWT_SECRET_KEY"] = "its-my-super-secret"
'''
app.config['MAIL_SERVER'] = 'smtp.mailtrap.io'
app.config['MAIL_USERNAME'] = os.environ['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.environ['MAIL_PASSWORD']
'''

jwt = JWTManager(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.cli.command('db_create')
def db_create():
    db.create_all()
    print("Database created successfully")

@app.cli.command('db_drop')
def db_drop():
    db.drop_all()
    print("Database dropped successfully")

@app.cli.command('db_seed')
def db_seed():
    mercury = Planet(p_name="Mercury", p_type="Class D", home_star="Sol", mass=3.285e23, radius=2439, distance=4.8e6)
    mars = Planet(p_name="Mars", p_type="Class T", home_star="Sol", mass=6.39e23, radius=3389, distance=2.27e9)
    jupiter = Planet(p_name="Jupiter", p_type="Class G", home_star="Sol", mass=1.898e27, radius=69991, distance=7.45e11)
    db.session.add(mercury)
    db.session.add(mars)
    db.session.add(jupiter)

    user1 = User(f_name="Ramesh", l_name="Chennithala", email="ramesh.chenni@gmail.com", password="ramesh")
    db.session.add(user1)
    db.session.commit()
    print("Database seeded successfully")


@app.route('/')
def simple():
    return jsonify(message='Hello, Welcome to the Planetary API'), 200


@app.route('/planets', methods=['GET'])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)

@app.route('/register', methods=['POST'])
def register():
    email = request.form['email']
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists.'), 409
    else:
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        password = request.form['password']
        user = User(f_name=f_name, l_name=l_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully."), 201


@app.route('/login', methods=['POST'])
def login():
    if request.is_json:
        email = request.json['email']
        password = request.json['password']
    else:
        email = request.form['email']
        password = request.form['password']
    test = User.query.filter_by(email=email,password=password).first()
    if test:
        access_token = create_access_token(identity=email)
        return jsonify(message="Login successful", access_token=access_token)
    else:
        return jsonify(message="Login Unsuccessful"), 401


@app.route('/read_planet/<int:p_id>', methods=['GET'])
def read_planet(p_id: int):
    planet = Planet.query.filter_by(p_id=p_id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message="Planet details not found"),404

@app.route('/add_planet',methods=['POST'])
@jwt_required
def add_planet():
    p_name = request.form['p_name']
    test = Planet.query.filter_by(p_name=p_name).first()
    if test:
        return jsonify(message="Planet Exists"), 409
    else:
        p_type = request.form['p_type']
        home_star = request.form['home_star']
        mass = float(request.form['mass'])
        distance = float(request.form['distance'])
        radius = float(request.form['radius'])
        new_planet = Planet(p_name=p_name,p_type=p_type, home_star=home_star, mass=mass, distance=distance, radius=radius)
        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message="New planet added"), 201

@jwt_required
@app.route('/update_planet', methods=['PUT'])
def update_planet():
    p_id = int(request.form['p_id'])
    planet = Planet.query.filter_by(p_id=p_id).first()
    if planet:
        planet.p_name = request.form['p_name']
        planet.p_type = request.form['p_type']
        planet.home_star = request.form['home_star']
        planet.mass = float(request.form['mass'])
        planet.radius = float(request.form['radius'])
        planet.distance = float(request.form['distance'])
        db.session.commit()
        return jsonify(message="Updated successfully"), 202
    else:
        return jsonify(message="Planet details not found"), 404

@jwt_required
@app.route('/delete_planet/<int:p_id>', methods=['DELETE'])
def delete_planet(p_id: int):
    planet = Planet.query.filter_by(p_id=p_id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message="Planet deleted"), 202
    else:
        return jsonify(message="Planet does not exist"), 404
'''
@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    if age < 18:
        return jsonify(message="Access Not Allowed "+name), 401
    else:
        return jsonify(message="Welcome "+name), 200

@app.route('/url_variables/<string:name>/<int:age>')
def url_variables(name: str,age: int):
    if age < 18:
        return jsonify(message="Access Not Allowed "+name), 401
    else:
        return jsonify(message="Welcome "+name), 200

@app.route('/retrieve_password/<string:email>', methods=['GET'])
def retrieve_password(email: str):
    user = User.query.filter_by(email=email).first()
    if user:
        msg = Message("Your API password is " + user.password,
                      sender="me@gmail.com",
                      recipients=[email])
        mail.send(msg)
        return jsonify(message="Password sent to " + email)
    else:
        return jsonify(message="That email doesn't exist"), 401
'''

class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    f_name = Column(String)
    l_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Planet(db.Model):
    __tablename__ = 'planets'
    p_id = Column(Integer, primary_key=True)
    p_name = Column(String)
    p_type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id","f_name","l_name","email","password")

class PlanetSchema(ma.Schema):
    class Meta:
        fields = ("p_id","p_name","p_type","home_star","mass","radius","distance")

user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

if __name__ == '__main__':
    app.run(debug=True)
