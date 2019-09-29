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
    @commands.command(aliases=['chalenge', 'challeng', 'fight', 'play', 'chaleng'])
    async def challenge(self, ctx: commands.Context, challenged: discord.Member):
        """
        This command !challenge is going to be used in order to challenge a player to a game of chess
        it takes one argument, which is the player, so it should be used like this: !challenge @Player
        """
        def check_challenger_move(message: discord.Message) -> bool:
            """
            This function will verify if the first, third, etc. messages during game are valid
            i.e. it must either be a MOVE sent by the PLAYER 1, or a RESIGN message sent by any player
            or a DRAW message sent by any player
            """
            return (message.author == ctx.author or message.content.lower() in ('resign', 'draw'))

        def check_challenged_move(message: discord.Message) -> bool:
            """
            This function will verify if the second, fourth, etc. messages during game are valid
            i.e. it must either be a MOVE sent by the PLAYER 2, or a RESIGN message sent by any player
            or a DRAW message sent by any player
            """
            return (message.author == challenged or message.content.lower() in ('resign', 'draw'))

        board = Board()  # creates an instance of Board class, which is going to be used during the game

        # sends a message to let the challenged know who challenged them
        await ctx.send(
            f'{challenged.mention}, you\'ve been challenged to a chess game by '
            f'{ctx.message.author.mention}!\n'
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
        player2_invalid_move = False  # checks if player 2 has made an invalid move
        player2_refused_draw = False  # checks if player 2 has refused a draw

        while True:
            if not (player2_invalid_move or player2_refused_draw):
                #  if player 2 makes an invalid move, this block will not execute, thus making player 2 repeat his move
                #  game begins by asking the challenger's move, updating board and then showing the updated board
                #  the line below will get the player's move
                challenger_msg = await self.bot.wait_for('message', check=check_challenger_move)

                if challenger_msg.content.lower() == 'resign':
                    # if the message is 'resign' (sent by any player), the game will end
                    return await ctx.send(f'{challenger_msg.author.mention} resigns! The game is over!')
                if challenger_msg.content.lower() == 'draw':
                    # if the message is 'draw' (sent by any player), the bot must wait for the other player's response
                    await board_message.edit(content=f'{challenger_msg.author.mention} offers a draw! Type `draw`'
                                             f' in order to accept it or anything else to decline it!', embed=embed)
                    bot_message = await ctx.send(f'{challenger_msg.author.mention} offers a draw! Type `draw` '
                                                 f'in order to accept it or anything else to decline it!')

                    # if message's author is equal to whoever sent the challenge
                    if challenger_msg.author == ctx.author:
                        # waits for other player's response
                        response = await self.bot.wait_for('message', check=lambda m: m.author == challenged)
                        if response.content.lower() == 'draw':  # if the response is draw then the game draws
                            await board_message.edit(content=f'The game is a draw!', embed=embed)
                            return await ctx.send('The game is a draw!')
                        else:
                            # if the response is not draw then the game continues
                            await board_message.edit(content=f'Draw declined!', embed=embed)
                            await bot_message.delete()
                            await response.delete()
                            await challenger_msg.delete()
                            continue
                    elif challenger_msg.author == challenged:  # if message's author is equal to the challenged person
                        # waits for other player's response
                        response = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                        if response.content.lower() == 'draw':  # if the response is draw then the game draws
                            await board_message.edit(content=f'The game is a draw!', embed=embed)
                            return await ctx.send('The game is a draw!')
                        else:
                            # if the response is not draw then the game continues
                            await board_message.edit(content=f'Draw declined!', embed=embed)
                            await bot_message.delete()
                            await response.delete()
                            await challenger_msg.delete()
                            continue
                try:
                    board.push_san(challenger_msg.content)  # updates board
                except ValueError:
                    # player 1 has made an illegal move
                    embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                    await board_message.edit(content=self.illegal_msg(ctx.author), embed=embed)
                    await challenger_msg.delete()
                    continue

                #  the line below edits bot's message in order to show the updated board and shows his move
                embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                embed.set_footer(text=f'Last move: {challenger_msg.content} by white')
                await board_message.edit(content='', embed=embed)
                await challenger_msg.delete()  # deletes player's message
                if board.is_drawn():  # checks if the current position is a draw
                    return await ctx.send('The game is a draw!')
                elif board.is_checkmate():  # checks if the current position is checkmate
                    return await ctx.send(self.game_over_msg(winner=ctx.author))

            #  asks for the challenged's move, updates board and then shows the updated board
            #  the line below will get the player's move
            challenged_msg = await self.bot.wait_for('message', check=check_challenged_move)

            if challenged_msg.content.lower() == 'resign':
                # if the message is 'resign' (sent by any player), the game will end
                return await ctx.send(f'{challenged_msg.author.mention} resigns! The game is over!')

            if challenged_msg.content.lower() == 'draw':
                # if the message is 'draw' (sent by any player), the bot must wait for the other player's response
                draw_msg = (
                    f'{challenged_msg.author.mention} offers a draw! Type `draw`'
                    f' in order to accept it or anything else to decline it!'
                )
                await board_message.edit(content=draw_msg, embed=embed)
                bot_message = await ctx.send(draw_msg)

                if challenged_msg.author == ctx.author:  # if message's author is equal to whoever sent the challenge
                    # gets response from the other player
                    response = await self.bot.wait_for('message', check=lambda msg: msg.author == challenged)

                    if response.content.lower() == 'draw':  # if response is draw then the game draws
                        await board_message.edit(content=f'The game is a draw!', embed=embed)
                        return await ctx.send('The game is a draw!')
                    else:  # if response is not draw then the game continues
                        await board_message.edit(content=f'Draw declined!', embed=embed)
                        await challenged_msg.delete()
                        await response.delete()
                        await bot_message.delete()
                        player2_refused_draw = True
                        continue
                elif challenged_msg.author == challenged:  # if message's author is equal to challenged player
                    # gets response from the other player
                    response = await self.bot.wait_for('message', check=lambda m: m.author == ctx.author)
                    if response.content.lower() == 'draw':  # if response is draw then the game draws
                        await board_message.edit(content=f'The game is a draw!', embed=embed)
                        return await ctx.send('The game is a draw!')
                    else:  # if response is not draw then the game continues
                        await board_message.edit(content=f'Draw declined!', embed=embed)
                        await challenged_msg.delete()
                        await response.delete()
                        await bot_message.delete()
                        player2_refused_draw = True
                        continue
            try:
                player2_invalid_move = False
                player2_refused_draw = False
                board.push_san(challenged_msg.content)  # updates board
            except ValueError:
                # player 2 has made an illegal move
                embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
                await board_message.edit(content=self.illegal_msg(challenged), embed=embed)
                await challenged_msg.delete()
                player2_invalid_move = True
                continue

            #  the line below edits bot's message in order to show the updated board and shows his move
            embed.set_image(url=f'http://www.fen-to-image.com/image/{board.fen().split()[0]}')  # updates image
            embed.set_footer(text=f'Last move: {challenged_msg.content} by black')
            await board_message.edit(content='', embed=embed)
            await challenged_msg.delete()
            if board.is_drawn():
                return await ctx.send('The game is a draw!')
            elif board.is_checkmate():
                return await ctx.send(self.game_over_msg(winner=challenged))


def setup(bot):
    bot.add_cog(Chess(bot))
