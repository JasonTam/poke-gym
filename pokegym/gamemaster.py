import requests
import json
import re
from typing import Dict
from pathlib import Path

CUR_DIR = Path(__file__).parent

url_game_master = 'https://raw.githubusercontent.com/' \
                  'pokemongo-dev-contrib/pokemongo-game-master/' \
                  'master/versions/latest/GAME_MASTER.json'
path_game_master = CUR_DIR / 'data/GAME_MASTER.json'

# gmdata = json.loads(requests.get(url_game_master).content)
gmdata = json.load(open(path_game_master, 'r'))


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


pokemon_raw_d: Dict[str, Dict] = {}
moves_raw_d: Dict[str, Dict] = {}
combat_settings_d: Dict[str, Dict] = {}


for template in gmdata["itemTemplate"]:
    tid = template['templateId']

    # Match move, either Fast or Charged
    if re.fullmatch(r'COMBAT_V\d+_MOVE_.+', tid):
        k = tid.split('_MOVE_')[-1]
        moves_raw_d[k] = template

    # Match Pokemon
    if re.fullmatch(r'V\d+_POKEMON_.+', tid):
        k = tid.split('POKEMON_')[-1]
        pokemon_raw_d[k] = template

    if tid == 'PLAYER_LEVEL_SETTINGS':
        level_to_cpm = dict(enumerate(
            template['playerLevel']['cpMultiplier'], start=1))
        half_level_to_cpm = {}
        for level, cpm in level_to_cpm.items():
            if (level + 1) in level_to_cpm.keys():
                half_level_to_cpm[level + 0.5] = (
                    (cpm ** 2 + level_to_cpm[level + 1] ** 2) / 2) ** 0.5
        level_to_cpm.update(half_level_to_cpm)

    if tid == 'COMBAT_SETTINGS':
        for name, value in template["combatSettings"].items():
            combat_settings_d[name] = value

    # Buff params
    if tid == 'COMBAT_STAT_STAGE_SETTINGS':
        for name, value in template["combatStatStageSettings"].items():
            combat_settings_d[name] = value

