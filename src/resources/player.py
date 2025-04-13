from flask_restful import Resource
from flask import jsonify
import requests
import urllib.parse
import os
from dotenv import load_dotenv
from db import get_mongo_client

load_dotenv()

class Player(Resource):
    def get(self, player_tag):
        encoded_tag = urllib.parse.quote(f"#{player_tag}")
        url = f"https://api.clashroyale.com/v1/players/{encoded_tag}"

        token = os.getenv("CLASH_ROYALE_API_TOKEN")

        if not token:
            return {"error": "Token de API não encontrado. Defina a variável de ambiente CLASH_ROYALE_API_TOKEN."}, 500

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            player_data = response.json()

            db = get_mongo_client()
            players_collection = db.players
            existing_player = players_collection.find_one({"playerTag": player_tag})

            if existing_player:
                players_collection.update_one({"playerTag": player_tag}, {"$set": player_data})
            else:
                player_data["playerTag"] = player_tag
                players_collection.insert_one(player_data)

            player_data["_id"] = str(player_data["_id"])

            return jsonify(player_data)
        else:
            return {"error": f"Falha na requisição. Status code: {response.status_code}"}, response.status_code
