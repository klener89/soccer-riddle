import requests
import random

from bs4 import BeautifulSoup
import re
from app import db
from app.models import User, Player

################

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


def request_tm(url):
    data = requests.get(url, headers={'User-Agent': random.choice(user_agent_list)})
    soup = BeautifulSoup(data.text, "html.parser")
    return soup

def find_player(name):
    url = "https://www.transfermarkt.com/schnellsuche/ergebnis/schnellsuche?query=%s&x=0&y=0" % name
    response = request_tm(url)
    found = response.find('div', {"class":"table-header"},text=re.compile("^Search results for players.*"))
    table = response.find("table", {"class": "items"})
    players = []
    if table and found:
        for row in table.find_all("table", {"class": "inline-table"}):
            player = {}
            pic = row.find("img", {"class": "bilderrahmen-fixed"})
            player_a = row.find("a", {"class": "spielprofil_tooltip"})
            club_a = player_a.find_next('td').find("a")
            position = club_a.find_next('td')
            club_img = position.find_next('td').find("img")
            age = club_img.find_next('td')
            
            nationality = age.find_next('td').find('img')
            
            player["id"] = player_a["id"]
            player["img"] = pic["src"]
            player["url"] = player_a["href"]
            player["name"] = player_a["title"]
            if age.text !="-":
                player["age"] = age.text
            else:
                player["age"] = 0
            player["position"] = position.text
            player["club_id"] = club_a["id"]
            player["club_name"] = club_a.text
            player["club_img"] = club_img["src"]
            if nationality is not None:
                player["nationality"] = nationality.get("title","NA")
                player["nationality_img"] = nationality.get("src","")
            else:
                player["nationality"] = "NA"
                player["nationality_img"] = ""
            players.append(player)
    return players


def find_mates(id):
    base_url = "https://www.transfermarkt.com/miroslav-klose/gemeinsameSpiele/spieler/%d" % id
    response = request_tm(base_url)
    select = response.find('select', {'name':'gegner'})
    mates = []
    for row in select.find_all("option"):
        if not row["value"] == "0":
            mates.append(dict(id=int(row["value"]), name=row.text))
    return mates


def add_player(name):
    players = find_player(name)
    for player in players:
        if (
            not db.session.query(Player)
            .filter(Player.player_id == player["id"])
            .first()
        ):
            db.session.add(
                Player(
                    player_id=player["id"],
                    name=player["name"],
                    club_id=player["club_id"],
                    club=player["club_name"],
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
    return players

# def extract_player(url):
#     playerAttributes = {}  # will store all the information in dictionnary

#     content = read_url(url)
#     soup = BeautifulSoup(content, "html.parser")

#     meta = soup.find("meta", {"property": "og:url"})
#     print(url)
#     playerAttributes["id"] = meta["content"].rsplit("/", 1)[-1]
#     meta_name = soup.find("meta", {"property": "og:title"})
#     playerAttributes["Name"] = meta_name["content"].split(" - ", 1)[0]
#     # retrieving picture url and basic name
#     # link = soup.find("div", {"class":"dataBild"})
#     # playerAttributes["Picture"] = link.img["src"]

#     # reading tabular info and storing
#     for link in soup.find_all("table", {"class": "auflistung"}):
#         for line in link.find_all("tr"):  # , {"class" : "dataValue"}):
#             text = re.sub("\r|\n|\t|\xa0|  ", "", line.text)
#             lhs, rhs = text.split(":")
#             if rhs:
#                 playerAttributes[lhs] = rhs

#     transfers = soup.find("div", {"class": "transferhistorie"})
#     transfer_list = []
#     for tr in transfers.find_all("tr", {"class": "zeile-transfer"}):
#         tds = tr.find_all("td")
#         transfer_list.append(
#             {
#                 "Season": tds[0].text,
#                 "Date": tds[1].text,
#                 "Left": tds[2].a["id"],
#                 "Joined": tds[6].a["id"],
#                 "MV": tds[10].text,
#                 "Fee": tds[11].text,
#             }
#         )
#     url_mates = (
#         "http://www.transfermarkt.co.uk/eder/gemeinsameSpiele/spieler/%s/ajax/yw1/page/"
#         % playerAttributes["id"]
#     )
#     content_mates_prev = read_url(url_mates + "1")
#     num_pages = int(
#         BeautifulSoup(content_mates_prev, "html.parser")
#         .find("li", {"class": "letzte-seite"})
#         .a["href"]
#         .rsplit("/", 1)[-1]
#     )

#     mates = []
#     for page_num in range(1, num_pages + 1):
#         content_1 = read_url(url_mates + str(page_num))
#         soup_1 = BeautifulSoup(content_1, "html.parser")
#         for mate in soup_1.find_all("a", {"class": "spielprofil_tooltip"}):
#             mates.append(mate["id"])
#     playerAttributes["mates"] = mates

#     players_list.append(playerAttributes)
#     return True