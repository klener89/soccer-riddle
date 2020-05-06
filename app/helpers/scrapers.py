import requests
import random

from bs4 import BeautifulSoup
import re
from app import db
from app.models import User, Player

################
famous_players = [
    "lionel-messi", "cristiano-ronaldo", "andres-iniesta", "zlatan-ibrahimovic", "neymar", 
    "wayne-rooney", "robin-van-persie", "cesc-fabregas", "gerard-pique", 
    "juan-mata", "leroy-sane", "kylian-mbappe", "erling-haaland", "lautaro-martinez", "kevin-de-bruyne"
]

positions_choices = {
    "Goalkeeper" : "GK",
    "Sweeper": "SW",
    "CentreBack": "CB",
    "LeftBack": "LB",
    "RightBack": "RB",
    "DefensiveMidfield": "DM",
    "CentralMidfield": "CM",
    "RightMidfield": "RM",
    "LeftMidfield": "LM",
    "AttackingMidfield" : "AM",
    "LeftWinger" : "LW",
    "RightWinger": "RW",
    "SecondStriker":"SS",
    "CentreForward": "CF",
}

user_agent_list = [
    # Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    # Firefox
    "Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)",
    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)",
]

def request_tm(mates=False, search_name=False, player=""):
    # Method to make a transfermarkt request with randomized names and user agents
    # Default is the profile of the player
    if mates:
        base_url = "https://www.transfermarkt.com/%s/gemeinsameSpiele/spieler/%s" % (random.choice(famous_players), player)
    elif search_name:
        base_url = "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query=%s&x=0&y=0" % player
    else:
        base_url = "https://www.transfermarkt.com/%s/profil/spieler/%s" % (random.choice(famous_players), player)
    
    data = requests.get(base_url, headers={'User-Agent': random.choice(user_agent_list)})
    soup = BeautifulSoup(data.text, "html.parser")
    return soup

def find_players(name):
    # search for a player based on his name. returns a list of dicts with the first 10 players found
    response = request_tm(search_name=True, player=name)
    found = response.find('div', {"class":"table-header"},text=re.compile("^Search results for players.*"))
    table = response.find("table", {"class": "items"})
    players = []
    if table and found:
        for row in table.find_all("table", {"class": "inline-table"}):
            player = {}
            
            # Search fields
            pic = row.find("img", {"class": "bilderrahmen-fixed"})
            player_a = row.find("a", {"class": "spielprofil_tooltip"})
            club_a = player_a.find_next('td').find("a")
            position = club_a.find_next('td')
            
            # Club information
            club_img = position.find_next('td').find("img")
            player["club_id"] = club_a["id"]
            player["club_name"] = club_a.text
            player["club_img"] = club_img["src"]

            # Player Information
            age = club_img.find_next('td')
            player["player_id"] = player_a["id"]
            player["img"] = pic["src"]
            player["url"] = player_a["href"]
            player["name"] = player_a["title"]
            if age.text !="-":
                player["age"] = age.text
            else:
                player["age"] = 0
            player["position"] = position.text
            

            # Nationality information
            nationality = age.find_next('td').find('img')
            if nationality is not None:
                player["nationality"] = nationality.get("title","NA")
                player["nationality_img"] = nationality.get("src","")
            else:
                player["nationality"] = "NA"
                player["nationality_img"] = ""
            players.append(player)
    return players

def find_player(player_id):
    # Find the specific player by his player_id. Returns a player dict if the player can be found
    # Assumtions: the player_id is correct and player can be found on tm.com
    
    # Check if player in db, and use that if so
    player = db.session.query(Player).filter(Player.player_id == player_id).first()
    if player:
        player = player.__dict__
    else:
        player = {}
        response = request_tm(player=str(player_id))
        player["player_id"] = player_id

        # Club information
        club_a = response.find('th', text=re.compile("Current club:*")).findNext('td').find('a')
        player["club_id"] = club_a["id"]
        club_img = club_a.find("img")
        player["club"] = club_img["alt"]
        player["club_img"] = club_img["src"]

        # Player information
        pic = response.find("meta", {"property": "og:image"})
        player["img"] = pic["content"]
        meta_name = response.find("meta", {"property": "og:title"})
        player["name"] = meta_name["content"].split(" - ", 1)[0]
        meta_url = response.find("meta", {"property": "og:url"})
        player["url"] = meta_url["content"].replace("http://www.transfermarkt.com", "")
        position = response.find('span', text=re.compile("Position:*")).findNext('span').text
        position_clean = re.sub('\W+','', position)
        player["position"] = positions_choices.get(position_clean,"")
        age = response.find('th', text=re.compile("Age*")).findNext('td').text
        player["age"] = age

        # Nationality information
        nationality = response.find('th', text=re.compile("Citizenship*")).findNext('td').find('img')
        player["nationality"] = nationality["title"]
        player["nationality_img"] = nationality["src"]

    return player

def find_mates(player_id):
    # Find all team mates of player by player_id
    response = request_tm(mates=True, player=str(player_id))
    select = response.find('select', {'name':'gegner'})
    mates = []
    # use the select field entries to extract all from first page
    for row in select.find_all("option"):
        if not row["value"] == "0":
            mates.append(dict(id=int(row["value"]), name=row.text))
    return mates

def add_player(player):
    # add a player to the database
    if (not db.session.query(Player).filter(Player.player_id == player["player_id"]).first()):
        db.session.add(
            Player(
                player_id=player["player_id"],
                name=player["name"],
                club_id=player["club_id"],
                club=player["club"],
                club_img=player["club_img"],
                img=player["img"],
                url=player["url"],
                age=player["age"],
                position=player["position"],
                nationality=player["nationality"],
                nationality_img=player["nationality_img"],
            )
        )
        db.session.flush()
    return player
