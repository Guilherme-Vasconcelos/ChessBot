import discord
import chess
from discord.ext import commands
from bot.bot_client import Bot

board = chess.Board()


class Chess(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=[''])
    async def challenge(self, ctx: commands.Context, challenged: discord.Member):
        await ctx.send(f'{challenged.mention}, you\'ve been challenged to a chess game by {ctx.message.author.mention}! Here\'s the board:\n```{board}```')


def setup(bot):
    bot.add_cog(Chess(bot))
