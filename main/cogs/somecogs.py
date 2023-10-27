import discord
import openai
import datetime
import json
from discord.ext import commands
from discord import app_commands

from data.postgresql import pcursor
from bot import bot

with open('config.json', 'r', encoding='utf-8') as f:
    cfg = json.load(f)

openai.api_key = cfg['BOT']['GPTTOKEN']

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

        @app_commands.command(name="usermsgclear", description="Убрать сообщения пользователя из дб")
        @app_commands.describe(user="Выберете пользователя", count="Количество удаляемых сообщений")
        async def clear(inter: discord.Interaction, user: discord.Member, count: int):
            try:
                pcursor.execute("SELECT userID, messages_count FROM messages_activity WHERE userID = %s", (user.id,))
                user_data = pcursor.fetchone()

                if user_data:
                    user_id, current_count = user_data

                    if count > current_count:
                        await inter.response.send_message("Указанное количество сообщений для удаления больше, чем имеющееся количество.", ephemeral=True)
                    else:
                        new_count = current_count - count

                        pcursor.execute("UPDATE messages_activity SET messages_count = %s WHERE userID = %s", (new_count, user_id))

                        await inter.response.send_message(f"У пользователя {user.mention} было удалено {count} сообщений. Теперь у него {new_count} сообщений.", ephemeral=True)
                else:
                    await inter.response.send_message("Такого пользователя нет", ephemeral=True)
            except Exception as e:
                print(f"[COMMAND] [ERROR] WITH CODE {e}")
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S, %d/%m')}] [MODER COMMANDS] [ERROR] WITH CODE {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(SomeCommandsCog(bot))