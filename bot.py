import disnake
from disnake.ext import commands
from dotenv import load_dotenv
import os
import asyncio
import datetime

load_dotenv()

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# Создание embed с footer
def create_embed(title=None, description=None, color=0x5865F2):
    embed = disnake.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Historical Empire")
    return embed

# Проверка прав (администратор или модератор)
def is_mod():
    async def predicate(ctx):
        return ctx.author.guild_permissions.administrator or \
               ctx.author.guild_permissions.moderate_members
    return commands.check(predicate)

# Отправка в канал логов
async def send_log(ctx, action, target, duration=None, reason=None):
    logs_channel = disnake.utils.get(ctx.guild.channels, name="「🔨」・логи-наказаний")
    if not logs_channel:
        return

    embed = create_embed(color=0xFF0000)
    embed.add_field(name="Действие", value=action, inline=False)
    embed.add_field(name="Пользователь", value=f"{target.mention} [{target.id}]", inline=False)
    if duration:
        embed.add_field(name="Продолжительность", value=f"{duration} минут", inline=False)
    embed.add_field(name="Причина", value=reason or "Не указана", inline=False)
    embed.add_field(name="Администратор", value=ctx.author.mention, inline=False)

    await logs_channel.send(embed=embed)

# Ожидание ответа от пользователя
async def wait_for_answer(ctx, question):
    embed = create_embed(description=question, color=0x5865F2)
    await ctx.send(embed=embed)
    try:
        msg = await bot.wait_for(
            "message",
            check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
            timeout=60
        )
        return msg.content
    except asyncio.TimeoutError:
        embed = create_embed(description="⏰ Время вышло. Команда отменена.", color=0xFF0000)
        await ctx.send(embed=embed)
        return None

# ===== PING =====
@bot.command()
async def ping(ctx):
    embed = create_embed(description="Pong! 🏓", color=0x00FF00)
    await ctx.send(embed=embed)

# ===== MUTE =====
@bot.command()
@is_mod()
async def mute(ctx, member: disnake.Member):
    duration = await wait_for_answer(ctx, "⏱ Введите продолжительность мута (в минутах):")
    if not duration:
        return

    reason = await wait_for_answer(ctx, "📝 Введите причину:")
    if not reason:
        return

    delta = datetime.timedelta(minutes=int(duration))
    await member.timeout(duration=delta, reason=reason)

    embed = create_embed(title="🔇 Пользователь заглушен", color=0xFF6600)
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="Длительность", value=f"{duration} минут", inline=True)
    embed.add_field(name="Причина", value=reason, inline=False)
    await ctx.send(embed=embed)
    await send_log(ctx, "🔇 Мут [!mute]", member, duration, reason)

# ===== UNMUTE =====
@bot.command()
@is_mod()
async def unmute(ctx, member: disnake.Member):
    await member.timeout(duration=None)

    embed = create_embed(title="🔊 Мут снят", color=0x00FF00)
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="Администратор", value=ctx.author.mention, inline=True)
    await ctx.send(embed=embed)
    await send_log(ctx, "🔊 Снятие мута [!unmute]", member)

# ===== KICK =====
@bot.command()
@is_mod()
async def kick(ctx, member: disnake.Member):
    reason = await wait_for_answer(ctx, "📝 Введите причину кика:")
    if not reason:
        return

    embed = create_embed(title="👢 Пользователь кикнут", color=0xFF6600)
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="Причина", value=reason, inline=False)
    await ctx.send(embed=embed)
    await send_log(ctx, "👢 Кик [!kick]", member, reason=reason)
    await member.kick(reason=reason)

# ===== BAN =====
@bot.command()
@is_mod()
async def ban(ctx, member: disnake.Member):
    reason = await wait_for_answer(ctx, "📝 Введите причину бана:")
    if not reason:
        return

    embed = create_embed(title="🔨 Пользователь забанен", color=0xFF0000)
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="Причина", value=reason, inline=False)
    await ctx.send(embed=embed)
    await send_log(ctx, "🔨 Бан [!ban]", member, reason=reason)
    await member.ban(reason=reason)

# ===== UNBAN =====
@bot.command()
@is_mod()
async def unban(ctx, user_id: int):
    try:
        user = await bot.fetch_user(user_id)
        await ctx.guild.unban(user)

        embed = create_embed(title="✅ Бан снят", color=0x00FF00)
        embed.add_field(name="Пользователь", value=f"{user} [{user_id}]", inline=True)
        embed.add_field(name="Администратор", value=ctx.author.mention, inline=True)
        await ctx.send(embed=embed)
        await send_log(ctx, "✅ Снятие бана [!unban]", user)
    except:
        embed = create_embed(description="❌ Пользователь не найден или не забанен.", color=0xFF0000)
        await ctx.send(embed=embed)

# ===== WARN =====
@bot.command()
@is_mod()
async def warn(ctx, member: disnake.Member):
    reason = await wait_for_answer(ctx, "📝 Введите причину варна:")
    if not reason:
        return

    embed = create_embed(title="⚠️ Пользователь получил предупреждение", color=0xFFFF00)
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="Причина", value=reason, inline=False)
    await ctx.send(embed=embed)
    await send_log(ctx, "⚠️ Варн [!warn]", member, reason=reason)

# ===== UNWARN =====
@bot.command()
@is_mod()
async def unwarn(ctx, member: disnake.Member):
    reason = await wait_for_answer(ctx, "📝 Укажите причину снятия варна:")
    if not reason:
        return

    embed = create_embed(title="✅ Предупреждение снято", color=0x00FF00)
    embed.add_field(name="Пользователь", value=member.mention, inline=True)
    embed.add_field(name="Причина", value=reason, inline=False)
    await ctx.send(embed=embed)
    await send_log(ctx, "✅ Снятие варна [!unwarn]", member, reason=reason)

# ===== АВТО-РОЛЬ ПРИ ВХОДЕ =====
@bot.event
async def on_member_join(member):
    role_participant = disnake.utils.get(member.guild.roles, name="❰👤❱〔Участник〕")
    role_unregistered = disnake.utils.get(member.guild.roles, name="❰❓❱〔Не зарегистрирован〕")
    
    if role_participant:
        await member.add_roles(role_participant)
    if role_unregistered:
        await member.add_roles(role_unregistered)

# ===== HELP =====
@bot.command(name="help")
async def help_command(ctx):
    embed = create_embed(title="📋 Список команд", color=0x5865F2)

    embed.add_field(
        name="🔇 Модерация",
        value=(
            "`!mute <@user>` — выдача мута пользователю\n"
            "`!unmute <@user>` — снятие мута\n"
            "`!kick <@user>` — кик пользователя\n"
            "`!ban <@user>` — бан пользователя\n"
            "`!unban <ID>` — снятие бана по ID\n"
            "`!warn <@user>` — выдача предупреждения\n"
            "`!unwarn <@user>` — снятие предупреждения\n"
        ),
        inline=False
    )

    embed.add_field(
        name="🛠 Прочее",
        value=(
            "`!ping` — проверка работы бота\n"
            "`!help` — список команд\n"
        ),
        inline=False
    )

    await ctx.send(embed=embed)

# ===== ОШИБКИ =====
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        embed = create_embed(description="❌ У вас нет прав для этой команды.", color=0xFF0000)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MemberNotFound):
        embed = create_embed(description="❌ Пользователь не найден.", color=0xFF0000)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.MissingRequiredArgument):
        embed = create_embed(description="❌ Укажи пользователя. Пример: `!mute @user`", color=0xFF0000)
        await ctx.send(embed=embed)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

bot.run(os.getenv("TOKEN"))