
'''run the bot'''

import json
import logging
import discord


log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s', '%Y-%m-%d %H:%M:%S'))
log.addHandler(handler)

with open('config.json', 'r', encoding='utf-8') as file:
    config = json.load(file)

client = discord.Client(intents = discord.Intents.all())


@client.event
async def on_ready():
    log.info('logged in as %s', client.user)


client.run(config['token'])
