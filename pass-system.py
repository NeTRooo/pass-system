# Импорты дискорда
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands, tasks
from nextcord import Webhook
import nextcord
import asyncio
import aiohttp
# Импорты настроек бота
from settings import pass_system, rcon, webhooks2  # Получаем настройки из файла
# Импорты вспомогательных библиотек
import datetime
import sqlite3  # БД которая используется в коде
from mcrcon import MCRcon  # RCON консоль

db = sqlite3.connect('pass-system.sqlite3')
sql = db.cursor()

heylon_db = sqlite3.connect('heylon.sqlite3')
heylon_sql = heylon_db.cursor()

client = commands.AutoShardedBot(shard_count=1, command_prefix='+', intents=nextcord.Intents.all())
client.remove_command('help')

def get_player_nick(channel_id):
    for pl_nick in sql.execute(f"SELECT nick FROM pass_info WHERE channel_id = {channel_id}"):
        pl_nick = pl_nick[0]
    return pl_nick

def get_player_id(channel_id):
    for player_id in sql.execute(f"SELECT player_id FROM pass_info WHERE channel_id = {channel_id}"):
        player_id = player_id[0]
    return player_id

def get_user_status(user_id):
    for status in heylon_sql.execute(f"SELECT status FROM heylon_users WHERE id = {user_id}"):
        status = status[0]
    return status

def get_all_slots():
    for all_slots in sql.execute(f"SELECT all_slots FROM pass_status"):
        all_slots = all_slots[0]
    return all_slots

def get_total_requests():
    for total_requests in sql.execute(f"SELECT total_requests FROM pass_status"):
        total_requests = total_requests[0]
    return total_requests

def get_all_requests():
    for all_requests in sql.execute(f"SELECT all_requests FROM pass_status"):
        all_requests = all_requests[0]
    return all_requests

def get_pass_status():
    for status in sql.execute(f"SELECT status FROM pass_status"):
        status = status[0]
    return status

@client.event
async def on_shard_ready(shard_id):
    print(f'Logged in as {client.user.name} - {client.user.id}')
    
    # for text in dev_sql.execute(f"SELECT status FROM all_status WHERE id = {pass_system['BOT_ID']}"):
    #     text = text[0]
    # await client.change_presence(status=nextcord.Status.idle, activity=nextcord.Game(f"{text}"))
    
    # channel = (await client.fetch_channel(pass_system['TRACKED_C']))
    # msg = (await channel.fetch_message(pass_system['TRACKED_M']))
    # view = PassView()
    # emb01 = nextcord.Embed(
    #     title=f":tools: Поддержка",
    #     description=f"Возникли проблемы или есть вопросы?\nНажмите на кнопку ниже, чтобы создать тикет.",
    #     color=pass_system['MAIN_C'])
    # emb01.set_footer(text=f'Система тикетов', icon_url=f'{client.user.avatar.url}')
    # await msg.edit(embed=emb01, view=view)
    
    channel = (await client.fetch_channel(pass_system['TRACKED_C2']))
    msg = (await channel.fetch_message(pass_system['TRACKED_M2']))
    status = get_pass_status()
    if status == 'open':
        status = '✅ Набор открыт'
    else:
        status = '⛔️ Набор закрыт'
    all_slots = get_all_slots()
    total_requests = get_total_requests()
    all_requests = get_all_requests()
    view = PassView()
    emb01 = nextcord.Embed(
        title=f"📝 Подача заявки",
        description=f"Для получения пропуска на сервер **подайте заявку**.\nПеред подачей **прочитайте** требования к заявке:"
                    f"\n\n• Поработайте над читабельностью заявки, соблюдайте орфографию и пунктуацию, разбейте предложения на абзацы."
                    f"\n\n• Пишите так, как считаете нужным, не приукрашайте."
                    f"\n\n• Попытайтесь написать как можно больше о себе, заявки в два предложения вряд-ли будут одобрены."
                    f"\n\n• Заявки проверяются в порядке очереди, каждая будет проверена."
                    f"\n\n• Рофло-заявки автоматически не принимаются.",
        color=pass_system['MAIN_C2'])
    if status == '✅ Набор открыт':
        emb01.set_footer(text=f'{status}\nОсталось слотов: {all_slots} | Заявок на набор: {total_requests} | Всего заявок: {all_requests}')
    else:
        emb01.set_footer(text=f'{status}')
    await msg.edit(embed=emb01, view=view)

