import random

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


## HTTP GET - Read Record
@app.route("/all")
def get_all_cafes():
    return jsonify(cafes=[cafe.to_dict() for cafe in db.session.query(Cafe).all()])


@app.route("/search")
def get_cafe_at_location():
    cafe_location = request.args["loc"]
    cafes_near_location = db.session.query(Cafe).filter_by(location=cafe_location).all()
    if cafes_near_location:
        return jsonify(cafes=[cafe.to_dict() for cafe in cafes_near_location])
    else:
        return jsonify(error={
            "Not Found": "Sorry, we don't have a cafe at that location."
        })


@app.route("/random")
def get_random_cafe():
    random_cafe = random.choice(db.session.query(Cafe).all())
    return jsonify(cafe=random_cafe.to_dict())


## HTTP POST - Create Record
@app.route("/add", methods=["POST", "GET"])
def add_cafe():
    new_cafe = Cafe(
        name=request.form.get("name"),
        map_url=request.form.get("map_url"),
        img_url=request.form.get("img_url"),
        location=request.form.get("location"),
        seats=request.form.get("seats"),
        has_toilet=bool(request.form.get("has_toilet")),
        has_wifi=bool(request.form.get("has_wifi")),
        has_sockets=bool(request.form.get("has_sockets")),
        can_take_calls=bool(request.form.get("can_take_calls")),
        coffee_price=request.form.get("coffee_price"),
    )
    db.session.add(new_cafe)
    db.session.commit()
    return jsonify(response={
        "succes": "Successfully added the new cafe."
    })


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=["PATCH"])
def update_coffee_price(cafe_id):
    new_price = request.args.get("new_price")
    cafe_to_update = db.session.get(Cafe, cafe_id)
    if cafe_to_update:
        cafe_to_update.coffee_price = new_price
        db.session.commit()
        return jsonify(success="Successfully updated the price.")
    else:
        return jsonify(error={
            "Not Found": "Sorry, a cafe with that id was not found in the database."
        })


## HTTP DELETE - Delete Record
@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    if request.args.get("api-key") == "TopSecretAPIKey":
        cafe_to_delete = db.session.get(Cafe, cafe_id)
        if cafe_to_delete:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(success="Successfully deleted the cafe."), 200
        else:
            return jsonify(error={
                "Not Found": "Sorry, a cafe with that id was not found in the database."
            }), 404
    else:
        return jsonify(error="Sorry, that's not allowed. Make sure you have the correct api_key"), 403


if __name__ == '__main__':
    app.run(debug=True)
