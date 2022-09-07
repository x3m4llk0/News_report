import json

import requests
from loguru import logger

from tgbot.config import load_config


async def send_to_api(id, title="Количество обращений", name="activity"):
    config = load_config(".env")
    r = requests.post(f'{config.misc.platform_host}/api/v1/targets/hit',
                      data={'title': title,
                            'name': name,
                            'bot_id': '5004063309',
                            'user_id': id},
                      headers={'X-Token': 'e12d72fab4dc966c3040b955ffbce079'},
                      )
    logger.info(r.json())


async def send_upd(upd, new=False):
    logger.info(upd)
    upd = json.loads(upd)
    upd["message"]["from"] = upd["message"].pop("from_user")
    upd = json.dumps(upd, default=dict)
    if new:
        open_request = upd
        open_request = json.loads(open_request)
        open_request["message"]["text"] = "/openmanagersesion"
        open_request["update_id"] = 0
        open_request = json.dumps(open_request, default=dict)
        requests.post(f'https://lk.bottec.ru/api/tg/v1/bot/client',
                      headers={'X-Secret': '6d3ad29879a90b4dd1b4f76e82166ca3', 'Bot-ID': '5004063309'},
                      data=open_request,
                      auth=('test', 'test'))

    r = requests.post(f'https://lk.bottec.ru/api/tg/v1/bot/client',
                      headers={'X-Secret': '6d3ad29879a90b4dd1b4f76e82166ca3', 'Bot-ID': '5004063309'},
                      data=upd,
                      auth=('test', 'test'))

    logger.info(r.json())
