import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command\_prefix='/', intents=intents)

@bot.event
async def on\_ready():
print(f'✅ Bot is ready: {bot.user}')

# 永続化ファイルの場所を Northflank に合わせる

VALUE\_PATH = "/app/data/bot\_value.json"

# 読み込み

if os.path.exists(VALUE\_PATH):
with open(VALUE\_PATH, "r") as f:
bot\_data = json.load(f)
else:
bot\_data = {"value": 10000}

# 保存する関数（使い回しできる）

def save\_data():
with open(VALUE\_PATH, "w") as f:
json.dump(bot\_data, f)

intents = discord.Intents.default()
intents.message\_content = True

# 🌞 朝用ビュー（挨拶ボタン）

class MyButtonView(discord.ui.View):
@discord.ui.button(label="挨拶", style=discord.ButtonStyle.primary)
async def button\_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
await interaction.response.send\_message("# ドカーン💥", ephemeral=True)

# 🌙 夜用ビュー（おやすみくじボタン）

user\_button\_click\_count = {}

class NightView(discord.ui.View):
@discord.ui.button(label="おやすみくじ", style=discord.ButtonStyle.success)
async def lucky\_color(self, interaction: discord.Interaction, button: discord.ui.Button):
user\_id = interaction.user.id

```
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
```

# 💬 各コマンドの処理

async def hello\_command(ctx):
await ctx.send("ハロー")

async def button\_command(ctx):
view = MyButtonView()
await ctx.send("おはようございます！", view=view)

async def oyasumi\_command(ctx):
view = NightView()
await ctx.send("おやすみなさい。ぐ～", view=view)

# ✅ コマンド登録

command\_map = {
"hello": hello\_command,
"おはよう": button\_command,
"おやすみ": oyasumi\_command
}

for name, handler in command\_map.items():
bot.command(name=name)(handler)

# 🤖 自動応答

@bot.event
async def on\_message(message):
if message.author.bot:
return

```
if "大丈夫？" in message.content:
    rand = random.random()
    if rand < 0.9:
        response = "俺なら大丈夫だぜ"
    else:
        response = "大丈夫なわけねえだろ"
    await message.channel.send(response)

await bot.process_commands(message)
```

@bot.command()
async def ざつよう(ctx):
bot\_data\["value"] -= 1
save\_data()
await ctx.send(f"サンキュ！あと{bot\_data\['value']}本残ってるぞ！")

PLAYER\_DATA\_FILE = 'player\_data.json'

# －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－



# 🔁 実行

bot.run(os.environ\['DISCORD\_TOKEN'])