# @client.command(aliases=['c'])
# async def __c(ctx):
#     view = PassView()
#     emb01 = nextcord.Embed(
#         title=f"📝 Подача заявки",
#         description=f"Для получения пропуска на сервер **подайте заявку**.\nПеред подачей **прочитайте** требования к заявке:"
#                     f"\n\n• Поработайте над читабельностью заявки, соблюдайте орфографию и пунктуацию, разбейте предложения на абзацы."
#                     f"\n\n• Пишите так, как считаете нужным, не приукрашайте."
#                     f"\n\n• Попытайтесь написать как можно больше о себе, заявки в два предложения вряд-ли будут одобрены."
#                     f"\n\n• Заявки проверяются в порядке очереди, каждая будет проверена."
#                     f"\n\n• Рофло-заявки автоматически не принимаются.",
#         color=pass_system['MAIN_C2']
#     )
#     emb01.set_footer(text=f'⛔️ Набор закрыт\nОсталось слотов: 0 | Заявок на набор: 0 | Всего заявок: 65')
#     await ctx.send(embed=emb01, view=view)

@client.command(aliases=['nick'])
async def __nick(ctx, nick):
    status = get_user_status(ctx.author.id)
    if status == 'admin':
        sql.execute(f"""UPDATE pass_info SET nick = '{nick}' WHERE channel_id = {ctx.channel.id}""")
        db.commit()
        await ctx.send(f'Ник изменён.')

