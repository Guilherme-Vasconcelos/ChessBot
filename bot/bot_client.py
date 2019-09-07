import re
import sys
import json
import asyncio
import logging
import datetime
from pathlib import Path

import discord
from discord.ext import commands

from bot.orm.models import db


class Bot(commands.Bot):
    def __init__(self, settings: dict):
        super().__init__(command_prefix=settings.get('prefix'), case_insensitive=True)
        self.settings = settings
        self.start_time = None
        self.app_info = None

        self.db_setup()
        self.remove_command('help')
        self.loop.create_task(self.track_start())
        self.loop.create_task(self.load_all_extensions())

    async def track_start(self):
        """
        Waits for the bot to connect to discord and then records the time
        """
        await self.wait_until_ready()
        self.start_time = datetime.datetime.utcnow()

    @staticmethod
    def get_cogs():
        """Gets cog names from /cogs/ folder"""
        not_extensions = ['utils', 'embeds', 'models', '__init__']
        cogs = [x.stem for x in Path('bot/cogs').glob('*.py')]
        for cog in cogs:
            if cog in not_extensions:
                cogs.remove(cog)
        return cogs

    async def unload_all_extensions(self):
        """Unloads all cog extensions"""
        errored = False
        for extension in self.get_cogs():
            try:
                self.unload_extension(f'bot.cogs.{extension}')
                print(f'- Unloaded extension {extension}')
            except Exception as e:
                error = f'{extension}:\n {type(e).__name__} : {e}'
                print(f'Failed to unload extension {error}')
                errored = True
        return errored

    async def load_all_extensions(self):
        """Attempts to load all .py files in /cogs/ as cog extensions"""
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing
        errored = False
        for extension in self.get_cogs():
            try:
                self.load_extension(f'bot.cogs.{extension}')
                print(f'- loaded Extension: {extension}')
            except Exception as e:
                error = f'{extension}:\n {type(e).__name__} : {e}'
                print(f'Failed to load extension {error}')
                errored = True
        print('-' * 10)
        return errored

    async def reload_all_extensions(self):
        """Attempts to reload all .py files in /cogs/ as cog extensions"""
        await self.wait_until_ready()
        await asyncio.sleep(1)  # ensure that on_ready has completed and finished printing
        errored = False
        for extension in self.get_cogs():
            try:
                self.reload_extension(f'bot.cogs.{extension}')
                print(f'- reloaded Extension: {extension}')
            except Exception as e:
                error = f'{extension}:\n {type(e).__name__} : {e}'
                print(f'Failed to reload extension {error}')
                errored = True
        print('-' * 10)
        return errored

    async def on_ready(self):
        """
        This event is called every time the bot connects or resumes connection.
        """
        print('-' * 10)
        self.app_info = await self.application_info()
        print(
            f'Logged in as: {self.user.name}\n'
            f'Using discord.py version: {discord.__version__}\n'
            f'Owner: {self.app_info.owner}\n'
            f'Prefix: {self.settings.get("prefix")}\n'
            f'Original Template Maker: SourSpoon / Spoon#7805\n'
            f'Updated by: https://github.com/johnvictorfs\n'
            f'Template available at: https://github.com/johnvictorfs/discord_bot_template'
        )
        print('-' * 10)

    async def on_message(self, message: discord.Message):
        """
        This event triggers on every message received by the bot
        """
        if message.author.bot:
            return  # Ignore all bot messages

        await self.process_commands(message)

    async def send_logs(self, e: Exception, tb: str, ctx: commands.Context = None):
        """
        Sends logs of errors to the bot's instance owner as a private Discord message
        """
        owner = self.app_info.owner
        separator = ("_\\" * 15) + "_"
        info_embed = None
        if ctx:
            info_embed = discord.Embed(title="__Error Info__", color=discord.Color.dark_red())
            info_embed.add_field(name="Message", value=ctx.message.content, inline=False)
            info_embed.add_field(name="By", value=ctx.author, inline=False)
            info_embed.add_field(name="In Guild", value=ctx.guild, inline=False)
            info_embed.add_field(name="In Channel", value=ctx.channel, inline=False)
        try:
            await owner.send(content=f"{separator}\n**{e}:**\n```python\n{tb}```", embed=info_embed)
        except discord.errors.HTTPException:
            logging.error(f"{e}: {tb}")
            try:
                await owner.send(
                    content=f"(Sending first 500 chars of traceback, too long)\n{separator}\n**{e}:**"
                    f"\n```python\n{tb[:500]}```",
                    embed=info_embed
                )
            except Exception:
                await owner.send(content="Error trying to send error logs.", embed=info_embed)

    @staticmethod
    def db_setup():
        """
        Setup the bot's database, creates necessary tables if not yet created
        """
        db.connect()
        models = []  # Add bot.orm.models Models here
        db.create_tables(models)
        db.close()
