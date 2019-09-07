from discord.ext import commands
import discord

from bot.bot_client import Bot


class Owner(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.has_permissions(manage_guild=True)
    @commands.command(aliases=['reload'])
    async def reload_cog(self, ctx: commands.Context, cog: str):
        """Reloads a cog"""
        try:
            self.bot.reload_extension(f'bot.cogs.{cog}')
            return await ctx.send(f'Extension {cog} reloaded sucessfully.')
        except ModuleNotFoundError:
            return await ctx.send(f"Extension {cog} does not exist.")
        except Exception as e:
            return await ctx.send(f'Error loading extension {cog}:\n {type(e).__name__} : {e}')

    @commands.has_permissions(manage_guild=True)
    @commands.command(aliases=['reloadall'])
    async def reload_all_cogs(self, ctx: commands.Context):
        """Reloads all cogs"""
        err = await self.bot.reload_all_extensions()
        if err:
            return await ctx.send('Error when reloading extensions. Check the bot logs.')
        return await ctx.send('All extensions were reloaded successfully.')


def setup(bot):
    bot.add_cog(Owner(bot))
