import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import json

# sample text HelloWorlds

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.event
async def on_ready():
    print(f'✅ Bot is ready: {bot.user}')

# 永続化ファイルの場所を Northflank に合わせる

VALUE_PATH = "/app/data/bot_value.json"

# 読み込み

if os.path.exists(VALUE_PATH):
    with open(VALUE_PATH, "r") as f:
        bot_data = json.load(f)
else:
    bot_data = {"value": 10000}

# 保存する関数（使い回しできる）

def save_data():
    with open(VALUE_PATH, "w") as f:
        json.dump(bot_data, f)

intents = discord.Intents.default()
intents.message_content = True

# 🌞 朝用ビュー（挨拶ボタン）

class MyButtonView(discord.ui.View):
    @discord.ui.button(label="挨拶", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("# ドカーン💥", ephemeral=True)

    # 🌙 夜用ビュー（おやすみくじボタン）

user_button_click_count = {}

class NightView(discord.ui.View):
    @discord.ui.button(label="おやすみくじ", style=discord.ButtonStyle.success)
    async def lucky_color(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id

        # ユーザーの押下回数を管理
        if user_id not in user_button_click_count:
            user_button_click_count[user_id] = 0

        # 2回までボタンを押せるように制限
        if user_button_click_count[user_id] >= 3:
            await interaction.response.send_message(f"{interaction.user.mention} はよ寝ろ", ephemeral=True)
            return

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
        await interaction.response.send_message(f"{interaction.user.mention} {random.choice(colors)}")
        user_button_click_count[user_id] += 1

# 💬 各コマンドの処理

async def hello_command(ctx):
    await ctx.send("ハロー")

async def button_command(ctx):
    view = MyButtonView()
    await ctx.send("おはようございます！", view=view)

async def oyasumi_command(ctx):
    view = NightView()
    await ctx.send("おやすみなさい。ぐ～", view=view)

async def ishiba_command(ctx):
    embed = discord.Embed(title="💥🔫")
    embed.set_image(url="https://images-ext-1.discordapp.net/external/xxHwpmL3IVQc_lho1AAo3nSLAtBULhzeJjXzqNQnP-Q/https/i.imgur.com/Gx4WaWK.png?format=webp&quality=lossless&width=381&height=375")
    await ctx.send(embed=embed)

# ✅ コマンド登録

command_map = {
"hello": hello_command,
"おはよう": button_command,
"おやすみ": oyasumi_command,
"石破茂暗殺": ishiba_command
}

for name, handler in command_map.items():
    bot.command(name=name)(handler)

# 🤖 自動応答

@bot.event
async def on_message(message):
    # ほかのボットの返信は無視する
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

@bot.command()
async def ざつよう(ctx):
    bot_data["value"] -= 1
    save_data()
    await ctx.send(f"サンキュ！あと{bot_data['value']}本残ってるぞ！")

PLAYER_DATA_FILE = 'player_data.json'

# －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－



# 🔁 実行

bot.run(os.environ['DISCORD_TOKEN'])

