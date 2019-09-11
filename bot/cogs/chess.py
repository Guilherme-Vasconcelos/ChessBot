import chess
from discord.ext import commands
import discord
from bot.bot_client import Bot


class Chess(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=['chalenge', 'challeng', 'fight', 'play', 'chaleng'])
    async def challenge(self, ctx: commands.Context, challenged: discord.Member):
        """
        This command !challenge is going to be used in order to challenge a player to a game of chess
        it takes one argument, which is the player, so it should be used like this: !challenge @Player
        """

        board = chess.Board()  # creates an instance of Board class, which is going to be used during the game

        await ctx.send(  # sends a message to let the challenged know who challenged them
            f'{challenged.mention}, you\'ve been challenged to a chess game by '
            f'{ctx.message.author.mention}! Here\'s the board:\n'
        )

        board_message = await ctx.send(f'```{board}```')  # sends the board (also saves it on board_message)

        while True:
            player2_invalid_move = False
            if not player2_invalid_move:
                #  if player 2 makes an invalid move, this block will not execute, thus making player 2 repeat his move
                #  game begins by asking the challenger's move, updating board and then showing the updated board
                #  the line below will get the player's move
                msg = await self.bot.wait_for('message', check=lambda message: message.author == ctx.author)
                try:
                    board.push_san(msg.content)  # updates board
                except ValueError:
                    await board_message.edit(content=f'```{board}```\n{ctx.author.mention} wait, '
                                             f'that\'s illegal! Please, make another move.')
                    await msg.delete()
                    continue
                #  the line below edits bot's message in order to show the updated board and shows his move
                await board_message.edit(content=f'```{board}```\n{ctx.author.mention} played {msg.content}')
                await msg.delete()  # deletes player's message

            #  asks for the challenged's move, updates board and then shows the updated board
            #  the line below will get the player's move
            msg = await self.bot.wait_for('message', check=lambda message: message.author == challenged)
            try:
                board.push_san(msg.content)  # updates board
                player2_invalid_move = False
            except ValueError:
                await board_message.edit(content=f'```{board}```\n{challenged.mention} wait, '
                                         f'that\'s illegal! Please, make another move.')
                await msg.delete()
                player2_invalid_move = True
                continue
            #  the line below edits bot's message in order to show the updated board and shows his move
            await board_message.edit(content=f'```{board}```\n{challenged.mention} played {msg.content}')
            await msg.delete()  # deletes player's message


def setup(bot):
    bot.add_cog(Chess(bot))