@client.command(aliases=['close'])
async def __close(ctx):
    status = get_user_status(ctx.author.id)
    if status == 'admin':
        player_id = get_player_id(ctx.channel.id)
        user = (await client.fetch_user(player_id))
        new_tc_ch_overwrites = {
            user: nextcord.PermissionOverwrite(read_messages=False, send_messages=False),
            ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
        await ctx.channel.edit(overwrites=new_tc_ch_overwrites)
        await ctx.send(f'Заявка закрыта.')

@client.command(aliases=['accept'])
async def __accept(ctx):
    status = get_user_status(ctx.author.id)
    if status == 'admin':
        pl_nick = get_player_nick(ctx.channel.id)
        pl_id = get_player_id(ctx.channel.id)
        guild = (await client.fetch_guild(ctx.guild.id))
        user1 = (await guild.fetch_member(pl_id))
        user = (await client.fetch_user(pl_id))
        await user1.add_roles(guild.get_role(pass_system['PLAYER_ROLE']))
        new_tc_ch_overwrites = {
            user: nextcord.PermissionOverwrite(read_messages=False, send_messages=False),
            ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
        await ctx.channel.edit(overwrites=new_tc_ch_overwrites)
        emb02 = nextcord.Embed(
            title=f':white_check_mark: Заявка одобрена',
            description=f'{pl_nick}, ваша заявка заявка одобрена, сейчас вы автоматически будете добавлены на сервер.'
                        f'\nВ личные сообщения вам будет отправленна информация о том как зайти на сервер',
            color=pass_system['SUCC_C'])
        await ctx.send(embed=emb02)
        emb0666 = nextcord.Embed(
            title=f"",
            description=f"Получил проходку по набору",
            color=0x58b9ff)
        emb0666.set_author(name=f"{pl_nick}", icon_url=f"https://cravatar.eu/helmavatar/{pl_nick}")
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(webhooks2['PASS_WEB'], session=session)
            await webhook.send(f"{user.mention}", embed=emb0666)
        mcr = MCRcon(f"{rcon['RCON_IP']}", f"{rcon['RCON_PASSWORD']}")
        mcr.connect()
        mcr.command(f"easywl add {pl_nick}")
        mcr.disconnect()
        if ((ctx.author.id != ctx.guild.owner_id) and (ctx.author.id != 445523159027023882)):
            await user.edit(nick=f"{pl_nick}")
        else:
            await ctx.send("Извините я не смогу сменить вам ник в дс, тк вы администратор сервера")
        dmchannel = (await user.create_dm())
        await dmchannel.send(f"СООБЩЕНИЕ С ИНФОЙ КАК И КУДА ЗАХОДИТЬ.")

@client.command(aliases=['deny'])
async def __deny(ctx):
    status = get_user_status(ctx.author.id)
    if status == 'admin':
        player_id = get_player_id(ctx.channel.id)
        user = (await client.fetch_user(player_id))
        new_tc_ch_overwrites = {
            user: nextcord.PermissionOverwrite(read_messages=False, send_messages=False),
            ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
        await ctx.channel.edit(overwrites=new_tc_ch_overwrites)
        emb02 = nextcord.Embed(
            title=f':no_entry_sign: Заявка отклонена',
            description=f'Вашу заявку отклонили',
            color=pass_system['ERROR_C'])
        await ctx.send(embed=emb02)

@client.command(aliases=['pass'])
async def __pass(ctx, status, slots=0):
    u_status = get_user_status(ctx.author.id)
    if u_status == 'admin':
        if status == 'open':
            sql.execute(f"""UPDATE pass_status SET status = '{status}'""")
            db.commit()
            sql.execute(f"""UPDATE pass_status SET all_slots = {slots}""")
            db.commit()
            sql.execute(f"""UPDATE pass_status SET total_requests = 0""")
            db.commit()
            await ctx.send('Набор открыт.')
        elif status == 'closed':
            sql.execute(f"""UPDATE pass_status SET status = '{status}'""")
            db.commit()
            sql.execute(f"""UPDATE pass_status SET all_slots = {slots}""")
            db.commit()
            sql.execute(f"""UPDATE pass_status SET total_requests = 0""")
            db.commit()
            await ctx.send('Набор закрыт.')
        if status == 'closed' or status == 'open':
            channel = (await client.fetch_channel(pass_system['TRACKED_C2']))
            msg = (await channel.fetch_message(pass_system['TRACKED_M2']))
            if status == 'open':
                status = '✅ Набор открыт'
            else:
                status = '⛔️ Набор закрыт'
            all_requests = get_all_requests()
            view = PassView()
            emb01 = nextcord.Embed(
                title=f"📝 Подача заявки",
                description=f"Для получения пропуска на сервер **подайте заявку**.\nПеред подачей **прочитайте** требования к заявке:"
                            f"\n\n• Поработайте над читабельностью заявки, соблюдайте орфографию и пунктуацию, разбейте предложения на абзацы."
                            f"\n\n• Пишите так, как считаете нужным, не приукрашайте."
                            f"\n\n• Попытайтесь написать как можно больше о себе, заявки в два предложения вряд-ли будут одобрены."
                            f"\n\n• Заявки проверяются в порядке очереди, каждая будет проверена."
                            f"\n\n• Рофло-заявки автоматически не принимаются.",
                color=pass_system['MAIN_C2'])
            if status == '✅ Набор открыт':
                emb01.set_footer(text=f'{status}\nОсталось слотов: {all_slots} | Заявок на набор: 0 | Всего заявок: {all_requests}')
            else:
                emb01.set_footer(text=f'{status}')
            await msg.edit(embed=emb01, view=view)

#
#       Кнопочки проходок НАЧАЛО
#

class PassOpenView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def handle_click(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        channel = (await client.fetch_channel(interaction.channel_id))
        msg = (await channel.fetch_message(interaction.message.id))
        user = (await client.fetch_user(interaction.user.id))
        guild = (await client.fetch_guild(interaction.guild_id))
        if str(button.emoji) == '🔒':
            player_id = get_player_id(channel.id)
            user = (await client.fetch_user(player_id))
            new_tc_ch_overwrites = {
                user: nextcord.PermissionOverwrite(read_messages=False, send_messages=False),
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
            await channel.edit(overwrites=new_tc_ch_overwrites)
            await channel.send(f'Заявка закрыта.')
        if str(button.emoji) == '👋':
            status = get_user_status(user.id)
            if status == 'admin':
                pl_nick = get_player_nick(channel.id)
                emb02 = nextcord.Embed(
                    title=f':white_check_mark: Заявка одобрена',
                    description=f'{pl_nick}, ваша заявка заявка одобрена, сейчас вы автоматически будете добавлены на сервер.'
                                f'\nВ личные сообщения вам будет отправленна информация о том как зайти на сервер',
                    color=pass_system['SUCC_C'])
                await interaction.response.send_message(embed=emb02)
                player_id = get_player_id(channel.id)
                user1 = (await guild.fetch_member(get_player_id(channel.id)))
                user = (await client.fetch_user(player_id))
                await user1.add_roles(guild.get_role(pass_system['PLAYER_ROLE']))
                new_tc_ch_overwrites = {
                    user: nextcord.PermissionOverwrite(read_messages=False, send_messages=False),
                    guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
                await channel.edit(overwrites=new_tc_ch_overwrites)
                sql.execute(f"""UPDATE pass_status SET all_slots = all_slots - 1""")
                db.commit()
                emb0666 = nextcord.Embed(
                    title=f"",
                    description=f"Получил проходку по набору",
                    color=0x58b9ff)
                emb0666.set_author(name=f"{pl_nick}", icon_url=f"https://cravatar.eu/helmavatar/{pl_nick}")
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(webhooks2['PASS_WEB'], session=session)
                    await webhook.send(f"{user.mention}", embed=emb0666)
                mcr = MCRcon(f"{rcon['RCON_IP']}", f"{rcon['RCON_PASSWORD']}")
                mcr.connect()
                mcr.command(f"easywl add {pl_nick}")
                mcr.disconnect()
                if ((player_id != guild.owner_id) and (player_id != 445523159027023882)):
                    await user.edit(nick=f"{pl_nick}")
                else:
                    await channel.send("Извините я не смогу сменить вам ник в дс, тк вы администратор сервера")
                dmchannel = (await user.create_dm())
                await dmchannel.send(f"СООБЩЕНИЕ С ИНФОЙ КАК И КУДА ЗАХОДИТЬ.")
            else:
                emb = nextcord.Embed(
                    title=f'⚠️ Ошибка',
                    description=f'Данную кнопку может использовать только администрация.',
                    color=pass_system['ERROR_C'])
                await interaction.response.send_message("", embed=emb, ephemeral=True)
        if str(button.emoji) == '👎':
            status = get_user_status(user.id)
            if status == 'admin':
                emb02 = nextcord.Embed(
                    title=f':no_entry_sign: Заявка отклонена',
                    description=f'Вашу заявку отклонили',
                    color=pass_system['ERROR_C'])
                await interaction.response.send_message(embed=emb02)
            else:
                emb = nextcord.Embed(
                    title=f'⚠️ Ошибка',
                    description=f'Данную кнопку может использовать только администрация.',
                    color=pass_system['ERROR_C'])
                await interaction.response.send_message("", embed=emb, ephemeral=True)
    
    @nextcord.ui.button(emoji='🔒', label='Закрыть', style=nextcord.ButtonStyle.red)
    async def ticket_close_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.handle_click(button, interaction)

    @nextcord.ui.button(emoji='👋', label='Одобрить', style=nextcord.ButtonStyle.grey)
    async def ticket_accept_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.handle_click(button, interaction)
    
    @nextcord.ui.button(emoji='👎', label='Отклонить', style=nextcord.ButtonStyle.red)
    async def ticket_deny_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.handle_click(button, interaction)


class PassView(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    async def handle_click(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        pass_status = get_pass_status()
        if pass_status == 'open': # open
            channel = (await client.fetch_channel(pass_system['TRACKED_C']))
            user = (await client.fetch_user(interaction.user.id))
            guild = (await client.fetch_guild(interaction.guild_id))
            for count in sql.execute(f"SELECT count (rowid) as countrowid FROM pass_info"):
                count = count[0]
                pass_count = count
                count = count + 1
            tc_ch = await channel.category.create_text_channel(name=f'заявка-{pass_count}')
            tc_ch.overwrites.update()
            new_tc_ch_overwrites = {
                user: nextcord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False)}
            await tc_ch.edit(overwrites=new_tc_ch_overwrites)
            sql.execute(f"""INSERT INTO pass_info (id, player_id, channel_id) VALUES ({count}, {user.id}, {tc_ch.id})""")
            db.commit()
            sql.execute(f"""UPDATE pass_status SET total_requests = total_requests + 1""")
            db.commit()
            sql.execute(f"""UPDATE pass_status SET all_requests = all_requests + 1""")
            db.commit()
            view = PassOpenView()
            channel_pass = (await client.fetch_channel(pass_system['TRACKED_C2']))
            emb01 = nextcord.Embed(
                title=f'📝 Подача заявки',
                description=f'— Следуйте требованиям к заявке в канале {channel_pass.mention}. Пишите заявку так, как хотите, главное - рассказать о себе, увлечениях, планах на сервер.'
                            f'\n\n— Начинайте писать заявку, позже с вами может связаться администрация и задать несколько вопросов',
                color=pass_system['MAIN_C2'])
            await tc_ch.send(f"{user.mention}", embed=emb01, view=view)
            emb91 = nextcord.Embed(title=':white_check_mark: Заявка создана',description=f'Ваша заявка создана: {tc_ch.mention}',color=pass_system['SUCC_C'])
            emb91.set_footer(text=f"Система тикетов", icon_url=f"{client.user.avatar.url}")
            await interaction.response.send_message("", embed=emb91, ephemeral=True)
            nick_msg = await tc_ch.send(f"{user.mention}, введите ваш точный ник.\nОн будет использоваться для игры на сервере, в случае одобрения заявки."
                                        f"\nНик необходимо написать в течении 300 секунд.")
            def pos1(message):
                return message.channel.id == tc_ch.id
            try:
                msg23 = await client.wait_for('message', timeout=300.0, check=pos1)
            except asyncio.TimeoutError:
                await nick_msg.delete()
            else:
                sql.execute(f"""UPDATE pass_info SET nick = '{msg23.content}' WHERE channel_id = {tc_ch.id}""")
                db.commit()
                await nick_msg.delete()
        else: # closed
            channel_news = (await client.fetch_channel(1058020657331437651))
            emb91 = nextcord.Embed(title=':no_entry_sign: Набор закрыт',description=f'Дождитесь следующего набора, о нём оповестим заранее в канале {channel_news.mention}',color=pass_system['ERROR_C'])
            await interaction.response.send_message("", embed=emb91, ephemeral=True)
    
    @nextcord.ui.button(label='Подать заявку', style=nextcord.ButtonStyle.primary)
    async def create_ticket_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.handle_click(button, interaction)

#
#       Кнопочки проходок КОНЕЦ
#

client.run(pass_system['TOKEN'])