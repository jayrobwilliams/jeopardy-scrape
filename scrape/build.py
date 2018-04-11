import pg
from genderize import Genderize
import geocoder
import json

with open('../credentials/keys.json') as key_file:
    keys = json.load(key_file)

def get_sex(name):
    return Genderize().get([name])

def games(cur, data):
    pg.insert(cur, "Games", [(data["id"], data["air_date"], data["season"], data["show_number"], data["before_double"])])

def contestants(cur, data, game_id):
    contestants = []
    game_contestants = []
    for i in data:
        sex = None
        probability = None
        lat = None
        lng = None
        if(i["first_name"]):
            sex_data = get_sex(i["first_name"])[0]
            sex = sex_data["gender"]
            probability = sex_data["probability"]
        if(i["home_town"]):
            geo = geocoder.google(location=i["home_town"], key=keys["gmaps_api_key"])
            lat, lng = geo.latlng
            # lng = geo["latlng"][1]
        contestants.append((i["id"], i["first_name"], i["last_name"], i["profession"], i["home_town"], sex, probability, lat, lng))
        game_contestants.append((game_id, i["id"], i["game_status"]["winner"], i["game_status"]["jeopardy_total"], i["game_status"]["double_jeopardy_total"], i["game_status"]["final_jeopardy_total"], i["game_status"]["final_jeopardy_wager"]))
    pg.insert_once(cur, "Contestants", contestants)
    pg.insert(cur, "GameContestants", game_contestants)

def clues(cur, data, category_id):
    clues = []
    rights = []
    wrongs = []
    for i in data:
        clues.append((i["id"], category_id, i["clue"], i["value"], i["answer"], i["daily_double"], i["daily_double_wager"], i["triple_stumper"]))
        for j in xrange(len(i["rights"])):
            rights.append((i["id"], i["rights"][j]))
        for k in xrange(len(i["wrongs"])):
            wrongs.append((i["id"], i["wrongs"][k]))
    pg.insert(cur, "Clues", clues)
    pg.insert(cur, "ClueRights", rights)
    pg.insert(cur, "ClueWrongs", wrongs)

def categories(cur, data, game_id, round_id):
    categories = []
    for i in data:
        categories.append((i["id"], game_id, round_id, i["name"]))
    pg.insert(cur, "Categories", categories)
    for i in data:
        clues(cur, i["clues"], i["id"])

def rounds(cur, data, game_id):
    rounds = []
    for i in data:
        categories(cur, i["categories"], game_id, i["id"])
