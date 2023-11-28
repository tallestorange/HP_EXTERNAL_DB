import os
import urllib.request

from PIL import Image
import requests
from bs4 import BeautifulSoup
import csv
import glob


def download_picture(url, id):
    if os.path.exists(f"{id}.jpg"):
        return
    urllib.request.urlretrieve(url,  f"{id}.jpg")
    img = Image.open(f"{id}.jpg")
    img.save(f"{id}.webp", quality=75)
    os.remove(f"{id}.jpg")


def parse_link(url):
    if "http://www.up-front-works.jp" in url:
        req = requests.get(url)
        img_bs4 = BeautifulSoup(req.text, "html.parser")
        img_link = img_bs4.select_one("#left > a")["href"]
        product_title, artist = img_bs4.find("h2", class_="product_title").text.split("\n")
        category, release_date, label = [i.text for i in img_bs4.find_all("td", class_="columnB")[:3]]
    elif "http://www.helloproject.com" in url:
        req = requests.get(url)
        img_bs4 = BeautifulSoup(req.text, "html.parser")
        img_link = img_bs4.select_one("#rd_left > ul > li > a")["href"]
        product_title = img_bs4.select_one("#rd_right > h2").text.strip()
        artist = img_bs4.select_one("#artist_name").text
        category, release_date, label = [i.text for i in img_bs4.find_all("td", class_="item02")[:3]]
    return (img_link, product_title, artist, category, release_date, label)


result = []
ids = set()

# with open('links.csv', 'w') as f:
#     writer = csv.writer(f)
#     writer.writerow(["song_index", "id", "url"])
#     for i in range(1, 4000):
#         url = f"https://hp-setlist.com/song_profile.php?id={i}"
#         req = requests.get(url)
#         bs4 = BeautifulSoup(req.text, "html.parser")
#         links = [i["href"] for i in bs4.select("#fav-table > tbody > tr > td:nth-child(2) > a")]
#         for link in links:
#             if "http://www.up-front-works.jp" in link or "http://www.helloproject.com" in link:
#                 id = link.split("/")[-2]
#                 if not id in ids:
#                     ids.add(id)
#                     print(i, id, link)
#                     writer.writerow([i, id, link])
#                     img_link, product_title, artist, category, release_date, label = parse_link(link)
#                     print([id, product_title, release_date, artist, category, label, img_link])
#                     result.append([id, product_title, release_date, artist, category, label, img_link])


with open("links.csv") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        i, id, link = row
        if any([os.path.exists(f"{j}/{id}.webp") for j in glob.glob("*")]):
            print("skip ", id)
            continue
        else:
            print("download ", id)
        img_link, product_title, artist, category, release_date, label = parse_link(link)
        if not os.path.exists(category):
            os.mkdir(category)
        download_picture(img_link, f"{category}/{id}")
        print(*[id, product_title, release_date, artist, category, label, img_link])
        result.append([id, product_title, release_date, artist, category, label, img_link])

with open('links_dl02.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(["id", "product_title", "release_date", "artist", "category", "label", "img_link"])
    writer.writerows(sorted(result, key=lambda x:x[2]))
