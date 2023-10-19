import discord
import requests
import datetime
import os
from discord.ext import tasks, commands
from PIL import Image, ImageDraw, ImageFont
import io

from bot import bot
from data.postgresql import pcursor
from .circle import image

@bot.event
async def on_message(message: discord.Message):

    try:
        if message.author.bot:
            return

        pcursor.execute("SELECT * FROM messages_activity WHERE userID = %s", (message.author.id,))
        user_data = pcursor.fetchone()

        if user_data:
            pcursor.execute("UPDATE messages_activity SET messages_count = messages_count + 1 WHERE userID = %s", (message.author.id,))
        else:
            pcursor.execute("INSERT INTO messages_activity (userID, messages_count) VALUES (%s, 1)", (message.author.id,))
        await bot.process_commands(message)
    except Exception as e:
        print(f"[ON_MESSAGE] [ERROR] WITH CODE {e}")


@tasks.loop(hours=2)
async def update_most_active_user_data():
    try:
        pcursor.execute("SELECT userID, messages_count FROM messages_activity ORDER BY messages_count DESC LIMIT 1")
        user_data = pcursor.fetchone()

        pcursor.execute("SELECT nickname FROM most_msg_activity_user")
        result = pcursor.fetchone()

        if user_data is not None and user_data[1] != 0:
            guild = bot.get_guild(494212272353181726)
            most_active = guild.get_member(user_data[0])

            pcursor.execute("UPDATE messages_activity SET messages_count = 0")

            if most_active:
                nickname = most_active.display_name[:10] + "..." if len(most_active.display_name) > 10 else most_active.display_name
                avatar_url = most_active.avatar.url if most_active.avatar else most_active.default_avatar.url

                if result is None:
                    pcursor.execute("INSERT INTO most_msg_activity_user (nickname, messages_count) VALUES (%s, %s)", (nickname, user_data[1]))
                else:
                    pcursor.execute("UPDATE most_msg_activity_user SET nickname = %s, messages_count = %s WHERE nickname = %s", (nickname, user_data[1], result[0]))

                print("[UPDATE ACTIVE USER] [TASK] [INFO] MOST ACTIVE USER INSERTED AT", datetime.datetime.now().strftime('%H:%M %d/%m/%Y'))
            else:
                pcursor.execute("UPDATE most_msg_activity_user SET nickname = %s, messages_count = %s WHERE nickname = %s", ("Неизвестно", 0, result[0] if result else None))
        else:
            pcursor.execute("UPDATE most_msg_activity_user SET nickname = %s, messages_count = %s WHERE nickname = %s", ("Неизвестно", 0, result[0] if result else None))

        print("[UPDATE ACTIVE USER] [TASK] [INFO] CAN'T INSERT MOST ACTIVE USER AT", datetime.datetime.now().strftime('%H:%M %d/%m/%Y'))
    except Exception as e:
        print("[UPDATE ACTIVE USER] [TASK] [ERROR] WITH CODE", e)


@tasks.loop(minutes=1)
async def update_banner():
    try:
        guild = bot.get_guild(494212272353181726)

        banner_image = Image.open("main/utils/banner/pics/banner.png")
        draw = ImageDraw.Draw(banner_image)

        pcursor.execute("SELECT nickname, messages_count FROM most_msg_activity_user")
        most_active_user = pcursor.fetchone()

        font_large = ImageFont.truetype('main/utils/banner/Aqum 2 Classic.ttf', size=40)
        font_nickname = ImageFont.truetype('main/utils/banner/Aqum 2 Classic.ttf', size=60)

        if most_active_user:
            nickname = most_active_user[0]
            messages_count = most_active_user[1]

            if nickname != "Неизвестно" and messages_count != 0:
                profile_pic = Image.open("main/utils/banner/pics/pfp.png")
                pfpframe = Image.open("main/utils/banner/pics/pfpframe.png")

                banner_image.paste(profile_pic, (150, 300), profile_pic)
                banner_image.paste(pfpframe, (142, 310), pfpframe)

                draw.text((305, 315), f"{nickname}", fill="white", font=font_nickname)
            else:
                draw.text((280, 315), "Неизвестно", fill="white", font=font_large)
        else:
            draw.text((280, 315), "Неизвестно", fill="white", font=font_large)

        member_count = guild.member_count
        voice_count = len([m for m in guild.members if m.voice])

        draw.text((660, 415), f'{member_count}', fill='white', font=font_large)  # Количество участников
        draw.text((705, 275), f'{voice_count}', fill='white', font=font_large)  # Количество участников в голосовом чате

        banner_image.save("main/utils/banner/pics/new_banner.png")

        with open("main/utils/banner/pics/new_banner.png", 'rb') as banner_file:
            banner = banner_file.read()

        await guild.edit(banner=banner)
        print("[UPDATE GUILD BANNER] [TASK] [INFO] BANNER SUCCESSFULLY UPDATED AT", datetime.datetime.now().strftime('%H:%M %d/%m/%Y'))
    except Exception as e:
        print("[UPDATE GUILD BANNER] [TASK] [ERROR] WITH CODE", e)