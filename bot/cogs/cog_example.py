import re

from discord.ext import commands


class CogExample(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=['example'])
    async def message(self, ctx: commands.Context, *a):
        await ctx.send(f'{" ".join(a)}')


def setup(bot):
    bot.add_cog(CogExample(bot))
