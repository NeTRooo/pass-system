# Импорты дискорда
from nextcord import Interaction, SlashOption, ChannelType
from nextcord.abc import GuildChannel
from nextcord.ext import commands, tasks
from nextcord import Webhook
import nextcord
import asyncio
import aiohttp
# Импорты настроек бота
from settings import pass_system, rcon, webhooks  # Получаем настройки из файла
# Импорты вспомогательных библиотек
import datetime
import sqlite3  # БД которая используется в коде
from mcrcon import MCRcon  # RCON консоль


db = sqlite3.connect('pass-system.sqlite3')
sql = db.cursor()

# dev_db = sqlite3.connect('dev.sqlite3')
# dev_sql = dev_db.cursor()

heylon_db = sqlite3.connect('heylon.sqlite3')
heylon_sql = heylon_db.cursor()

client = commands.AutoShardedBot(shard_count=1, command_prefix='+', intents=nextcord.Intents.all())
client.remove_command('help')

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
    #     color=pass_system['MAIN_C']
    # )
    # emb01.set_footer(text=f'Система тикетов', icon_url=f'{client.user.avatar.url}')
    # await msg.edit(embed=emb01, view=view)
    
    channel = (await client.fetch_channel(pass_system['TRACKED_C2']))
    msg = (await channel.fetch_message(pass_system['TRACKED_M2']))
    for status in sql.execute(f"SELECT status FROM pass_status"):
        status = status[0]
        if status == 'open':
            status = '✅  Набор открыт'
        else:
            status = '⛔️  Набор закрыт'
    for all_slots in sql.execute(f"SELECT all_slots FROM pass_status"):
        all_slots = all_slots[0]
    for total_requests in sql.execute(f"SELECT total_requests FROM pass_status"):
        total_requests = total_requests[0]
    for all_requests in sql.execute(f"SELECT all_requests FROM pass_status"):
        all_requests = all_requests[0]
    view = PassView()
    emb01 = nextcord.Embed(
        title=f"📝 Подача заявки",
        description=f"Для получения пропуска на сервер **подайте заявку**.\nПеред подачей **прочитайте** требования к заявке:"
                    f"\n\n• Поработайте над читабельностью заявки, соблюдайте орфографию и пунктуацию, разбейте предложения на абзацы."
                    f"\n\n• Пишите так, как считаете нужным, не приукрашайте."
                    f"\n\n• Попытайтесь написать как можно больше о себе, заявки в два предложения вряд-ли будут одобрены."
                    f"\n\n• Заявки проверяются в порядке очереди, каждая будет проверена.",
        color=pass_system['MAIN_C2']
    )
    emb01.set_footer(text=f'{status}\nОсталось слотов: {all_slots} | Заявок на набор: {total_requests} | Всего заявок: {all_requests}')
    await msg.edit(embed=emb01, view=view)

@client.event
async def on_message(message):
    if isinstance(message.channel, nextcord.channel.DMChannel):
        async with aiohttp.ClientSession() as session:
            webhook = Webhook.from_url(webhooks1['BOT_DM'], session=session)
            await webhook.send(f"{message.author} > {message.content}")
        await client.process_commands(message)
    else:
        await client.process_commands(message)


#
#       Команда для создания сообщения с кнопочками для открытия тикета/заявки
#


# @client.command(aliases=['c'])
# async def __c(ctx):
#     view = PassView()
#     emb01 = nextcord.Embed(
#         title=f"📝 Подача заявки",
#         description=f"Для получения пропуска на сервер **подайте заявку**.\nПеред подачей **прочитайте** требования к заявке:"
#                     f"\n\n• Поработайте над читабельностью заявки, соблюдайте орфографию и пунктуацию, разбейте предложения на абзацы."
#                     f"\n\n• Пишите так, как считаете нужным, не приукрашайте."
#                     f"\n\n• Попытайтесь написать как можно больше о себе, заявки в два предложения вряд-ли будут одобрены."
#                     f"\n\n• Заявки проверяются в порядке очереди, каждая будет проверена.",
#         color=pass_system['MAIN_C2']
#     )
#     emb01.set_footer(text=f'⛔️  Набор закрыт\nОсталось слотов: 0 | Заявок на набор: 0 | Всего заявок: 65')
#     await ctx.send(embed=emb01, view=view)


