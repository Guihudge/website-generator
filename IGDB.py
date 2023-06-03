import requests
import logging

BASE_URL = "https://api.igdb.com/v4"
class IGDB:
    logger:logging.Logger = None
    auth_header = {}

    def __init__(self, logger:logging.Logger) -> None:
        self.logger = logger

    def login(self, clientId:str, clientSecret:str):
        url = "https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials".format(clientId, clientSecret)
        log_info = requests.post(url)
        self.logger.debug("Start logging on IGDB")
        
        if log_info.status_code != 200:
            self.logger.critical("IGDB loggin failed with code : {}".format(log_info.status_code))
            return "Error!"
        
        else:
            log_token = log_info.json()
            self.auth_header["Client-ID"] = clientId
            self.auth_header["Authorization"] = "Bearer " + log_token['access_token']
            self.logger.debug("loggin sucesful")
            return "OK"

    def searchGameID(self, gameName:str):
        url = BASE_URL + "/search"
        body = 'fields game; search "{}"; limit 5;'.format(gameName).encode("utf-8")
        self.logger.debug("serach game {} in IGDB".format(gameName))

        response = requests.post(url, data=body, headers=self.auth_header)
        if response.status_code != 200:
            self.logger.warn("get {} HTTP code for search : {}".format(response.status_code, gameName))
            return "-1"

        gameID = response.json()
        if len(gameID) <= 0:
            self.logger.warning("Game {} not found".format(gameName))
            return -1
        else:
            found = False
            for e in gameID:
                if not "game" in e and "title" in e:
                    self.logger.error("IGDB return folowing error: {}".format(gameID[0]['title']))
                    return -1
                else:
                    if "game" in e:
                        return e["game"]
            
            return -1
    
    def getGameInfo(self, gameID):
        url = BASE_URL + "/games"
        body = "fields artworks, platforms, screenshots, storyline, summary, name, rating, themes, first_release_date; where id = {};".format(str(gameID)).encode("utf-8")
        response = requests.post(url, data=body, headers=self.auth_header)
        
        if response.status_code != 200:
            self.logger.warn("get {} HTTP code for ID : {}".format(response.status_code, gameID))
            return {}
        
        gameID = response.json()
        if len(gameID) <= 0:
            self.logger.warning("Game ID {} not found".format(gameID))
            return {}
        else:
            if not "id" in gameID[0] and "title" in gameID[0]:
                self.logger.error("IGDB return folowing error: {}".format(gameID[0]['title']))
                return {}
            else:
                return gameID[0]
    
    def getImageUrl(self, img_type, gameID):
        url = BASE_URL + "/" + img_type
        body = ""
        
        match img_type:
                    case "covers":
                        body = "fields *; where game = {};".format(gameID).encode("utf-8")
                    case "artworks":
                        body = "fields *; where id = {};".format(gameID).encode("utf-8")
                    case "screenshots":
                        body = "fields *; where id = {};".format(gameID).encode("utf-8")
        
        response = requests.post(url, data=body, headers=self.auth_header)
        self.logger.debug("URL: {}".format(url))
        self.logger.debug("body: {}".format(body))

        if response.status_code != 200:
            self.logger.warn("get {} HTTP code for ID : {}".format(response.status_code, gameID))
            return ""
        
        img = response.json()
        if len(img) <= 0:
            self.logger.warning("{} for game ID {} not found".format(img_type, gameID))
            return ""
        else:
            if not "id" in img[0] and "image_id" in img[0]:
                self.logger.warning("{} for game ID {} not found".format(img_type, gameID))
                return ""
            else:
                match img_type:
                    case "covers":
                        return "https://images.igdb.com/igdb/image/upload/t_cover_big/" + img[0]["image_id"] + ".jpg"
                    case "artworks":
                        return "https://images.igdb.com/igdb/image/upload/t_screenshot_huge/" + img[0]["image_id"] + ".jpg"
                    case "screenshots":
                        return "https://images.igdb.com/igdb/image/upload/t_screenshot_huge/" + img[0]["image_id"] + ".jpg"
    
    def getCoverUrl(self, gameID):
        return self.getImageUrl("covers", gameID)
    
    def getArtworksUrl(self, gameID):
        return self.getImageUrl("artworks", gameID)
    
    def getScreenshotUrl(self, gameID):
        return self.getImageUrl("screenshots", gameID)

    def getPlatformInfo(self, platformID):
        url = BASE_URL + "/platforms"
        body = "fields *; where id = {};".format(platformID)

        reponse = requests.post(url, data=body, headers=self.auth_header)

        if reponse.status_code != 200:
            self.logger.warn("get {} HTTP code for platform ID : {}".format(reponse.status_code, platformID))
            return {}
        
        j = reponse.json()
        
        if len(j) > 0:
            return j[0]
        return {}
    
    def getPlatformLogoUrl(self, platformID):
        info = self.getPlatformInfo(platformID)
        
        if info == {}:
            return ""
        
        url = BASE_URL + "/platform_logos"
        body = "fields *; where id = {};".format(info["platform_logo"])
        reponse = requests.post(url, data=body, headers=self.auth_header)

        if reponse.status_code != 200:
            self.logger.warn("get {} HTTP code for platform ID : {}".format(reponse.status_code, platformID))
            return ""
        
        j = reponse.json()
        if len(j) > 0:
            return "https://images.igdb.com/igdb/image/upload/t_logo_med/" + j[0]["image_id"] + ".jpg"
        return ""
    
    def getThemeInfo(self, themeID):
        url = BASE_URL + "/themes"
        body = "fields *; where id = {};".format(themeID)
        reponse = requests.post(url, data=body, headers=self.auth_header)

        if reponse.status_code != 200:
            self.logger.warn("get {} HTTP code for platform ID : {}".format(reponse.status_code, platformID))
            return ""
        
        j = reponse.json()
        if len(j) > 0:
            return j[0]["name"]
        return ""
    
    def alive(self):
        url = BASE_URL + "/games"
        test = requests.post(url, headers=self.auth_header)
        print(test.json())

        



# 7046