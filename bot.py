import logging

import asyncio
import discord
import json
import sys

from bot.bot_client import Bot


def load_settings() -> dict:
    """
    Loads bot settings from 'settings.json' file

    Example settings file at 'settings.example.json'
    """
    with open('bot/settings.json', 'r') as f:
        return json.load(f)


async def run(settings: dict) -> None:
    bot = Bot(settings=settings)
    try:
        await bot.start(settings.get('token'))
    except KeyboardInterrupt:
        await bot.logout()
    except discord.errors.LoginFailure:
        print(f"Error: Invalid Token. Please input a valid token in '/bot/settings.json' file.")
        sys.exit(1)

if __name__ == '__main__':
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
    logger.addHandler(handler)
    loop = asyncio.get_event_loop()
    settings = load_settings()
    loop.run_until_complete(run(settings))
