import chess
from discord.ext import commands
import discord
from bot.bot_client import Bot


def check_for_draw(board: chess.Board) -> bool:
    """
    Function checks for stalemate/insufficient material/threefold repetition/fifty moves rule
    """
    return any([
        board.is_insufficient_material(), board.can_claim_threefold_repetition(),
        board.can_claim_fifty_moves(), board.is_stalemate()
    ])


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
        def check_for_valid_message1(message: discord.Message) -> bool:
            """
            This function will verify if the first, third, etc. messages during game are valid
            i.e. it must either be a MOVE sent by the PLAYER 1, or a RESIGN message sent by any player
            or a DRAW message sent by any player
            """
            return (message.author == ctx.author or
                    message.content.lower() == 'resign' or message.content.lower() == 'draw')

        def check_for_valid_message2(message: discord.Message) -> bool:
            """
            This function will verify if the second, fourth, etc. messages during game are valid
            i.e. it must either be a MOVE sent by the PLAYER 2, or a RESIGN message sent by any player
            or a DRAW message sent by any player
            """
            return (message.author == challenged or
                    message.content.lower() == 'resign' or message.content.lower() == 'draw')

        board = chess.Board()  # creates an instance of Board class, which is going to be used during the game

        await ctx.send(  # sends a message to let the challenged know who challenged them
            f'{challenged.mention}, you\'ve been challenged to a chess game by '
            f'{ctx.message.author.mention}!\n'
            f'Check out the board below:\n'
        )

        embed = discord.Embed(color=0x0473b3)  # creates embed
        embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # sets board image
        embed.add_field(name='Special words:', value='\n**`resign`**: resigns the game'
                        f'\n**`draw`**: offers/accepts draw')

        board_message = await ctx.send(embed=embed)  # sends the board (also saves it on board_message)
        player2_invalid_move = False  # checks if player 2 has made an invalid move
        player2_refused_draw = False

        while True:
            if not (player2_invalid_move or player2_refused_draw):
                #  if player 2 makes an invalid move, this block will not execute, thus making player 2 repeat his move
                #  game begins by asking the challenger's move, updating board and then showing the updated board
                #  the line below will get the player's move
                msg = await self.bot.wait_for('message', check=check_for_valid_message1)
                if msg.content.lower() == 'resign':
                    # if the message is 'resign' (sent by any player), the game will end
                    embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                    await board_message.edit(content=f'{msg.author.mention} resigns! The game is over!', embed=embed)
                    break
                if msg.content.lower() == 'draw':
                    # if the message is 'draw' (sent by any player), the bot must wait for the other player's response
                    await board_message.edit(content=f'{msg.author} offers a draw! Type `draw`'
                                             f'in order to accept it or anything else to decline it!', embed=embed)
                    if msg.author == ctx.author:
                        response = await self.bot.wait_for('message', check=lambda m: m.author == challenged)
                        if response.content.lower() == 'draw':
                            await board_message.edit(content=f'The game is a draw!', embed=embed)
                            break
                        else:
                            await board_message.edit(content=f'Draw declined!', embed=embed)
                            continue
                    elif msg.author == challenged:
                        response = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                        if response.content.lower() == 'draw':
                            await board_message.edit(content=f'The game is a draw!', embed=embed)
                            break
                        else:
                            await board_message.edit(content=f'Draw declined!', embed=embed)
                            continue
                try:
                    board.push_san(msg.content)  # updates board
                except ValueError:
                    # player 1 has made an illegal move
                    embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                    await board_message.edit(content=f'{ctx.author.mention} wait, '
                                             f'that\'s illegal! Please, make another move.', embed=embed)
                    await msg.delete()
                    continue
                #  the line below edits bot's message in order to show the updated board and shows his move
                embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                embed.set_footer(text=f'Last move: {msg.content} by white')
                await board_message.edit(embed=embed)
                await msg.delete()  # deletes player's message
                if check_for_draw(board):  # checks if the current position is a draw
                    await ctx.send('The game is a draw!')
                    break
                elif board.is_checkmate():  # checks if the current position is checkmate
                    await ctx.send(f'The game is over! The winner is {ctx.author.mention}.')
                    break
            #  asks for the challenged's move, updates board and then shows the updated board
            #  the line below will get the player's move
            msg2 = await self.bot.wait_for('message', check=check_for_valid_message2)
            if msg2.content.lower() == 'resign':
                # if the message is 'resign' (sent by any player), the game will end
                embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                await board_message.edit(content=f'{msg2.author.mention} resigns! The game is over!', embed=embed)
                break
            if msg2.content.lower() == 'draw':
                # if the message is 'draw' (sent by any player), the bot must wait for the other player's response
                await board_message.edit(content=f'{msg2.author} offers a draw! Type `draw`'
                                         f'in order to accept it or anything else to decline it!', embed=embed)
                if msg2.author == ctx.author:
                    response = await self.bot.wait_for('message', check=lambda m: m.author == challenged)
                    if response.content.lower() == 'draw':
                        await board_message.edit(content=f'The game is a draw!', embed=embed)
                        break
                    else:
                        await board_message.edit(content=f'Draw declined!', embed=embed)
                        player2_refused_draw = True
                        continue
                elif msg2.author == challenged:
                    response = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                    if response.content.lower() == 'draw':
                        await board_message.edit(content=f'The game is a draw!', embed=embed)
                        break
                    else:
                        await board_message.edit(content=f'Draw declined!', embed=embed)
                        player2_refused_draw = True
                        continue
            try:
                player2_invalid_move = False
                player2_refused_draw = False
                board.push_san(msg2.content)  # updates board
            except ValueError:
                # player 2 has made an illegal move
                embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                await board_message.edit(content=f'{challenged.mention} wait, '
                                         f'that\'s illegal! Please, make another move.', embed=embed)
                await msg2.delete()
                player2_invalid_move = True
                continue
            #  the line below edits bot's message in order to show the updated board and shows his move
            embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
            embed.set_footer(text=f'Last move: {msg2.content} by black')
            await board_message.edit(embed=embed)
            await msg2.delete()  # deletes player's message
            if check_for_draw(board):  # checks if the current position is a draw
                await ctx.send('The game is a draw!')
                break
            elif board.is_checkmate():  # checks if the current position is a checkmate
                await ctx.send(f'The game is over! The winner is {challenged.mention}.')
                break


def setup(bot):
    bot.add_cog(Chess(bot))
