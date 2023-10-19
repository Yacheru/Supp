import discord
import json
import asyncio

from datetime import datetime
from bot import bot
from discord.ext import commands
from discord.utils import get
from discord.ui import *
from discord import TextStyle, Embed, Colour, ButtonStyle, PermissionOverwrite

from data.postgresql import pcursor

async def ticket_create(inter: discord.Interaction, ticket: str):
    podd_logs = bot.get_channel(1151041222299885630)

    em = Embed(title=f"{ticket}", description=f"Тикет на тему: **{ticket}** *создан* пользователем: {inter.user.mention}", color=Colour.from_rgb(88, 101, 242) if ticket == 'Жалоба на игрока' else Colour.from_rgb(78, 80, 88), timestamp=datetime.now())
    await podd_logs.send(embed=em)

class DeleteTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        button = Button(label="Удалить обращение", style=ButtonStyle.red, custom_id="Delete Ticket")
        self.add_item(button)
        async def button_callback(inter: discord.Interaction):
                await inter.channel.delete()
        button.callback = button_callback

class CloseTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        button = Button(label="Закрыть обращение", style=ButtonStyle.gray, custom_id="Close Ticket")
        self.add_item(button)
        async def button_callback(inter: discord.Interaction):
            close = get(inter.guild.categories, id = 1148468634574930052)

            overwrites = {
                inter.guild.default_role: discord.PermissionOverwrite(read_messages = False)}

            await asyncio.gather(
                inter.channel.edit(category=close, overwrites=overwrites), 
                inter.message.edit(embed=(inter.message.embeds[0].set_footer(text=f"Тикет закрыт: {inter.user.name}")), view=DeleteTicket()))

            pcursor.execute("DELETE FROM tickets WHERE channel = %s", (inter.channel.id,))

            await inter.response.send_message("Тикет успешно закрыт!", ephemeral=True)
        button.callback = button_callback
    
class UserСomplaints(Modal, title="Жалоба на игрока"):               
    member = TextInput(label="Ссылка на игрока:", placeholder="Укажите Steam-профиль нарушителя", style=TextStyle.short, max_length=500)
    docs = TextInput(label="Доказательства:", placeholder="Укажите ссылку на фото/видео доказательство нарушения", style=TextStyle.short, max_length=500)
    description = TextInput(label="Что нарушил игрок:", placeholder="Опишите, какое правило нарушил игрок: https://infinity-tm.ru/pages/rules", style=TextStyle.paragraph, max_length=2000)
    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(thinking=True, ephemeral=True)

        open = get(inter.guild.categories, id = 1148468781719490610)

        embed_complaints = Embed(title=f"{self.title}", description=f"**Комментарий заявителя:**\n>>> {self.description.value}", color=Colour.dark_theme(), timestamp=datetime.now())
        embed_complaints.add_field(name="\u200b", value=f"- **Информация:**\n - {self.member.value} *(игрок)*\n - {self.docs.value} *(доказательства)*", inline=True)
        embed_complaints.set_author(name=f"{inter.user.name}", icon_url=f"{inter.user.avatar.url if inter.user.avatar else inter.user.default_avatar}")
        embed_complaints.set_footer(text="Нажмите на кнопку ниже, чтобы закрыть обращение.")
        embed_complaints.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1129601347352809532/1148473215568588893/player_complaints.png")
        embed_complaints.set_image(url="https://cdn.discordapp.com/attachments/1111378209934680087/1113885628132765747/invs.png")

        gl = get(inter.guild.roles, id = 1146225293997117450)
        zam = get(inter.guild.roles, id = 1146225328889536594)
        st = get(inter.guild.roles, id = 1146225443641495562)

        overwrites = {
            inter.guild.default_role: PermissionOverwrite(read_messages = False),
            inter.user: PermissionOverwrite(read_messages = True, attach_files = True),
            gl: PermissionOverwrite(read_messages = True),
            zam: PermissionOverwrite(read_messages = True),
            st: PermissionOverwrite(read_messages = True)
        }

        channel = await inter.guild.create_text_channel(name=f"Обращение: {inter.user.name}", category=open, overwrites=overwrites)    
        await channel.send(content="||<@&-860197500735586325>, <@&-1146225687070523453>||", embed = embed_complaints, view=CloseTicket())

        pcursor.execute("INSERT INTO tickets (user_id, channel) VALUES (%s, %s)", (inter.user.id, channel.id))

        await asyncio.gather(
            inter.followup.send(f"- **Тикет создан**\n - Проследуйте в канал: {channel.mention}", ephemeral=True),
            ticket_create(inter, f"{self.title}"))

