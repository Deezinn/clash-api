from flask_restful import Api
from resources.player import Player
from resources.player_battle import PlayerBattle

def initialize_routes(app):
    api = Api(app)

    api.add_resource(Player, '/player/<string:player_tag>')
    api.add_resource(PlayerBattle, '/playerBattle/<string:player_tag>')

    return api
