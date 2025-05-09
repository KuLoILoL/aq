import discord
from discord.ext import commands
import os
import random  # 🔧 これを追加！

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is ready: {bot.user}')

class NightView(discord.ui.View):
    @discord.ui.button(label="おやすみくじ", style=discord.ButtonStyle.success)
 async def lucky_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        colors = [
        "明日は何もいいことありません",
        "明日はいいことあります",
        "明日のラッキーカラーは赤です",
        "明日のラッキーカラーは青です。",
        "明日のラッキーナンバーは5です。",
        "明日は中吉です。",
        "明日は大吉です。",
        "明日は大凶です。"
    ]
        await interaction.response.send_message(f"{random.choice(colors)}", ephemeral=True)

async def hello_command(ctx):
    await ctx.send("ハロー")

async def button_command(ctx):
    view = MyButtonView()
    await ctx.send("おはようございます！", view=view)

async def oyasumi_command(ctx):
    await ctx.send("おやすみなさい。ぐ～", view=view)


command_map = {
    "hello": hello_command,
    "おはよう": button_command,
    "おやすみくじ": oyasumikuji_command,
    "おやすみ":oyasumi_command
}

for name, handler in command_map.items():
    bot.command(name=name)(handler)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "大丈夫？" in message.content:
        rand = random.random()
        if rand < 0.9:
            response = "俺なら大丈夫だぜ"
        else:
            response = "大丈夫なわけねえだろ"
        await message.channel.send(response)

    await bot.process_commands(message)

bot.run(os.environ['DISCORD_TOKEN'])
