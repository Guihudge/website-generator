# Web Site generator
## Desc:
Generate website from script provided by `./play.it`.

## Status
### TO DO
- instalation instruction
- clean code
- add progress bar for indexing
- better index
- bug fix

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