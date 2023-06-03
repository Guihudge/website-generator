import os
import logging
import sys
import time
import json
from progress.bar import Bar
from datetime import datetime

from IGDB import IGDB
from config import *

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

spript_folder = "/home/guillaume/game_extarctor/games"

def get_all_script(folder):
    scripts = []
    for file in os.listdir(folder):
        if ".sh" in file:
            scripts.append(file)
    return scripts

def extract_strings(fake_string):
    string = ""
    try:
        string = fake_string.split("'")[1]
    except:
        string = ""
    return string
    

def get_script_info(script_path, logger):
    id_found = False
    name_found = False
    info = {}
    info["script_name"] = script_path.split("/")[-1]
    with open(script_path, 'r') as file:
        data = file.readlines()
        for line in data:
            if "script_version=" in line:
                info["script_version"] = line.split("=")[1][0:-1]
            elif (("GAME_ID=" in line) or ("GAME_ID_BASE=" in line)) and not id_found:
                info["id"] = extract_strings(line.split("=")[1])
                id_found = True
            elif (("GAME_NAME=" in line) or ("GAME_NAME_BASE=" in line)) and not name_found:
                info["name"] = extract_strings(line.split("=")[1])
                name_found = True
            elif ("ARCHIVE_" in line and not "FILES" in line and not "MD5" in line and not "TYPE" in line and not "SIZE" in line and not "SIZE" in line and not "VERSION" in line and  "=" in line):
                if "URL" in line:
                    if "url" in info:
                        info["url"].append(extract_strings(line.split("=")[1]))
                    else:
                        info["url"]= [extract_strings(line.split("=")[1])]
                else:
                    if "file" in info:
                        info["file"].append(extract_strings(line.split("=")[1]))
                    else:
                        info["file"]= [extract_strings(line.split("=")[1])]
                
    
    if info == {}:
        logger.warn("Unable to parse : {}".format(script_path.split("/")[-1]))
    elif not "name" in info:
        logger.warn("Unable to get name : {}".format(script_path.split("/")[-1]))
    return info

def extract_provider_from_url(url):
    if url != '':
        url = url.split("/")[2]
        url = url.split(".")[-2]
    return url


def get_game_provider(infos):
    provider = []
    for game_info in infos:
        if "url" in game_info:
            for url in game_info["url"]:
                prov = extract_provider_from_url(url)
                if prov not in provider:
                    provider.append(prov)
    return provider


# create logger with 'spam_application'
logger = logging.getLogger("Game_list_Extractor")
logger.setLevel(logging.INFO)

# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

ch.setFormatter(CustomFormatter())

logger.addHandler(ch)

logger.info("Logger Init!")


api = IGDB(logger)
if api.login(clientID, clientSecret) != "OK":
    logger.error("Unable to log in IGDB!")
    sys.exit(1)


scripts_list = get_all_script(spript_folder)
logger.info("Found {} script(s)".format(len(scripts_list)))
infos = []


for s in scripts_list:
    infos.append(get_script_info(spript_folder + "/" + s, logger))
logger.debug("Parsing script ok")

"""
for s in range(0,5):
    infos.append(get_script_info(spript_folder + "/" + scripts_list[s], logger))
logger.debug("Parsing script ok")
"""


igdb_info = {}
with open("out_igdb.json", "r") as file:
    try:
        igdb_info = json.load(file)
    except:
        pass

presentInFile = []
for g in igdb_info:
    presentInFile.append(g["script"]["name"])

trated_script = 0
generalBar = Bar("General Progress", max=len(infos))


for game in infos:
    if not game["name"] in presentInFile:
        id = api.searchGameID(game["name"])
        if id >= 0:
            logger.debug("found id: {} for game {}".format(id, game["name"]))
            info = api.getGameInfo(id)
            size = 0
            if "screenshots" in info:
                size += len(info["screenshots"])
            if "artworks" in info:
                size += len(info["artworks"])
            if "platforms" in info:
                size += len(info["platforms"])
            if "themes" in info:
                size += len(info["themes"])
            
            scriptBar = Bar("script progression ({})".format(game["name"]), max=size)
            time.sleep(0.3)
            if "screenshots" in info:
                for i in range(0, len(info["screenshots"])):
                    info["screenshots"][i] = api.getScreenshotUrl(info["screenshots"][i])
                    time.sleep(0.3)
                    scriptBar.next()
                
            if "artworks" in info:
                for i in range(0, len(info["artworks"])):
                    info["artworks"][i] = api.getArtworksUrl(info["artworks"][i])
                    time.sleep(0.3)
                    scriptBar.next()
            
            if "platforms" in info:
                for i in range(0, len(info["platforms"])):
                    info["platforms"][i] = api.getPlatformInfo(info["platforms"][i])["name"]
                    time.sleep(0.3)
                    scriptBar.next()

            if "themes" in info:
                for i in range(0, len(info["themes"])):
                    info["themes"][i] = api.getThemeInfo(info["themes"][i])
                    time.sleep(0.3)
                    scriptBar.next()
        
            if "rating" in info:
                info["rating"] = int(info["rating"])

            if "first_release_date" in info:
                info["first_release_date"] = datetime.utcfromtimestamp(info["first_release_date"]).strftime('%m/%d/%Y')
            
            info["script"] = game

            info["cover"] = api.getCoverUrl(id)

            igdb_info.append(info)

            file = open("out_igdb.json", "w")
            json.dump(igdb_info, file)
            file.flush()
            file.close()
            scriptBar.finish()

    trated_script += 1
    generalBar.next()

generalBar.finish()
logger.debug("Getting data ok")

#print(igdb_info)
#print(get_game_provider(infos))
#print(infos)
