import pg
import json

with open('../credentials/keys.json') as key_file:
    keys = json.load(key_file)

def games(cur, data):
    res = pg.insert_no_duplicate(cur, "games", [(data["id"], data["air_date"], data["season"], data["show_number"], data["before_double"], data["contained_tiebreaker"], data["all_star_game"], data["no_winner"], data["unknown_winner"])])
    if(len(res) > 0):
        return True
    else:
        return False

def contestants(cur, data, game_id):
    contestants = []
    game_contestants = []
    for i in data:
        contestants.append((i["id"], i["first_name"], i["last_name"], i["profession"], i["home_town"]))
        game_contestants.append((game_id, i["id"], i["game_status"]["position"], i["game_status"]["winner"], i["game_status"]["jeopardy_total"], i["game_status"]["double_jeopardy_total"], i["game_status"]["final_jeopardy_total"], i["game_status"]["final_jeopardy_wager"]))
    pg.insert_once(cur, "contestants", contestants)
    pg.insert(cur, "game_contestants", game_contestants)

def clues(cur, data, category_id):
    clues = []
    rights = []
    wrongs = []
    for i in data:
        clues.append((i["id"], category_id, i["clue"], i["value"], i["answer"], i["daily_double"], i["daily_double_wager"], i["triple_stumper"], None))
        for j in range(len(i["rights"])):
            rights.append((i["id"], i["rights"][j]))
        for k in range(len(i["wrongs"])):
            wrongs.append((i["id"], i["wrongs"][k]))
    pg.insert(cur, "clues", clues)
    pg.insert(cur, "clue_rights", rights)
    pg.insert(cur, "clue_wrongs", wrongs)

def categories(cur, data, game_id, round_id):
    categories = []
    for i in data:
        categories.append((i["id"], game_id, round_id, i["name"]))
    pg.insert(cur, "categories", categories)
    for i in data:
        clues(cur, i["clues"], i["id"])

def rounds(cur, data, game_id):
    for i in data:
        categories(cur, i["categories"], game_id, i["id"])
