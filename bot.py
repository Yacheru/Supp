import json
import discord
import dotenv
import os

from discord.ext import commands

with open('config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()

        super().__init__(
            command_prefix=commands.when_mentioned_or(f'{cfg["BOT"]["prefix"]}'),
            intents=intents,
            activity=discord.Activity(
                type = 5, 
                name="SUPPORT"), 
            help_command=None)

    async def setup_hook(self):
        from main.utils.banner.statbanner import update_banner, update_most_active_user_data

        from main.utils.boost import ButtonBoost
        from main.tickets.tickets import DeleteTicket, CloseTicket, ButtonTicket
        from main.utils.warns.warnings import GiveWarn
        
        self.add_view(ButtonBoost())
        self.add_view(DeleteTicket())
        self.add_view(ButtonTicket())
        self.add_view(CloseTicket())
        self.add_view(GiveWarn())

        update_most_active_user_data.start()
        update_banner.start()

        for filename in os.listdir("main/cogs"):
            if filename.endswith("py"):
                await self.load_extension(f"main.cogs.{filename[:-3]}")
    
    async def on_ready(self):
        await self.tree.sync()

dotenv.load_dotenv()
TOKEN = cfg['BOT']['TOKEN']
bot = Bot()