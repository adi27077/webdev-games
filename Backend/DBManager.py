from pymongo.mongo_client import MongoClient
import certifi
import gridfs

uri = "insert_your_mongodb_uri_here"

# Create a new client and connect to the server
client = MongoClient(uri, tlsCAFile=certifi.where())

database = client["webdev"]
fs = gridfs.GridFS(database)

userCollection = database["users"]
userList = [
    {"username": "spiderman99", "password": "123456"},
    {"username": "princessLEIA", "password": "123456"},
    {"username": "geraltOfRivia", "password": "123456"},
    {"username": "ezio_auditore", "password": "123456"},
    {"username": "nathan_drake99", "password": "123456"}
]
userIDs = userCollection.insert_many(userList)

print(userIDs.inserted_ids)

gamesCollection = database["games"]
gameList = [
    {"title": "Endless Runner",
     "description": "How long can you survive in this endless runner? Can you beat the high-scores of other players?",
     "image": ""},
    {"title": "Balloon Madness",
     "description": "Try beat your friends high-scores by shooting as many balloons as possible before the time runs out!",
     "image": ""},
    {"title": "Chicken Invaders",
     "description": "The chickens are invading! Can you save the world from the chicken menace?",
     "image": ""},
    {"title": "Flappy Bird",
     "description": "Flap your wings and fly through the pipes! How far can you go?",
     "image": ""}
]

try:
    file1 = open("runner.png", "rb")
    content1 = file1.read()
    out1 = fs.put(content1, filename="runner.png")
    gameList[0]["image"] = out1
except:
    print("Error uploading image")

try:
    file2 = open("balloon.jpg", "rb")
    content2 = file2.read()
    out2 = fs.put(content2, filename="balloon.jpg")
    gameList[1]["image"] = out2
except:
    print("Error uploading image")

try:
    file3 = open("chickeninvaders.jpg", "rb")
    content3 = file3.read()
    out3 = fs.put(content3, filename="chicken.jpg")
    gameList[2]["image"] = out3
except:
    print("Error uploading image")

try:
    file4 = open("flappybird.png", "rb")
    content4 = file4.read()
    out4 = fs.put(content4, filename="flappybird.png")
    gameList[3]["image"] = out4
except:
    print("Error uploading image")

gameIDs = gamesCollection.insert_many(gameList)
print(gameIDs.inserted_ids)

highscoresCollection = database["scores"]
highscoresList = [
    {"game": "Balloon Madness", "user": "spiderman99", "score": 67},
    {"game": "Endless Runner", "user": "spiderman99", "score": 55},
    {"game": "Endless Runner", "user": "princessLEIA", "score": 109},
    {"game": "Balloon Madness", "user": "geraltOfRivia", "score": 73},
    {"game": "Balloon Madness", "user": "ezio_auditore", "score": 45},
    {"game": "Endless Runner", "user": "nathan_drake99", "score": 77},
    {"game": "Chicken Invaders", "user": "spiderman99", "score": 100},
    {"game": "Chicken Invaders", "user": "princessLEIA", "score": 50},
    {"game": "Chicken Invaders", "user": "geraltOfRivia", "score": 150},
    {"game": "Flappy Bird", "user": "spiderman99", "score": 10},
    {"game": "Flappy Bird", "user": "princessLEIA", "score": 20},
    {"game": "Flappy Bird", "user": "ezio_auditore", "score": 30},
]

scoresIDs = highscoresCollection.insert_many(highscoresList)
print(scoresIDs.inserted_ids)

# try:
#     file = open("balloon.jpg", "rb")
#     content = file.read()
#     out = fs.put(content, filename="balloon.jpg")
#     print(out)
#     try:
#         out2 = fs.get(out)
#         file2 = open("balloon2.jpg", "wb")
#         byteArray = out2.read()
#         file2.write(byteArray)
#     except:
#         print("Error downlaoding image")
# except:
#     print("Error uploading image")
