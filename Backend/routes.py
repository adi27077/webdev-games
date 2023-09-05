import certifi
import gridfs
from bson import ObjectId
from flask import Flask, jsonify, request
from flask_cors import cross_origin
from pymongo.mongo_client import MongoClient

uri = "insert_your_mongodb_uri_here"

# Create a new client and connect to the server
client = MongoClient(uri, tlsCAFile=certifi.where())

database = client["webdev"]
fs = gridfs.GridFS(database)
userCollection = database["users"]
gamesCollection = database["games"]
highscoresCollection = database["scores"]

app = Flask(__name__)


@app.route("/login", methods=["POST"])
@cross_origin(supports_credentials=True)
def login():
    cred = request.get_json()

    user = userCollection.find_one({"username": cred["username"], "password": cred["password"]})

    if user is not None:
        response = jsonify(result="Login successful", username=user["username"])
        response.status_code = 200
    else:
        response = jsonify(result="Invalid username or password")
        response.status_code = 401

    return response


@app.route("/register", methods=["POST"])
@cross_origin(supports_credentials=True)
def register():
    cred = request.get_json()

    user = userCollection.find_one({"username": cred["username"]})

    if user is None:
        userCollection.insert_one(cred)
        response = jsonify(result="Registration successful")
        response.status_code = 201
    else:
        response = jsonify(result="Username already exists")
        response.status_code = 400

    return response


@app.route("/reset_password", methods=["PUT"])
@cross_origin(supports_credentials=True)
def reset_password():
    cred = request.get_json()

    user = userCollection.find_one({"username": cred["username"]})

    if user is not None:
        userCollection.update_one({"username": cred["username"]}, {"$set": {"password": cred["password"]}})
        response = jsonify(result="Password reset successful")
        response.status_code = 200
    else:
        response = jsonify(result="Username not found")
        response.status_code = 400

    return response


@app.route("/games", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_games():
    result = []
    for game in gamesCollection.find():
        result.append({"_id": str(game["_id"]), "title": game["title"], "description": game["description"],
                       "image": str(game["image"])})

    return jsonify(result=result)


@app.route("/images/<image_id>", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_image(image_id):
    try:
        image = fs.get(ObjectId(image_id))
        return image.read()
    except:
        return jsonify(result="Image not found")


@app.route("/scores", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_scores():
    result = []
    for score in highscoresCollection.find():
        result.append({"_id": str(score["_id"]), "game": score["game"], "user": score["user"], "score": score["score"]})

    return jsonify(result=result)


@app.route("/scoresByGame/<game>", methods=["GET"])
@cross_origin(supports_credentials=True)
def get_scores_by_game(game):
    result = []
    for score in highscoresCollection.find({"game": game}):
        result.append({"_id": str(score["_id"]), "game": score["game"], "user": score["user"], "score": score["score"]})

    return jsonify(result=result)


@app.route("/scores", methods=["POST", "PUT"])
@cross_origin(supports_credentials=True)
def add_score():
    req_dict = request.get_json()

    data = {
        "game": req_dict["game"],
        "user": req_dict["user"],
        "score": req_dict["score"]
    }

    if request.method == "POST":
        requested_id = highscoresCollection.insert_one(data).inserted_id
        return jsonify(result="Score added successfully", id=str(requested_id))
    elif request.method == "PUT":
        requested_id = highscoresCollection.update_one({"user": data["user"], "game": data["game"]},
                                                       {"$set": data}).upserted_id
        return jsonify(result="Score updated successfully", id=str(requested_id))


if __name__ == "__main__":
    app.run(debug=True)