class Support(Modal, title="По любым вопросам"):
    description = TextInput(label="Текст:", placeholder="Ваше обращение", style=TextStyle.paragraph, max_length=2000)
    async def on_submit(self, inter: discord.Interaction):
        await inter.response.defer(thinking=True, ephemeral=True)

        open = get(inter.guild.categories, id = 1148468781719490610)

        embed_complaints = Embed(title=f"{self.title}", description=f"**Комментарий заявителя:**\n>>> {self.description.value}", color=Colour.dark_theme(), timestamp=datetime.now())
        embed_complaints.set_author(name=f"{inter.user.name}", icon_url=f"{inter.user.avatar.url if inter.user.avatar else inter.user.default_avatar}")
        embed_complaints.set_footer(text="Нажмите на кнопку ниже, чтобы закрыть обращение.")
        embed_complaints.set_thumbnail(url = "https://cdn.discordapp.com/attachments/1129601347352809532/1149616464718987375/a137c994eeb9f6f2.png")
        embed_complaints.set_image(url="https://cdn.discordapp.com/attachments/1111378209934680087/1113885628132765747/invs.png")

        overwrites = {
            inter.guild.default_role: PermissionOverwrite(read_messages = False),
            inter.user: PermissionOverwrite(read_messages = True, attach_files = True),
        }

        channel = await inter.guild.create_text_channel(name=f"Обращение: {inter.user.name}", category=open, overwrites=overwrites)    
        await channel.send(content="||<@&860197500735586325>, <@&1146225687070523453>||", embed = embed_complaints, view=CloseTicket())

        pcursor.execute("INSERT INTO tickets (user_id, channel) VALUES (%s, %s)", (inter.user.id, channel.id))

        await asyncio.gather(
            inter.followup.send(f"- **Тикет создан**\n - Проследуйте в канал: {channel.mention}", ephemeral=True),
            ticket_create(inter, f"{self.title}"))


class ButtonTicket(View):
    def __init__(self):
        super().__init__(timeout=None)
        
        button = Button(label="Жалоба на игрока", style=ButtonStyle.blurple, custom_id="player-complaints")
        self.add_item(button)       
        async def button_callback(inter: discord.Interaction):
            await inter.response.send_modal(UserСomplaints())
        button.callback = button_callback

        button = Button(label="По любым вопросам", style=ButtonStyle.gray, custom_id="qa")
        self.add_item(button)       
        async def button_callback(inter: discord.Interaction):
            await inter.response.send_modal(Support())
        button.callback = button_callback


@bot.command()
@commands.has_permissions(administrator = True)
async def sup(ctx: commands.Context):
    await ctx.channel.purge(limit = 1)
    embed_support_image = Embed(title="", color=Colour.dark_theme())
    embed_support_image.set_image(url="https://cdn.discordapp.com/attachments/1129601347352809532/1148476569342451752/infinity_support.png")
    
    embed_support = Embed(title="", color=Colour.dark_theme())
    embed_support.set_author(name=f"{ctx.guild.name}", icon_url=f"{ctx.guild.icon.url}")
    embed_support.set_image(url="https://cdn.discordapp.com/attachments/1111378209934680087/1113885628132765747/invs.png")
    embed_support.add_field(name="", value="При создании тикета необходимо предоставлять как можно больше подробной информации, включая видео/скриншоты, ссылки на доказательства и прочее, что может способствовать быстрому рассмотрению тикета\n\nПри создании тикета учитывайте время, в которое вы пишете. Время ответа на ваш тикет зависит от сложности обращения и загруженности администратции.\n\n- [**Жалобы на администраторов**](https://infinity-tm.ru/complaints/)\n- [**Заявки на разбан**](https://infinity-tm.ru/bans/)", inline=False)
    await ctx.send(embeds =[embed_support_image, embed_support], view = ButtonTicket())