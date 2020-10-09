from pySmartDL import SmartDL
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

debug = True
episode_links = []
dump_location = "{}\dl".format(os.getcwd())
anime_site = "https://www2.gogoanime.video"

if debug:
    url = "https://www2.gogoanime.video/category/fatekaleid-liner-prisma-illya-zwei"
else:
    url = input("Enter URL of series: ")
    print(url.strip())

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome(options=chrome_options)

def build_ep_list(url):
    print("Building List..")
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    episode_list = soup.find(id='episode_related')
    links = episode_list.find_all('a')
    for item in links:
        episode_links.append("{}{}".format(anime_site, item['href'].strip()))
        print("Found episode: {}{}".format(anime_site, item['href'].strip()))
    episode_links.reverse()
    print("Done.")
    DL_POSTER(browser)

def DL_POSTER(browser):
    print("Getting Poster..")
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('div', {"class", 'anime_info_body_bg'})
    imgsrc = div.find("img")

    if imgsrc['src'] is not None:
        print("Found poster: {}".format(imgsrc['src']))
        obj = SmartDL(imgsrc['src'], dump_location)
        obj.start()
        ext = "jpg"
        os.rename(r'{}'.format(obj.get_dest()), r'dl/poster.{}'.format(ext))
        print("Done.")
    else:
        print("Could not get poster!")

def get_dl_link(url):
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    dl_btn = soup.find('li', {"class", 'dowloads'})
    dl_btn_url = dl_btn.find_all('a')
    return dl_btn_url[0]['href'].strip()

class Quality:
    BEST = "720"
    MED = "480"
    LOW = "360"

def Find_quality(data, Quality):
    dl_index = 0
    found = False
    for item in data:
        if Quality in item.get_text():
            found = True
            break
        else:
            dl_index = dl_index + 1
    return found, dl_index

def beginDl(url):
    browser.get(url)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')
    dl_btns = soup.find_all('div', {"class", "dowload"})

    exists, index = Find_quality(dl_btns, Quality.BEST)
    if exists is False:
        exists, index = Find_quality(dl_btns, Quality.MED)
        if exists is False:
            exists, index = Find_quality(dl_btns, Quality.LOW)

    dl_btn_url = dl_btns[index].find_all('a')
    return dl_btn_url[0]['href'].strip()

def rename_file(file, name, season, episode):
    ext = "mp4"
    os.rename(r'{}'.format(file), r'dl/{}-s{}e{}.{}'.format(name, season, episode, ext))

def restructor():
    pass

def main():
    build_ep_list(url)

    for link in episode_links:
        src_link = get_dl_link(link)
        print("Captured Link: {}".format(src_link))
        dl_link = beginDl(src_link)
        print("DL Link: {}".format(dl_link))
        obj = SmartDL(dl_link, dump_location)
        obj.start()
        print("Completed Episode {}".format(link))

        Episode_number = re.sub(r'https://(.*)episode-', '', link)
        Episode_name = str(link).replace(anime_site+"/", "")
        if int(Episode_number) < 10:
            Episode_number = "0"+Episode_number

        rename_file(obj.get_dest(), Episode_name, "01", Episode_number)

#main()
build_ep_list(url)