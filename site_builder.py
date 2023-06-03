import json
from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates/"))
template = env.get_template("game.jinja")

data = {}
with open("out_igdb.json", "r") as file:
    data = json.load(file)

links = []

for game in data:
    filename = "site/"+str(game["id"]) + ".html"
    content = template.render(game, gellerySize=len(game["screenshots"]))
    links.append({"name":game["name"], "link":str(game["id"]) + ".html"})
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
        print("Done")

index = env.get_template("index.jinja")
idx = index.render(games=links)
with open("site/index.html", "w") as ind:
    ind.write(idx)
    print("Index Write")
