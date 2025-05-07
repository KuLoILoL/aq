import discord
from discord.ext import commands
import os
import random
import json

intents = discord.Intents.default()
intents.message\_content = True

bot = commands.Bot(command\_prefix='/', intents=intents)

@bot.event
async def on\_ready():
print(f'✅ Bot is ready: {bot.user}')

# 🔹 ボタン付きの処理用ビュー

class MyButtonView(discord.ui.View):
@discord.ui.button(label="挨拶", style=discord.ButtonStyle.primary)
async def button\_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
await interaction.response.send\_message("# ドカーン💥", ephemeral=True)

# 🔹 コマンド関数

async def hello\_command(ctx):
await ctx.send("ハロー")

async def button\_command(ctx):
view = MyButtonView()
await ctx.send("おはようございます！", view=view)

# 🔹 コマンドマップ

command\_map = {
"hello": hello\_command,
"おはよう": button\_command
}

for name, handler in command\_map.items():
bot.command(name=name)(handler)

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

DATA\_FILE = "player\_data.json"
player\_data = {}

def load\_data():
global player\_data
if os.path.exists(DATA\_FILE):
with open(DATA\_FILE, "r", encoding="utf-8") as f:
player\_data = json.load(f)

# ここから戦闘ーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーーー

intents = discord.Intents.default()
bot = commands.Bot(command\_prefix="!", intents=intents)

DATA\_FILE = "player\_data.json"
player\_data = {}
battle\_state = {}  # 一時的な戦闘状態（HPなど）

# ------------------------ JSON 読み書き ------------------------

def load\_data():
global player\_data
if os.path.exists(DATA\_FILE):
with open(DATA\_FILE, "r", encoding="utf-8") as f:
player\_data = json.load(f)
else:
player\_data = {}

def save\_data():
with open(DATA\_FILE, "w", encoding="utf-8") as f:
json.dump(player\_data, f, ensure\_ascii=False, indent=2)

# ------------------------ レベルアップ処理 ------------------------

def check\_level\_up(user\_id):
data = player\_data\[user\_id]
level = data\["level"]
exp = data\["exp"]
next\_exp = level \* 50

```
if exp >= next_exp:
    data["level"] += 1
    data["exp"] -= next_exp
    data["max_hp"] += 20
    data["strength"] += 5
    data["agility"] += 3
    return True
return False
```

# ------------------------ 戦闘View（ボタン） ------------------------

class BattleView(discord.ui.View):
def **init**(self, user\_id):
super().**init**(timeout=None)
self.user\_id = str(user\_id)

```
@discord.ui.button(label="攻撃", style=discord.ButtonStyle.danger)
async def attack(self, interaction: discord.Interaction, button: discord.ui.Button):
    if str(interaction.user.id) != self.user_id:
        await interaction.response.send_message("これはあなたの戦闘ではありません！", ephemeral=True)
        return

    data = player_data[self.user_id]
    state = battle_state[self.user_id]

    # プレイヤーと敵の攻撃力
    player_atk = data["strength"]
    enemy_level = data["level"]
    enemy_hp = 30 + enemy_level * 10
    enemy_atk = 5 + enemy_level * 3

    damage_to_enemy = random.randint(player_atk - 3, player_atk + 3)
    damage_to_player = random.randint(enemy_atk - 2, enemy_atk + 2)

    state["enemy_hp"] -= damage_to_enemy
    state["player_hp"] -= damage_to_player

    if state["enemy_hp"] <= 0:
        data["exp"] += 20 + enemy_level * 5
        leveled_up = check_level_up(self.user_id)
        save_data()
        msg = f"🎉 勝利！{damage_to_enemy}ダメージを与えた！\n経験値 +{20 + enemy_level * 5}"
        if leveled_up:
            msg += f"\n🆙 {data['level']} レベルにアップ！"

        await interaction.response.edit_message(content=msg, embed=None, view=None)
        battle_state.pop(self.user_id)
        return

    if state["player_hp"] <= 0:
        await interaction.response.edit_message(content="💀 あなたはやられてしまった…", embed=None, view=None)
        battle_state.pop(self.user_id)
        return

    embed = discord.Embed(title="⚔️ 戦闘中", color=discord.Color.red())
    embed.add_field(name="あなたのHP", value=f"{state['player_hp']} / {data['max_hp']}", inline=True)
    embed.add_field(name="敵のHP", value=f"{state['enemy_hp']}", inline=True)
    await interaction.response.edit_message(embed=embed, view=self)
```

# ------------------------ コマンド：戦闘開始 ------------------------

@bot.command()
async def たたかい(ctx):
user\_id = str(ctx.author.id)

```
if user_id not in player_data:
    player_data[user_id] = {
        "name": ctx.author.display_name,
        "level": 1,
        "exp": 0,
        "max_hp": 100,
        "strength": 10,
        "agility": 8
    }
    save_data()

if user_id in battle_state:
    await ctx.send("すでに戦闘中です！")
    return

# 戦闘用のHP状態を初期化
player_hp = player_data[user_id]["max_hp"]
enemy_level = player_data[user_id]["level"]
enemy_hp = 30 + enemy_level * 10

battle_state[user_id] = {
    "player_hp": player_hp,
    "enemy_hp": enemy_hp
}

embed = discord.Embed(title="⚔️ 戦闘開始！", description="攻撃ボタンで戦おう！", color=discord.Color.red())
embed.add_field(name="あなたのHP", value=f"{player_hp} / {player_hp}", inline=True)
embed.add_field(name="敵のHP", value=str(enemy_hp), inline=True)

view = BattleView(user_id)
await ctx.send(embed=embed, view=view)
```

# ------------------------ コマンド：ステータス表示 ------------------------

@bot.command()
async def ステータス(ctx):
user\_id = str(ctx.author.id)
if user\_id not in player\_data:
await ctx.send("まだプレイヤーデータがありません。まずは `!たたかい` で戦ってみましょう！")
return

```
data = player_data[user_id]
embed = discord.Embed(title=f"🧍 {data['name']} のステータス", color=discord.Color.blue())
embed.add_field(name="レベル", value=data["level"], inline=True)
embed.add_field(name="経験値", value=f"{data['exp']} / {data['level'] * 50}", inline=True)
embed.add_field(name="最大HP", value=data["max_hp"], inline=True)
embed.add_field(name="ちから", value=data["strength"], inline=True)
embed.add_field(name="すばやさ", value=data["agility"], inline=True)
await ctx.send(embed=embed)
```

# ------------------------ Bot 起動準備 ------------------------

# 実行

bot.run(os.environ\['DISCORD\_TOKEN'])
