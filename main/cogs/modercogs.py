import datetime
import discord
import json
import re

from discord.ext import commands
from discord.utils import utcnow
from discord import Embed, Colour, app_commands

from bot import bot
from data.postgresql import pcursor


with open("config.json", "r") as f:
    cfg = json.load(f)


date = datetime.datetime.now().strftime('%d/%m/%Y %H:%M')

class ModerCommandsCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    try:
        @app_commands.command(name="clear", description="Очистить определённое количество сообщение из чата")
        async def clear(self, inter: discord.Interaction, count: int):
            await inter.response.defer(thinking=True, ephemeral=True)
            msg = await inter.channel.purge(limit=int(count))
            if len((msg)) == 0:
                embed_clear = discord.Embed(title="", description=f"Ничего не удалено c <#{inter.channel.id}>", timestamp=datetime.datetime.now(), color=discord.Colour.green())
            else:
                embed_clear = discord.Embed(title="", description=f"Успешно удалено **{len(msg)}** сообщений c <#{inter.channel.id}>", timestamp=datetime.datetime.now(), color=discord.Colour.green())

            embed_clear.set_author(name=f"{inter.user.name}#{inter.user.discriminator}", icon_url=f"{inter.user.avatar.url}")
            embed_clear.set_thumbnail(url=inter.user.avatar.url)
            embed_clear.set_footer(text=f"{inter.guild.name}", icon_url=f"{inter.guild.icon.url}")

            if len((msg)) == 0:
                await inter.followup.send(f"Ничего не удаленно", ephemeral=True)
            else:
                await inter.followup.send(f"Удаленно", ephemeral=True) 
            channel = bot.get_channel(1154281203986354217)
            await channel.send(embed=embed_clear)


        @app_commands.command(name="mute", description="Отправить участника в Тайм-Аут")
        async def mute(self, inter: discord.Interaction, user: discord.Member, time: str, reason: str):
            time_values = re.findall(r"(\d+)([hmd])", time)
            if not time_values:
                await inter.response.send_message("Неверный формат времени.", ephemeral=True)
                return

            delta = datetime.timedelta()
            for amount, unit in time_values:
                amount = int(amount)
                if unit == "h":
                    delta += datetime.timedelta(hours=amount)
                elif unit == "m":
                    delta += datetime.timedelta(minutes=amount)
                elif unit == "d":
                    delta += datetime.timedelta(days=amount)
                else:
                    await inter.response.send_message("Неверный формат времени.", ephemeral=True)
                    return

            end_time = utcnow() + delta
            await user.edit(timed_out_until=end_time, reason=reason)

            embed_timeout = discord.Embed(title="<:timeout:1113547982764261438> Добавление Тайм-аута", color=discord.Color.red(), timestamp=datetime.datetime.now())
            embed_timeout.add_field(name="Модератор:", value=inter.user.mention)
            embed_timeout.add_field(name="Время:", value=time, inline=True)
            embed_timeout.add_field(name="Участник:", value=f"{user.mention}\n({user.id})")
            embed_timeout.add_field(name="По причине:", value=reason, inline=True)
            embed_timeout.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            try:
                logs = bot.get_channel(cfg["MOD"]["logs"])
                await logs.send(embed=embed_timeout)
                await inter.response.send_message(f"Пользователь {user.mention} был отправлен подумать о своём поведении", ephemeral=True)
            except Exception as e:
                print(e)


        @app_commands.command(name="unmute", description="Снять Тайм-Аут с участника")
        async def unmute(self, inter: discord.Interaction, user: discord.Member):
            await user.edit(timed_out_until=None, reason=None)

            embed_timeout = discord.Embed(title="<:untimeout:1113584329130524712> Снятие Тайм-аута", color=discord.Color.green(), timestamp=datetime.datetime.now())
            embed_timeout.add_field(name="Модератор:", value=inter.user.mention)
            embed_timeout.add_field(name="Участник:", value=f"{user.mention}\n{user.id}")
            embed_timeout.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url) 
            embed_timeout.set_footer(text=f"{inter.guild.name}", icon_url=f"{inter.guild.icon.url}")

            try:
                logs = bot.get_channel(cfg["MOD"]["logs"])
                await logs.send(embed=embed_timeout)
                await inter.response.send_message(f"С пользователя {user.mention} было снято наказание", ephemeral=True)
            except Exception as e:
                print(e)
                await inter.response.send_message(f"Произошла ошибка при снятии наказания с пользователя {user.mention}({user.id})", ephemeral=True)
                
        @app_commands.command(name="kick", description="Исключить пользователя")
        async def kick(self, inter: discord.Interaction, user: discord.Member, reason: str):
            await user.kick(reason=reason)

            embed_kick = discord.Embed(title="<:ban:1113647045861978162> Кик", color=discord.Colour.red(), timestamp=datetime.datetime.now())
            embed_kick.add_field(name="Модератор:", value=inter.user.mention)
            embed_kick.add_field(name="Пользователь:", value=f"{user.mention}\n{user.id}", inline=True)
            embed_kick.add_field(name="По причине:", value=reason, inline=True)
            embed_kick.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            embed_kick.set_footer(text=f"{inter.guild.name}", icon_url=inter.guild.icon.url)

            try:
                logs = bot.get_channel(cfg["MOD"]["logs"])
                await logs.send(embed=embed_kick)
                await inter.response.send_message(f"Пользователь {user.mention} был кикнут", ephemeral=True)
            except Exception as e:
                print(e)
                await inter.response.send_message(f"Произошла ошибка при кике пользователя {user.mention}({user.id})", ephemeral=True)
                    
                    
        @app_commands.command(name="ban", description="Забанить участника")
        async def ban(self, inter: discord.Interaction, user: discord.Member, reason: str):
            if user:
                await user.ban(delete_message_days=7, reason=reason)

                embed_ban = discord.Embed(title="<:ban:1113647045861978162> Бан", color=discord.Colour.red(), timestamp=datetime.datetime.now())
                embed_ban.add_field(name="Модератор:", value=inter.user.mention)
                embed_ban.add_field(name="Пользователь:", value=f"{user.mention}\n{user.id}", inline=True)
                embed_ban.add_field(name="По Причине:", value=reason, inline=True)
                embed_ban.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
                embed_ban.set_footer(text=f"{inter.guild.name}", icon_url=inter.guild.icon.url)

                try:
                    logs = bot.get_channel(cfg["MOD"]["logs"])
                    await logs.send(embed=embed_ban)
                    await inter.response.send_message(f"Пользователь {user.mention} был забанен", ephemeral=True)
                except Exception as e:
                    print(e)
                    await inter.response.send_message(f"Произошла ошибка при бане пользователя {user.mention}({user.id})", ephemeral=True)
        
                
        @app_commands.command(name="warn", description="Предупредить пользователя")
        async def warn(self, inter: discord.Interaction, user: discord.Member, reason: str):
            pcursor.execute("INSERT INTO moderation VALUES (%s, %s, %s, %s)", (user.id, inter.guild.id, reason, date))
            
            pcursor.execute("SELECT reason FROM moderation WHERE user_id = %s AND guild_id = %s", (user.id, inter.guild.id))
            result = pcursor.fetchall()
            
            em_warn = Embed(title="Предупреждение", timestamp=datetime.datetime.now(), color=Colour.red())
            em_warn.add_field(name="Модератор:", value=f"{inter.user.mention}")
            em_warn.add_field(name="Пользователь:", value=f"{user.mention}")
            em_warn.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)
            em_warn.add_field(name="Предупреждение:", value=f"{reason} (Всего: {len(result)})")
            em_warn.set_footer(text=f"{inter.guild.name}", icon_url=f"{inter.guild.icon.url}")
            
            await inter.response.send_message(embed=em_warn)


        @app_commands.command(name="warns", description="Посмотреть предупреждения пользователя")
        async def warnings(self, inter: discord.Interaction, user: discord.Member):
            
            pcursor.execute("SELECT reason FROM moderation WHERE user_id = %s AND guild_id = %s", (user.id, inter.guild.id))
            result = pcursor.fetchall()
            
            em_warnings = Embed(title="Предупреждения пользователя:", timestamp=datetime.datetime.now(), color=Colour.yellow())
            em_warnings.add_field(name="Пользователь:", value=f"{user.mention}")
            em_warnings.set_footer(text=f"{inter.guild.name}", icon_url=f"{inter.guild.icon.url}")
            em_warnings.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)   
            if len(result) == 0:
                em_warnings.add_field(name="Предупреждения:",value="У данного пользователя нет предупреждений.")
            else:
                reasons = [row[0] for row in result]
                em_warnings.add_field(name="Предупреждения:", value=', '.join(reasons) + f" Всего: ({len(result)})")
            await inter.response.send_message(embed=em_warnings)
                
                
        @app_commands.command(name="warnclear", description="Очистить предупреждения у пользователя")
        async def clear_warnings(self, inter: discord.Interaction, user: discord.Member):
            pcursor.execute("DELETE FROM moderation WHERE user_id = ? AND guild_id = ?", (user.id, inter.guild.id))
            
            pcursor.execute("SELECT reason FROM moderation WHERE user_id = ? AND guild_id = ?", (user.id, inter.guild.id))
            result = pcursor.fetchall()
            
            em_clear_warns = Embed(title="Очистка предупреждений", color=discord.Colour.green(), timestamp=datetime.datetime.now())
            em_clear_warns.add_field(name="Модератор:", value=inter.user.mention)
            em_clear_warns.add_field(name="Пользователь:", value=user.mention)
            em_clear_warns.set_footer(text=f"{inter.guild.name}", icon_url=f"{inter.guild.icon.url}")
            em_clear_warns.set_thumbnail(url=user.avatar.url if user.avatar else user.default_avatar.url)   
            if len(result) == 0:
                em_clear_warns.add_field(name="Предупреждения:", value="Теперь у пользователя нет предупреждений")         
            await inter.response.send_message(embed=em_clear_warns)

      
        @app_commands.command(name="allwarns", description="Вывести список всех предупреждений")
        async def all_warnings(self, inter: discord.Interaction):
            pcursor.execute("SELECT user_id, reason, date FROM moderation")
            results = pcursor.fetchall()

            if results:
                user_reasons = {}
                for user_id, reason, date in results:
                    user = bot.get_user(user_id)
                    if user not in user_reasons:
                        user_reasons[user] = []
                    user_reasons[user].append((reason, date))

                em_all_warnings = Embed(title="Список всех предупреждений", timestamp=datetime.datetime.now(), color=Colour.blue())
                for user, reasons in user_reasons.items():
                    reasons_text = '\n'.join([f"Предупреждение: {reason}\nДата: `{date}`\n" for reason, date in reasons])
                    em_all_warnings.add_field(name="Пользователь:", value=f"{user.mention}\n{reasons_text}", inline=False)
                em_all_warnings.set_footer(text=f"{inter.guild.name}", icon_url=f"{inter.guild.icon.url}")
                em_all_warnings.set_thumbnail(url=f"{inter.guild.icon.url}")

                await inter.response.send_message(embed=em_all_warnings)
            else:
                await inter.response.send_message('В базе данных нет предупреждений.')
    except Exception as e:
        print(f"[{datetime.datetime.now().strftime('%H:%M:%S, %d/%m')}] [MODER COMMANDS] [ERROR] WITH CODE {e}")

async def setup(bot: commands.Bot):
    await bot.add_cog(ModerCommandsCog(bot))