# Web Site generator
## Desc:
Generate website from script provided by `./play.it`.

## Status
### Done
- extract some information from script
- getting information from IGDB
- web page generation
    - General information (Tags, platform (not accurate), Reakease, store link)
    - Description
    - Instalation (missing dpendencies)
    - Screenshot

### TO DO
- clean code (aka deduplicate code in API, fix typo, add comment)
- better index
- bug :
    - Fix duplicata
    - Game not found (ex: mokey Island 1)
    - Wrong game prasing (ex: rogue leagacy -> found: Assassin’s Creed Rogue)
    - fix script parsing for : `play-fallout-classics.sh`, `play-enigmatis.sh`, `play-braveland.sh`


## How to run
### Depedences and keys

First install python >= 3.11.

Install dpendencie: `pip install -r requirment.txt`

Create file `config.py` with your api keys (more info: https://api-docs.igdb.com/?python#account-creation)

config.py sample:
``` python
clientID = "abcdefg123"
clientSecret = "hijklm456"
```

### Collect data
Change script directory at: `game_list_extractor.py` line 32

run `game_list_extractor.py`

At the end a new file `out_igdb.json` was created.

### Generating web site
run `site_builder.py`
At the end a new directory `site` was created, with game pages and simple index