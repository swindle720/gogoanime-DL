from threading import Thread
from pySmartDL import SmartDL
import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

class gogoanime_DL:

    class Quality:
        BEST = "720"
        MED = "480"
        LOW = "360"

    anime_site = "https://www2.gogoanime.video"
    browser = None
    url = None
    dl_folder = os.path.join(os.getcwd(), 'dl')
    series_name = None

    def __init__(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        self.browser = webdriver.Chrome(options=chrome_options)
        self.url = url

    def extract_eps(self):
        episode_links = []
        print("Extracting episode list..")
        self.browser.get(self.url)
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        episode_list = soup.find(id='episode_related')
        links = episode_list.find_all('a')
        for item in links:
            episode_links.append(["{}{}".format(self.anime_site, item['href'].strip()), False])
            print("Found episode: {}{}".format(self.anime_site, item['href'].strip()))
        episode_links.reverse()
        print("Completed.")

        skip = None
        while(isinstance(skip, int) is False):
            try:
                skip = int(input("Want to skip episodes (0-{})? ".format(len(episode_links))))

                if skip == 0:
                    print("Not skipping any.")
                elif skip < 0:
                    skip = None
                    print("That episode does not exist!")
                elif skip > len(episode_links):
                    skip = None
                    print("That episode does not exist!")
            except ValueError:
                print("Enter a number!")

        if skip > 0:
            for i in range(skip):
                del episode_links[0]
            print("Removed unwanted episodes.")

        return episode_links

    def getPoster(self):
        print("Extracting Poster")
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', {"class", 'anime_info_body_bg'})
        imgsrc = div.find("img")

        if imgsrc['src'] is not None:
            print("Found poster: {}".format(imgsrc['src']))
            print("Downloading..")
            obj = SmartDL(imgsrc['src'], self.dl_folder)
            obj.start()
            ext = self.getextension(obj.get_dest())
            os.rename(r'{}'.format(obj.get_dest()), r'dl/poster.{}'.format(ext))
            print("Completed.")
        else:
            print("Could not get poster! Skipping..")

    def extractDLlink(self, url):
        self.browser.get(url)
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        dl_btn = soup.find('li', {"class", 'dowloads'})
        dl_btn_url = dl_btn.find_all('a')
        return dl_btn_url[0]['href'].strip()

    def getextension(self, path):
        filename, file_extension = os.path.splitext(path)
        return file_extension

    def get_best_quality(self, data, Quality):
        dl_index = 0
        found = False
        for item in data:
            if Quality in item.get_text():
                found = True
                break
            else:
                dl_index = dl_index + 1
        return found, dl_index

    def getBestDLlink(self, url):
        self.browser.get(url)
        html = self.browser.page_source
        soup = BeautifulSoup(html, 'html.parser')
        dl_btns = soup.find_all('div', {"class", "dowload"})

        exists, index = self.get_best_quality(dl_btns, self.Quality.BEST)
        if exists is False:
            exists, index = self.get_best_quality(dl_btns, self.Quality.MED)
            if exists is False:
                exists, index = self.get_best_quality(dl_btns, self.Quality.LOW)

        dl_btn_url = dl_btns[index].find_all('a')
        return dl_btn_url[0]['href'].strip()

    def eps_rename(self, file, link):
        Episode_number = re.sub(r'https://(.*)episode-', '', link)
        Episode_name = str(link).replace(self.anime_site + "/", "")
        series_name = Episode_name.replace("-episode", "")
        if int(Episode_number) < 10:
            Episode_number = "0" + Episode_number
        ext = self.getextension(file)
        new_name = r'dl/{}-s{}e{}.{}'.format(Episode_name, "01", Episode_number, ext)
        os.rename(r'{}'.format(file), new_name)
        return new_name, series_name

    def PlexReconstruct(self, series_name):
        print("Rebuilding Folder structure for plex server..")
        name = os.path.join(self.dl_folder, series_name)
        if os.path.isdir(name) is False:
            os.mkdir(name)

        season_folder = os.path.join(name, 'Season 01')
        if os.path.isdir(season_folder) is False:
            os.mkdir(season_folder)

        for i in os.listdir(self.dl_folder):
            if os.path.isdir(os.path.join(self.dl_folder, i)) is False:
                print(os.path.join(self.dl_folder, i))
                os.rename(os.path.join(self.dl_folder, i), os.path.join(self.dl_folder, season_folder, i))
        print("Completed!")

    def HasEpsToProcess(self, episode_links):
        found = False
        for i in episode_links:
            if i[1] is False:
                found = True
                break
        return found

    def __del__(self):
        self.browser.close()

    def Runner(self, Tname):
        global episode_links
        while self.HasEpsToProcess(episode_links):
            for data in episode_links:
                if data[1] is False:
                    data[1] = True
                    print("{} Finding DL link for: {}".format(Tname, data[0]))
                    src_link = self.extractDLlink(data[0])
                    print("{} Captured src Link: {}".format(Tname, src_link))
                    dl_link = self.getBestDLlink(src_link)
                    print("{} Found Best DL Link: {}".format(Tname, dl_link))
                    print("{} Downloading..".format(Tname))
                    obj = SmartDL(dl_link, self.dl_folder)
                    obj.start()
                    print("{} Completed Episode: {}".format(Tname, data[0]))
                    new_name, self.series_name = self.eps_rename(obj.get_dest(), data[0])
                    print("{} Episode renamed to: ".format(Tname, new_name))



RunningThreads = []
Thread_Count = 3

url = input("Enter URL of series: ")
main = gogoanime_DL(url)
episode_links = main.extract_eps()
main.getPoster()

if Thread_Count > len(episode_links):
    Thread_Count = len(episode_links)

for i in range(Thread_Count):
    gogoanime = gogoanime_DL(url)
    t = Thread(target=gogoanime.Runner, args=("Thread-{}".format(i),))
    t.start()
    t.join()
    RunningThreads.append(t)

series = input("Enter name of series: ")
main.PlexReconstruct(series)