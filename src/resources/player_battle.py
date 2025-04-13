from flask_restful import Resource
from flask import jsonify
import requests
import urllib.parse
import os
from dotenv import load_dotenv
from db import get_mongo_client

load_dotenv()

class PlayerBattle(Resource):
    def get(self, player_tag):
        encoded_tag = urllib.parse.quote(f"#{player_tag}")
        url = f"https://api.clashroyale.com/v1/players/{encoded_tag}/battlelog"

        token = os.getenv("CLASH_ROYALE_API_TOKEN")

        if not token:
            return {"error": "Token de API não encontrado. Defina a variável de ambiente CLASH_ROYALE_API_TOKEN."}, 500

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            player_battles = response.json()

            db = get_mongo_client()
            playerbattles_collection = db.playerbattles

            for battle in player_battles:
                battle["playerTag"] = player_tag
                battle_id = battle["battleTime"]
                existing_battle = playerbattles_collection.find_one({"battleTime": battle_id})

                if existing_battle:
                    playerbattles_collection.update_one({"battleTime": battle_id}, {"$set": battle})
                else:
                    playerbattles_collection.insert_one(battle)
            for battle in player_battles:
                battle["_id"] = str(battle["_id"])
            return jsonify(player_battles)
        else:
            return {"error": f"Falha na requisição. Status code: {response.status_code}"}, response.status_code
