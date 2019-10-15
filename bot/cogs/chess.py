import chess
from discord.ext import commands
import discord
from bot.bot_client import Bot


class Board(chess.Board):
    def is_drawn(self) -> bool:
        """
        Function checks for stalemate/insufficient material/threefold repetition/fifty moves rule
        """
        return any([
            self.is_insufficient_material(), self.can_claim_threefold_repetition(),
            self.can_claim_fifty_moves(), self.is_stalemate()
        ])


class Chess(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

    def illegal_msg(self, player: discord.Member) -> str:
        return f'{player.mention} wait, that\'s illegal! Please, make another move.'

    def game_over_msg(self, winner: discord.Member) -> str:
        return f'The game is over! The winner is {winner.mention}.'

    @commands.has_permissions(manage_channels=True)
    @commands.command(aliases=['chalenge', 'challeng', 'fight', 'challenge', 'chaleng'])
    async def play(self, ctx: commands.Context, white_player: discord.Member, black_player: discord.Member):
        """
        This command !play is going to be used in order to start a game of chess between both players.
        First name is white, second name is black. It should be used like this: !play @Player1 @Player2
        """
        if ctx.author not in (white_player, black_player):
            return await ctx.send('You can only start a game if you are a player yourself.')

        def check_white_move(message: discord.Message) -> bool:
            """
            This function will verify if the first, third, etc. messages during game are valid
            i.e. it must either be a MOVE sent by the white_player, or a RESIGN message sent by any player
            or a DRAW message sent by any player
            """
            return (message.author == white_player or message.content.lower() in ('resign', 'draw'))

        def check_black_move(message: discord.Message) -> bool:
            """
            This function will verify if the second, fourth, etc. messages during game are valid
            i.e. it must either be a MOVE sent by the black_player, or a RESIGN message sent by any player
            or a DRAW message sent by any player
            """
            return (message.author == black_player or message.content.lower() in ('resign', 'draw'))

        board = Board()  # creates an instance of Board class, which is going to be used during the game

        # sends a message to let the players know about their pieces' color
        await ctx.send(
            f'{white_player.mention} will play with white pieces and '
            f'{black_player.mention} plays with black pieces!\n'
            f'Check out the board below:\n'
        )

        embed = discord.Embed(color=0x0473b3)  # creates embed
        embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # sets board image
        embed.add_field(
            name='Special words:',
            value='\n**`resign`**: resigns the game'
            f'\n**`draw`**: offers/accepts draw'
        )

        board_message = await ctx.send(embed=embed)  # sends the board (also saves it on board_message)
        black_invalid_move = False  # checks if black_player has made an invalid move
        black_refused_draw = False  # checks if black_player has refused a draw

        while True:
            if not (black_invalid_move or black_refused_draw):
                #  if player 2 makes an invalid move, this block will not execute, thus making player 2 repeat his move
                #  game begins by asking the white's move, updating board and then showing the updated board
                #  the line below will get the player's move
                white_msg = await self.bot.wait_for('message', check=check_white_move)

                if white_msg.content.lower() == 'resign':
                    # if the message is 'resign' (sent by any player), the game will end
                    return await ctx.send(f'{white_msg.author.mention} resigns! The game is over!')
                if white_msg.content.lower() == 'draw':
                    # if the message is 'draw' (sent by any player), the bot must wait for the other player's response
                    await board_message.edit(content=f'{white_msg.author.mention} offers a draw! Type `draw`'
                                             f' in order to accept it or anything else to decline it!', embed=embed)
                    bot_message = await ctx.send(f'{white_msg.author.mention} offers a draw! Type `draw` '
                                                 f'in order to accept it or anything else to decline it!')

                    # if message's author is equal to whoever sent the challenge
                    if white_msg.author == white_player:
                        # waits for other player's response
                        response = await self.bot.wait_for('message', check=lambda m: m.author == black_player)
                        if response.content.lower() == 'draw':  # if the response is draw then the game draws
                            await board_message.edit(content=f'The game is a draw!', embed=embed)
                            return await ctx.send('The game is a draw!')
                        else:
                            # if the response is not draw then the game continues
                            await board_message.edit(content=f'Draw declined!', embed=embed)
                            await bot_message.delete()
                            await response.delete()
                            await white_msg.delete()
                            continue
                    elif white_msg.author == black_player:  # if message's author is equal to the challenged person
                        # waits for other player's response
                        response = await self.bot.wait_for('message', check=lambda m: m.author == white_player)
                        if response.content.lower() == 'draw':  # if the response is draw then the game draws
                            await board_message.edit(content=f'The game is a draw!', embed=embed)
                            return await ctx.send('The game is a draw!')
                        else:
                            # if the response is not draw then the game continues
                            await board_message.edit(content=f'Draw declined!', embed=embed)
                            await bot_message.delete()
                            await response.delete()
                            await white_msg.delete()
                            continue
                try:
                    board.push_san(white_msg.content)  # updates board
                except ValueError:
                    # player 1 has made an illegal move
                    embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                    await board_message.edit(content=self.illegal_msg(white_player), embed=embed)
                    await white_msg.delete()
                    continue

                #  the line below edits bot's message in order to show the updated board and shows his move
                embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                embed.set_footer(text=f'Last move: {white_msg.content} by white')
                await board_message.edit(content='', embed=embed)
                await white_msg.delete()  # deletes player's message
                if board.is_drawn():  # checks if the current position is a draw
                    return await ctx.send('The game is a draw!')
                elif board.is_checkmate():  # checks if the current position is checkmate
                    return await ctx.send(self.game_over_msg(winner=ctx.author))

            #  asks for the challenged's move, updates board and then shows the updated board
            #  the line below will get the player's move
            black_msg = await self.bot.wait_for('message', check=check_black_move)

            if black_msg.content.lower() == 'resign':
                # if the message is 'resign' (sent by any player), the game will end
                return await ctx.send(f'{black_msg.author.mention} resigns! The game is over!')

            if black_msg.content.lower() == 'draw':
                # if the message is 'draw' (sent by any player), the bot must wait for the other player's response
                draw_msg = (
                    f'{black_msg.author.mention} offers a draw! Type `draw`'
                    f' in order to accept it or anything else to decline it!'
                )
                await board_message.edit(content=draw_msg, embed=embed)
                bot_message = await ctx.send(draw_msg)

                if black_msg.author == white_player:  # if message's author is equal to whoever sent the challenge
                    # gets response from the other player
                    response = await self.bot.wait_for('message', check=lambda msg: msg.author == black_player)

                    if response.content.lower() == 'draw':  # if response is draw then the game draws
                        await board_message.edit(content=f'The game is a draw!', embed=embed)
                        return await ctx.send('The game is a draw!')
                    else:  # if response is not draw then the game continues
                        await board_message.edit(content=f'Draw declined!', embed=embed)
                        await black_msg.delete()
                        await response.delete()
                        await bot_message.delete()
                        black_refused_draw = True
                        continue
                elif black_msg.author == black_player:  # if message's author is equal to challenged player
                    # gets response from the other player
                    response = await self.bot.wait_for('message', check=lambda m: m.author == white_player)
                    if response.content.lower() == 'draw':  # if response is draw then the game draws
                        await board_message.edit(content=f'The game is a draw!', embed=embed)
                        return await ctx.send('The game is a draw!')
                    else:  # if response is not draw then the game continues
                        await board_message.edit(content=f'Draw declined!', embed=embed)
                        await black_msg.delete()
                        await response.delete()
                        await bot_message.delete()
                        black_refused_draw = True
                        continue
            try:
                black_invalid_move = False
                black_refused_draw = False
                board.push_san(black_msg.content)  # updates board
            except ValueError:
                # player 2 has made an illegal move
                embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                await board_message.edit(content=self.illegal_msg(black_player), embed=embed)
                await black_msg.delete()
                black_invalid_move = True
                continue

            #  the line below edits bot's message in order to show the updated board and shows his move
            embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
            embed.set_footer(text=f'Last move: {black_msg.content} by black')
            await board_message.edit(content='', embed=embed)
            await black_msg.delete()
            if board.is_drawn():
                return await ctx.send('The game is a draw!')
            elif board.is_checkmate():
                return await ctx.send(self.game_over_msg(winner=black_player))


def setup(bot):
    bot.add_cog(Chess(bot))
