import requests
import pprint
import json
import pandas as pd
import time
import numpy as np
dota_heroes_file = open(r"C:\Users\97252\Desktop\Dota analysis\heroes.json", "r") ## Should be adjusted to pull directly from git
dota_heroes = json.load(dota_heroes_file)
dota_heroes_file.close()

def get_hero_by_id(json_f, id):
    '''
    Returns hero's name by id.
            Parameters:
                    json_f (dict): A json file containing the correlation between hero name and hero id
                    id (int): The hero's id.
    '''
    for hero in json_f["result"]["heroes"]:
        if hero["id"] == id:
            return hero["name"]

def isRadiant(json_players, player_slot):
    '''
    Returns True or False depending a selected player has played for the Radiant team.
            Parameters:
                    json_players (dict): The player segment in the match json.
                    player_slot (int): The player's id in a given match.
    '''
    for player in json_players:
        if player['player_slot'] == player_slot:
            return player['isRadiant']

def get_first_pick_hero(match_id, team_id):
    '''
    Returns the hero's name that was first picked in the draft phase for the wanted team, if the opposing team had first pick, returns that as a note.
            Parameters:
                    match_id (int): The match id.
                    team_id (int): The team id.
    ''' 
    match_req = requests.get("https://api.opendota.com/api/matches/" + str(match_id))
    match_json = json.loads(match_req.text)
    drafts = match_json['draft_timings']
    for phase in drafts:
        if phase["pick"] == True: ##iterating over the draft phase until the first pick.       
            if isRadiant(match_json['players'], phase['player_slot']) == True:
                if match_json["radiant_team"]["team_id"] == team_id:
                    if get_hero_by_id(dota_heroes, phase["hero_id"]) == None:
                        return None
                    return get_hero_by_id(dota_heroes, phase["hero_id"])[14::] #Removing the first 14 character of each name, which is "npc_dota_hero_"
                else: return "opposing team had first pick"   
            break

def get_team_matches(team_id, num_of_matches):
    '''
    Returns a list of matches for a selected team.
            Parameters:
                    team_id (int): The team id.
                    num_of_matches (int): The number of matches. Note: The number of matches select is the last matches played by default.
    ''' 
    team_req = requests.get("https://api.opendota.com/api/teams/" + str(team_id) + "/matches")
    team_matches = json.loads(team_req.text)
    num_of_matches = 1
    match_id_list = []
    #print(team_matches)
    for i in team_matches:
        num_of_matches += 1
        match_id_list.append(i["match_id"])
        if num_of_matches == 20:
            break
    return match_id_list

def hero_name_cleaner(heroes_list):
    '''
    Returns a list of heroes without "None" or "Opposing team had last pick".
            Parameters:
                    heroes_list (list): The original heroes list that needs to be cleaned.
                    num_of_matches (int): The number of matches. Note: The number of matches select is the last matches played by default.
    '''
    for hero in heroes_list:
        if hero == None:
            heroes_list.remove(hero)
            continue
        if hero.startswith("opp"):
            heroes_list.remove(hero)
    return heroes_list


def main():
    matches_list = get_team_matches(2586976, 10)
    first_pick_heroes = []
    for match in matches_list:
        first_pick_heroes.append(get_first_pick_hero(match, 2586976))
    print(hero_name_cleaner(first_pick_heroes))
if __name__ == "__main__":
    #Only call main() when this file is run directly, ignore if imported
    main()