#
#       Команды для заявок
#


@client.command(aliases=['nick'])
async def __nick(ctx, nick):
    for status in heylon_sql.execute(f"SELECT status FROM heylon_users WHERE id = {ctx.author.id}"):
        status = status[0]
    if status == 'admin':
        sql.execute(f"""UPDATE pass_info SET nick = '{nick}' WHERE channel_id = {ctx.channel.id}""")
        db.commit()
        await ctx.send(f'Ник изменён.')

@client.command(aliases=['close'])
async def __close(ctx):
    for status in heylon_sql.execute(f"SELECT status FROM heylon_users WHERE id = {ctx.author.id}"):
        status = status[0]
    if status == 'admin':
        for player_id in sql.execute(f"SELECT player_id FROM pass_info WHERE channel_id = {ctx.channel.id}"):
            player_id = player_id[0]
        user = (await client.fetch_user(player_id))
        new_tc_ch_overwrites = {
            user: nextcord.PermissionOverwrite(read_messages=False, send_messages=False),
            ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
        }
        await ctx.channel.edit(overwrites=new_tc_ch_overwrites)
        await ctx.send(f'Заявка закрыта.')

@client.command(aliases=['accept'])
async def __accept(ctx):
    for status in heylon_sql.execute(f"SELECT status FROM heylon_users WHERE id = {ctx.author.id}"):
        status = status[0]
    if status == 'admin':
        emb02 = nextcord.Embed(
            title=f':white_check_mark: Заявка одобрена',
            description=f'Нужно отправить в какой-то канал уведомление, что челик принят на сервер. Плюс через RCON добавить челикса в вайтлист.'
                        f'\nПлюс сменить челиксу ник в дс гильдии. Плюс написать ему в лс.',
            color=pass_system['SUCC_C']
        )
        await ctx.send(embed=emb02)

@client.command(aliases=['deny'])
async def __deny(ctx):
    for status in heylon_sql.execute(f"SELECT status FROM heylon_users WHERE id = {ctx.author.id}"):
        status = status[0]
    if status == 'admin':
        emb02 = nextcord.Embed(
            title=f':white_check_mark: Заявка отклонена',
            description=f'Наверное нужно в какой-то канал отправить уведомление, что челиксу отказано. Плюс написать ему в лс',
            color=pass_system['ERROR_C']
        )
        await ctx.send(embed=emb02)

