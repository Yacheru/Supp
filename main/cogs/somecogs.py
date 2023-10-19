import discord
import openai
import datetime
from discord.ext import commands
from discord import app_commands

from data.postgresql import pcursor
from bot import bot

openai.api_key = "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"

class SomeCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    try:

        @app_commands.command()
        async def ping(self, inter: discord.Interaction):
            bot_ping = round(bot.latency * 1000)
            await inter.response.send_message(f"Пинг бота: **{bot_ping}** ms.", ephemeral=True)


        @app_commands.command(name="aiimg", description="Сгенерировать картинку")
        @app_commands.describe(size='Размер изображения', prompt="Что ты хочешь сгенерировать ?")
        @app_commands.choices(
            size=[
                app_commands.Choice(name='Размер: 256x256', value='256x256'),
                app_commands.Choice(name='Размер: 512x512', value='512x512'),
                app_commands.Choice(name='Размер: 1024x1024', value='1024x1024'),
            ])
        async def aiimg(self, inter: discord.Interaction, prompt: str, size: app_commands.Choice[str]):
            await inter.response.defer(thinking=True)

            response = openai.Image.create(
                prompt=f"{prompt}",
                n=1,
                size=f"{size.value}"
            )

            em = discord.Embed(title="Сгенерированное изображение", description=f">>> {prompt}", timestamp=datetime.datetime.now(), color=discord.Colour.green())
            em.set_author(name=f"{inter.user.name}", icon_url = f"{inter.user.avatar.url if inter.user.avatar else inter.user.default_avatar}")
            em.set_image(url=f"{response['data'][0]['url']}")
            await inter.followup.send(embed=em)
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S, %d/%m')}] [MODER COMMANDS] [ERROR] WITH CODE {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(SomeCommandsCog(bot))