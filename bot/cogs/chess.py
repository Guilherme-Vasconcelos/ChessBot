import chess
from discord.ext import commands
import discord
from bot.bot_client import Bot


class Chess(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=[])
    async def challenge(self, ctx: commands.Context, challenged: discord.Member):
        """
        This command !challenge is going to be used in order to challenge a player to a game of chess
        it takes one argument, which is the player, so it should be used like this: !challenge @Player
        """

        board = chess.Board()

        await ctx.send(
            f'{challenged.mention}, you\'ve been challenged to a chess game by'
            f'{ctx.message.author.mention}! Here\'s the board:\n'
        )

        board_message = await ctx.send(f'```{board}```')

        while True:
            #  Game begins by asking the challenger's move, updating board and then showing the updated board
            msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)  # gets move
            board.push_san(msg.content)  # updates board
            #  the line below edits bot's message in order to show the updated board and shows his move
            await board_message.edit(content=f'```{board}```\n{ctx.message.author.mention} played {msg.content}')
            await msg.delete()  # deletes player's message

            #  Asks for the challenged's move, updates board and then shows the updated board
            msg2 = await self.bot.wait_for('message', check=lambda message: message.author == challenged)  # gets move
            board.push_san(msg2.content)  # updates board
            #  the line below edits bot's message in order to show the updated board and shows his move
            await board_message.edit(content=f'```{board}```\n{challenged.mention} played {msg2.content}')
            await msg2.delete()  # deletes player's message


def setup(bot):
    bot.add_cog(Chess(bot))
