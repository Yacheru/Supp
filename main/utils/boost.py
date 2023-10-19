import discord
import requests
import re
from bot import bot
from discord import Embed, Colour, ButtonStyle, TextStyle
from discord.ext import commands
from discord.utils import get
from discord.ui import View, Button, Modal, TextInput

from data.postgresql import pcursor

class ModalBoostRole(Modal, title="Создание роли"):
    role_name = TextInput(label="Название роли", placeholder="Введите название будущей роли сюда", style = TextStyle.short, max_length=99)
    role_color = TextInput(label="Цвет роли", placeholder="Укажите цвет роли в HEX-формате (Пример: #ff0000)", style = TextStyle.short, max_length=7)
    role_icon = TextInput(label="Укажите ссылку на желаемую иконку роли", placeholder="https://example.com/example.png", style=TextStyle.short)

    async def on_submit(self, inter: discord.Interaction):
        role_color_value = self.role_color.value
        try:
            role_color_int = int(role_color_value[1:], 16)
        except ValueError as e:
            await inter.response.send_message("Некорректно указан цвет роли [HEX](https://htmlcolorcodes.com/color-picker/) (Пример: #ff0000).Если вы уверены, что это сообщение ошибочное, обратитесь к <@554089377446494248>", ephemeral=True)
            return
        
        if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', role_color_value):
            await inter.response.send_message(content=f"{inter.user.mention} Некорректный формат цвета роли. Укажите цвет в формате [HEX](https://htmlcolorcodes.com/color-picker/) (Пример: #ff0000)\nЕсли вы уверены, что это сообщение ошибочное, обратитесь к <@554089377446494248>", ephemeral=True)
            return
        
        try:
            new_role = await inter.guild.create_role(name=f"{self.role_name.value}", colour=discord.Color(role_color_int), mentionable=False, hoist=True)
            
            role_icon_url = self.role_icon.value
            if role_icon_url:
                if role_icon_url.endswith(('.png', '.jpeg', '.jpg')):
                    response = requests.get(role_icon_url)
                    if response.status_code == 200:
                        icon_data = response.content
                        await new_role.edit(display_icon=icon_data)
                else:
                    await new_role.delete()
                    await inter.response.send_message(content=f"{inter.user.mention} Неверный формат указанной ссылки на иконку для роли. Поддерживаемые форматы: **.png**, **.jpeg**, **.jpg**\n> `https://example.com/example.png`", ephemeral=True)
                    return
            
            await inter.user.add_roles(new_role)
            await inter.response.send_message(content=f"{inter.user.mention} Роль {new_role.mention} Успешно создана и добавлена вам!\nДля каких-либо изменений роли, пишите - <@554089377446494248>", ephemeral=True)

            user_id = inter.user.id
            pcursor.execute("INSERT INTO boost (user_id, role_id) VALUES (%s, %s)", (user_id, new_role.id,))

        except discord.HTTPException as e:
            await inter.response.send_message(content=f"Ошибка при создании роли: {e}. Проверьте правильность указанных данных или обратитесь к <@554089377446494248>", ephemeral=True)

class ModalBoostVIP(Modal, title="Получение VIP"):
    profile_link = TextInput(label="Профиль INFINITY:", placeholder="https://infinity-tm.ru/profile/", style=TextStyle.short)
    steam_link = TextInput(label="Профиль STEAM:", placeholder="https://steamcommunity.com/id/", style=TextStyle.short)
    servers = TextInput(label="Сервера:", placeholder="Выберeте желаемые сервера получения VIP.", style=TextStyle.paragraph)
    async def on_submit(self, inter: discord.Interaction):
        yacheru = await bot.fetch_user(554089377446494248)
        em_vip = Embed(title=f"Получение VIP - {inter.user.name}", description=f"<a:dot:1113242361510772786> {self.profile_link.value}\n<a:dot:1113242361510772786> {self.steam_link.value}\n<a:dot:1113242361510772786> {self.servers.value}")
        await yacheru.send(embed=em_vip)
        await inter.response.send_message("Заявка на получение VIP отправленно, ожидайте получения услуги у себя в профиле infinity", ephemeral=True)

class ButtonBoost(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        button = Button(label="Получить VIP", style=ButtonStyle.blurple, custom_id="take-vip")
        self.add_item(button)       
        async def button_callback(inter: discord.Interaction):
            boost = get(inter.guild.roles, id = 853277261960577084)

            if boost in inter.user.roles:
                await inter.response.send_modal(ModalBoostVIP())
            else:
                await inter.response.send_message(f"У вас нет роли: {boost.mention}", ephemeral=True)
        button.callback = button_callback

@bot.command(name="boost")
@commands.has_permissions(administrator = True)
async def boost(ctx: commands.Context):
    await ctx.channel.purge(limit = 1)
    em_boost_image = Embed(title="", color=Colour.dark_theme())
    em_boost_image.set_image(url="https://cdn.discordapp.com/attachments/1129601347352809532/1146300233245007933/159f5b00ef741e58.png")

    em_boost = Embed(title="<a:boost:1113257580970639421> Бустинг сервера", description="> Привилегии и возможности за буст сервера.", color=Colour.dark_theme())
    em_boost.add_field(name="Привилегии и дополнительные возможности:", value="\n<a:dot:1113242361510772786> Роль <@&853277261960577084> с доп. возможностями.\n<a:dot:1113242361510772786> Отображение отдельно от других участников\n<a:dot:1113242361510772786> 300.000<:inf_coin:1146236826252742690> экономической валюты Akemi\n<a:dot:1113242361510772786> Услуга VIP на 3 месяца")
    em_boost.add_field(name="Полезное:", value="• [__ЧаВо по бустам сервера__](https://support.discord.com/hc/ru/articles/360028038352-%D0%A7%D0%B0%D0%92%D0%BE-%D0%BF%D0%BE-%D0%B1%D1%83%D1%81%D1%82%D0%B0%D0%BC-%D1%81%D0%B5%D1%80%D0%B2%D0%B5%D1%80%D0%B0-)", inline = False)
    em_boost.set_thumbnail(url=f"{ctx.guild.icon.url}")
    em_boost.set_image(url="https://i.imgur.com/8M30d4r.png")
    em_boost.set_footer(text=f"INFINITY-TM 〡 После бустинга нажмите на кнопку ниже.", icon_url=f"{ctx.guild.icon.url}")
    await ctx.send(embeds = [em_boost_image, em_boost], view = ButtonBoost())