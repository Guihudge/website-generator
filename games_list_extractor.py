import os
import logging
import sys
import time
import json

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

spript_folder = "/home/guillaume/src/games/games"

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
    with open(script_path, 'r') as file:
        data = file.readlines()
        for line in data:
            if (("GAME_ID=" in line) or ("GAME_ID_BASE=" in line)) and not id_found:
                info["id"] = extract_strings(line.split("=")[1])
                id_found = True
            elif (("GAME_NAME=" in line) or ("GAME_NAME_BASE=" in line)) and not name_found:
                info["name"] = extract_strings(line.split("=")[1])
                name_found = True
            elif ("ARCHIVE" in line and "URL=" in line):
                if "url" in info:
                    info["url"].append(extract_strings(line.split("=")[1]))
                else:
                    info["url"] = [extract_strings(line.split("=")[1])]
    
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
"""
for s in scripts_list:
    infos.append(get_script_info(spript_folder + "/" + s, logger))
logger.debug("Parsing script ok")
"""
for s in range(0,5):
    infos.append(get_script_info(spript_folder + "/" + scripts_list[s], logger))
logger.debug("Parsing script ok")

igdb_info = []
trated_script = 0

for game in infos:
    id = api.searchGameID(game["name"])
    if id >= 0:
        logger.debug("found id: {} for game {}".format(id, game["name"]))
        info = api.getGameInfo(id)
        time.sleep(0.3)
        for i in range(0, len(info["screenshots"])):
            info["screenshots"][i] = api.getScreenshotUrl(info["screenshots"][i])
            time.sleep(0.3)
        
        if "artworks" in info:
            for i in range(0, len(info["artworks"])):
                info["artworks"][i] = api.getArtworksUrl(info["artworks"][i])
                time.sleep(0.3)

        info["cover"] = api.getCoverUrl(id)

        igdb_info.append(info)
    trated_script += 1
    logger.info("Script {}/{}".format(trated_script, len(infos)))
logger.debug("Getting data ok")

with open("out_igdb.json", "w") as file:
    json.dump(igdb_info, file)
#print(igdb_info)
#print(get_game_provider(infos))
#print(infos)
