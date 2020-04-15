import urllib
# import urllib.request
import requests
from bs4 import BeautifulSoup
import re
from multiprocessing import Pool
from datetime import datetime

players_list = []


def read_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    # response.text = response.read()
    return response.content


def extract_player(url):
    playerAttributes = {}  # will store all the information in dictionnary

    content = read_url(url)
    soup = BeautifulSoup(content, "html.parser")

    meta = soup.find("meta", {"property": "og:url"})
    print(url)
    playerAttributes["id"] = meta["content"].rsplit("/", 1)[-1]
    meta_name = soup.find("meta", {"property": "og:title"})
    playerAttributes["Name"] = meta_name["content"].split(" - ", 1)[0]
    # retrieving picture url and basic name
    # link = soup.find("div", {"class":"dataBild"})
    # playerAttributes["Picture"] = link.img["src"]

    # reading tabular info and storing
    for link in soup.find_all("table", {"class": "auflistung"}):
        for line in link.find_all("tr"):  # , {"class" : "dataValue"}):
            text = re.sub("\r|\n|\t|\xa0|  ", "", line.text)
            lhs, rhs = text.split(":")
            if rhs:
                playerAttributes[lhs] = rhs

    transfers = soup.find("div", {"class": "transferhistorie"})
    transfer_list = []
    for tr in transfers.find_all("tr", {"class": "zeile-transfer"}):
        tds = tr.find_all("td")
        transfer_list.append(
            {
                "Season": tds[0].text,
                "Date": tds[1].text,
                "Left": tds[2].a["id"],
                "Joined": tds[6].a["id"],
                "MV": tds[10].text,
                "Fee": tds[11].text,
            }
        )
    url_mates = (
        "http://www.transfermarkt.co.uk/eder/gemeinsameSpiele/spieler/%s/ajax/yw1/page/"
        % playerAttributes["id"]
    )
    content_mates_prev = read_url(url_mates + "1")
    num_pages = int(
        BeautifulSoup(content_mates_prev, "html.parser")
        .find("li", {"class": "letzte-seite"})
        .a["href"]
        .rsplit("/", 1)[-1]
    )

    mates = []
    for page_num in range(1, num_pages + 1):
        content_1 = read_url(url_mates + str(page_num))
        soup_1 = BeautifulSoup(content_1, "html.parser")
        for mate in soup_1.find_all("a", {"class": "spielprofil_tooltip"}):
            mates.append(mate["id"])
    playerAttributes["mates"] = mates

    players_list.append(playerAttributes)
    return True


def f(x):
    return x * x


if __name__ == "__main__":
    # running check on Lord Eder
    # id=84481
    # start = datetime.utcnow()
    url = "http://www.transfermarkt.co.uk/eder/profil/spieler/"
    url_list = [url + str(i) for i in range(1, 11)]
    print(url_list)
    # extract_player(url_list[0])
    with Pool(5) as p:
        records = p.map(extract_player, url_list)
    print(players_list)