@client.command(aliases=['pass'])
async def __pass(ctx, status, slots=0):
    for u_status in heylon_sql.execute(f"SELECT status FROM heylon_users WHERE id = {ctx.author.id}"):
        u_status = u_status[0]
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
                status = '✅  Набор открыт'
            else:
                status = '⛔️  Набор закрыт'
            for all_requests in sql.execute(f"SELECT all_requests FROM pass_status"):
                all_requests = all_requests[0]
            view = PassView()
            emb01 = nextcord.Embed(
                title=f"📝 Подача заявки",
                description=f"Для получения пропуска на сервер **подайте заявку**.\nПеред подачей **прочитайте** требования к заявке:"
                            f"\n\n• Поработайте над читабельностью заявки, соблюдайте орфографию и пунктуацию, разбейте предложения на абзацы."
                            f"\n\n• Пишите так, как считаете нужным, не приукрашайте."
                            f"\n\n• Попытайтесь написать как можно больше о себе, заявки в два предложения вряд-ли будут одобрены."
                            f"\n\n• Заявки проверяются в порядке очереди, каждая будет проверена.",
                color=pass_system['MAIN_C2']
            )
            emb01.set_footer(text=f'{status}\nОсталось слотов: {slots} | Заявок на набор: 0 | Всего заявок: {all_requests}')
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
            for player_id in sql.execute(f"SELECT player_id FROM pass_info WHERE channel_id = {channel.id}"):
                player_id = player_id[0]
            user = (await client.fetch_user(player_id))
            new_tc_ch_overwrites = {
                user: nextcord.PermissionOverwrite(read_messages=False, send_messages=False),
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
            }
            await channel.edit(overwrites=new_tc_ch_overwrites)
            await channel.send(f'Заявка закрыта.')
        if str(button.emoji) == '👋':
            for status in heylon_sql.execute(f"SELECT status FROM heylon_users WHERE id = {user.id}"):
                status = status[0]
            if status == 'admin':
                emb02 = nextcord.Embed(
                    title=f':white_check_mark: Заявка одобрена',
                    description=f'Нужно отправить в какой-то канал уведомление, что челик принят на сервер.',
                    color=pass_system['SUCC_C']
                )
                await interaction.response.send_message(embed=emb02)
                
                for pl_nick in sql.execute("SELECT nick FROM pass_info WHERE channel_id = {channel.id}"):
                    pl_nick = pl_nick[0]
                emb0666 = nextcord.Embed(
                    title=f"",
                    description=f"Получил проходку по набору",
                    color=0x58b9ff
                )
                emb0666.set_author(name=f"{pl_nick}", icon_url=f"https://cravatar.eu/helmavatar/{pl_nick}")
                async with aiohttp.ClientSession() as session:
                    webhook = Webhook.from_url(webhooks['PASS_WEB'], session=session)
                    await webhook.send(f"{user.mention}", embed=emb0666)
                
                mcr = MCRcon(f"{rcon['RCON_IP']}", f"{rcon['RCON_PASSWORD']}")
                mcr.connect()
                mcr.command(f"easywl add {pl_nick}")
                mcr.disconnect()
                if ((message.author.id != message.guild.owner_id) and (message.author.id != 445523159027023882)):
                    await user.edit(nick=f"{pl_nick}")
                else:
                    await channel.send("Извините я не смогу сменить вам ник в дс, тк вы администратор сервера")
                dmchannel = (await user.create_dm())
                await dmchannel.send(f"Тикет {count} закрыт администратором. Вам предоставляется лог-файл тикета.")
                
            else:
                emb = nextcord.Embed(
                    title=f'⚠️ Ошибка',
                    description=f'Данную кнопку может использовать только администрация.',
                    color=pass_system['ERROR_C']
                )
                await interaction.response.send_message("", embed=emb, ephemeral=True)
        if str(button.emoji) == '👎':
            for status in heylon_sql.execute(f"SELECT status FROM heylon_users WHERE id = {user.id}"):
                status = status[0]
            if status == 'admin':
                emb02 = nextcord.Embed(
                    title=f':white_check_mark: Заявка отклонена',
                    description=f'Наверное нужно в какой-то канал отправить уведомление, что челиксу отказано. Плюс написать ему в лс',
                    color=pass_system['ERROR_C']
                )
                await interaction.response.send_message(embed=emb02)
            else:
                emb = nextcord.Embed(
                    title=f'⚠️ Ошибка',
                    description=f'Данную кнопку может использовать только администрация.',
                    color=pass_system['ERROR_C']
                )
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
        for pass_status in sql.execute(f"SELECT status FROM pass_status"):
            pass_status = pass_status[0]
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
                guild.default_role: nextcord.PermissionOverwrite(read_messages=False)
            }
            await tc_ch.edit(overwrites=new_tc_ch_overwrites)
            
            sql.execute(f"""INSERT INTO pass_info (id, player_id, channel_id) VALUES ({count}, {user.id}, {tc_ch.id})""")
            db.commit()
            sql.execute(f"""UPDATE pass_status SET total_requests = total_requests + 1""")
            db.commit()
            sql.execute(f"""UPDATE pass_status SET all_requests = all_requests + 1""")
            db.commit()
            
            view = PassOpenView()
            emb01 = nextcord.Embed(
                title=f'📝 Подача заявки',
                description=f'Следуйте требованиям к заявке в канале #подать-заявку. Пишите заявку так, как хотите, главное - рассказать о себе, увлечениях, планах на сервер.',
                color=pass_system['MAIN_C2']
            )
            emb01.set_footer(text=f"Начинайте писать заявку, позже с вами может связаться администрация и задать несколько вопросов.")
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
            emb91 = nextcord.Embed(title=':no_entry_sign:  Набор закрыт',description=f'Дождитесь следующего набора, о нём оповестим заранее в канале #новости',color=pass_system['ERROR_C'])
            await interaction.response.send_message("", embed=emb91, ephemeral=True)
        

    @nextcord.ui.button(label='Подать заявку', style=nextcord.ButtonStyle.primary)
    async def create_ticket_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await self.handle_click(button, interaction)



#
#       Кнопочки проходок КОНЕЦ
#


client.run(pass_system['TOKEN'])