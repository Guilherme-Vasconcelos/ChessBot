import discord
from discord.ext import commands
from bot.bot_client import Bot


class Help(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=['chess', 'chessbot'])
    async def help(self, ctx: commands.Context):
        embed_help = discord.Embed(title='Hello! Here are all my commands:', color=0x0473b3)
        embed_help.add_field(name='!help', value='Lists all available commands')
        embed_help.add_field(name='!challenge [player]',
                             value='Starts a game against [player]. Remember to mention them!'
                             )
        await ctx.send(embed=embed_help)


def setup(bot):
    bot.add_cog(Help(bot))
