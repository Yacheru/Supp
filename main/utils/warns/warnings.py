import discord
import datetime

from bot import bot
from datetime import datetime
from discord import Embed, TextStyle, ButtonStyle, Colour
from discord.ext import commands
from discord.ui import View, Button, Modal, TextInput
from discord.utils import format_dt

from data.postgresql import pcursor


def is_admin(inter: discord.Interaction):
    return inter.user.guild_permissions.administrator 

class WarnModal(Modal, title="Добавить предупреждение"):
    steamid = TextInput(label="Steamid админа:", style=TextStyle.short, placeholder="Формат: STEAM_X:X:XXXXXXXXX",
                        max_length=23)
    inflink = TextInput(label="Профиль админа:", style=TextStyle.short,
                        placeholder="https://infinity-tm.ru/profile/GoddamN", max_length=100)
    docs = TextInput(label="Доказательства на нарушение:", style=TextStyle.short,
                     placeholder="Вставьте ссылку на видео/фото док-во нарушения", required=False, max_length=500)
    warn = TextInput(label="Причина выдачи варна:", style=TextStyle.long, placeholder="Напишите здесь причину варна",
                     max_length=1000)

    async def on_submit(self, inter: discord.Interaction):
        global steamid_value
        global inflink_value
        global warn_value
        global docs_value

        steamid_value = self.steamid.value
        inflink_value = self.inflink.value
        warn_value = self.warn.value
        docs_value = self.docs.value

        em = Embed(title="Подтвердите данные",
                   description=f"- SteamID: **{self.steamid.value}**\n- Ссылка: **{self.inflink.value}**\n- Док-ва: {'**Отсутствуют**' if self.docs.value == '' else f'**{self.docs.value}**'}\n- Предупреждение: **{self.warn.value}**")
        em.set_footer(text="Для отклонения просто скройте это сообщение")

        await inter.response.send_message(embed=em, view=Confirm(), ephemeral=True)


class DeleteModal(Modal, title="Удалить предупреждение"):
    predid = TextInput(label="ID предупреждения:", placeholder="Введите ID предупреждения", max_length=5)

    async def on_submit(self, inter: discord.Interaction):

        pcursor.execute("SELECT * FROM infwarns WHERE id = %s", (self.predid.value,))
        result = pcursor.fetchone()

        if result:
            if result[1] == inter.user.id:
                pcursor.execute("DELETE FROM infwarns WHERE id = %s", (self.predid.value,))
                pcursor.execute("SELECT * FROM infwarns WHERE steam_id = %s", (steamid,))
                result = pcursor.fetchall()

                if result:

                    em = Embed(title="", description="### Найденные предупреждения:", color=Colour.red())

                    for i, values in enumerate(result, start=1):
                        em.add_field(name=f"```Предупреждение {i}:```",
                                     value=f"__ID:__ **{values[0]}**\n- Выдал: <@{values[1]}>\n- SteamID: **{values[2]}**\n- [**INF-профиль**]({values[3]})\n- Док-ва: {'**Отсутствуют**' if values[5] == '' else f'**{values[5]}**'}\n- Предупреждение: **{values[4]}**\n- Выдано: {values[6]}",
                                     inline=True)

                        if i % 2 == 0:
                            em.add_field(name="\u200b", value="\u200b", inline=True)

                    await inter.response.send_message(embed=em, view=DeleteSendModal(), ephemeral=True)
                else:
                    await inter.response.send_message(content=f"Не найдено предупреждений для {steamid}",
                                                      ephemeral=True)
            else:
                await inter.response.send_message("Удалить предупреждение может только тот, кто его выдал.",
                                                  ephemeral=True)
        else:
            await inter.response.send_message("Предупреждение с таким ID не найдено!", ephemeral=True)


class DeleteSendModal(View):
    def __init__(self):
        super().__init__(timeout=None)

        button = Button(label=f"Удалить", style=ButtonStyle.gray, custom_id="delete")
        self.add_item(button)

        async def button_callback(inter: discord.Interaction):
            if is_admin(inter):
                await inter.response.send_modal(DeleteModal())
            else:
                await inter.response.send_message("Вы не можете использовать это взаимодействие!", ephemeral=True)

        button.callback = button_callback


class FindModal(Modal, title="Найти предупреждение"):
    steamid = TextInput(label="Steamid:", placeholder="Формат: STEAM_X:X:XXXXXXXXX", max_length=23)

    async def on_submit(self, inter: discord.Interaction):
        global steamid

        steamid = self.steamid.value

        pcursor.execute("SELECT * FROM infwarns WHERE steam_id = %s", (self.steamid.value,))
        result = pcursor.fetchall()

        if result:
            em = Embed(title="", description="### Найденные предупреждения:", color=Colour.red(),
                       timestamp=datetime.now())
            for i, values in enumerate(result, start=1):
                em.add_field(name=f"```Предупреждение {i}:```",
                             value=f"__ID:__ **{values[0]}**\n- Выдал: <@{values[1]}>\n- SteamID: **{values[2]}**\n- [**INFINITY-профиль**]({values[3]})\n- Док-ва: {'**Отсутствуют**' if values[5] == '' else f'**{values[5]}**'}\n- Предупреждение: **{values[4]}**\n- Выдано: {values[6]}",
                             inline=True)

                if i % 2 == 0:
                    em.add_field(name="\u200b", value="\u200b", inline=True)

            await inter.response.send_message(embed=em, view=DeleteSendModal(), ephemeral=True)
        else:
            await inter.response.send_message(f"Не найдены предупреждения по **{self.steamid.value}**", ephemeral=True)


class Confirm(View):
    def __init__(self):
        super().__init__(timeout=None)

        button = Button(label="Подтвердить", style=ButtonStyle.gray, custom_id="confirm")
        self.add_item(button)

        async def button_callback(inter: discord.Interaction):
            pcursor.execute(
                "INSERT INTO infwarns (giving, steam_id, inf_link, warn, docs, date) VALUES (%s, %s, %s, %s, %s, %s)", (
                    inter.user.id, steamid_value, inflink_value, warn_value, docs_value,
                    format_dt(datetime.now(), style='D')))
            await inter.response.send_message("Данные успешно внесены", ephemeral=True)

        button.callback = button_callback


class GiveWarn(View):
    def __init__(self):
        super().__init__(timeout=None)

        button = Button(label="Внести", style=ButtonStyle.gray, custom_id="give")
        self.add_item(button)

        async def button_callback(inter: discord.Interaction):
            if is_admin(inter):
                await inter.response.send_modal(WarnModal())
            else:
                await inter.response.send_message("Вы не можете использовать эту команду!", ephemeral=True)

        button.callback = button_callback

        button = Button(label="Найти", style=ButtonStyle.gray, custom_id="find")
        self.add_item(button)

        async def button_callback(inter: discord.Interaction):
            await inter.response.send_modal(FindModal())

        button.callback = button_callback


@bot.command()
@commands.has_permissions(administrator=True)
async def warn(ctx: commands.Context):
    await ctx.channel.purge(limit=1)

    em_img = Embed(title="", color=Colour.red())
    em_img.set_image(
        url="https://cdn.discordapp.com/attachments/1129601347352809532/1152052676868182027/00e7f17c937e95bc.png")

    em = Embed(title="Предупреждения Администраторов",
               description="Первая кнопка позволит вам отправить предупреждение администратору, а вторая кнопка поможет вам найти уже существующее предупреждение.",
               color=Colour.red())
    em.set_image(url="https://cdn.discordapp.com/attachments/1111378209934680087/1113885628132765747/invs.png")
    await ctx.send(embeds=[em_img, em], view=GiveWarn())
