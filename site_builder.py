import json
from jinja2 import Environment, FileSystemLoader

def getName(game):
    return game["name"]

env = Environment(loader=FileSystemLoader("templates/"))
template = env.get_template("game.jinja")

data = {}
with open("out_igdb.json", "r") as file:
    data = json.load(file)

links = []

for game in data:
    if "id" in game:
        filename = "site/"+str(game["id"]) + ".html"
        content = ""
        if "screenshots" in game and "platforms" in game:
            content = template.render(game, gellerySize=len(game["screenshots"]), nbPlatform=len(game["platforms"]))
        elif "screenshots" in game and "platforms" not in game:
            content = template.render(game, gellerySize=len(game["screenshots"]), nbPlatform=0)
        elif "screenshots" not in game and "platforms" in game:
            content = template.render(game, gellerySize=0, nbPlatform=len(game["platforms"]))
        elif "screenshots" not in game and "platforms" not in game:
            content = template.render(game, gellerySize=0, nbPlatform=0)
        index_info = {}

        if game["cover"] != "":
            index_info = {"name":game["name"], "link":str(game["id"]) + ".html", "cover":game["cover"]}
        else:
            index_info = {"name":game["name"], "link":str(game["id"]) + ".html", "cover":"image/notFound.jpeg"}

        links.append(index_info)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)
            print("Done")

links.sort(key=getName)

index = env.get_template("index.jinja")
idx = index.render(games=links)

with open("site/index.html", "w") as ind:
    ind.write(idx)
    print("Index Write")

print("Generated {} pages".format(len(links)))
