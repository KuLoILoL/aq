import discord
from discord.ext import commands
from discord.ui import Button, View
import os
import random
import json

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

# 永続化ファイルの場所
VALUE_PATH = "/app/data/bot_value.json"  # NorthFlankに合わせたパス
PLAYER_DATA_FILE = '/app/data/player_data.json'  # 同じくNorthFlank用

# 読み込み
def load_value():
    if os.path.exists(VALUE_PATH):
        with open(VALUE_PATH, "r") as f:
            return json.load(f)
    else:
        return {"value": 10000}

def save_value(data):
    with open(VALUE_PATH, "w") as f:
        json.dump(data, f)

# プレイヤーデータの読み込み
def load_data():
    if not os.path.exists(PLAYER_DATA_FILE):
        return {}
    with open(PLAYER_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

# プレイヤーデータの保存
def save_data(data):
    with open(PLAYER_DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

@bot.event
async def on_ready():
    print(f'✅ Bot is ready: {bot.user}')

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
            "明は大凶です。"
        ]
        await interaction.response.send_message(f"{interaction.user.mention} {random.choice(colors)}")
        user_button_click_count[user_id] += 1

# －－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－－
# ステータス表示
@bot.command()
async def status(ctx):
    user_id = str(ctx.author.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = init_player(user_id)
        save_data(data)
    player = data[user_id]
    status_text = f"レベル: {player['level']}\nHP: {player['hp']}/{player['max_hp']}\n攻撃力: {player['attack']}"
    if player['equipped']['weapon']:
        status_text += f" (+{SHOP_ITEMS[player['equipped']['weapon']]['power']})"
    status_text += f"\n防御力: {player['defense']}"
    if player['equipped']['armor']:
        status_text += f" (+{SHOP_ITEMS[player['equipped']['armor']]['power']})"
    status_text += f"\n所持金: {player['gold']}\nアイテム: {', '.join(player['items']) if player['items'] else 'なし'}"
    await ctx.send(f"```{status_text}```")

# アイテム使用コマンド
@bot.command()
async def use(ctx, item_key):
    user_id = str(ctx.author.id)
    data = load_data()
    if user_id not in data or item_key not in data[user_id]['items']:
        await ctx.send("そのアイテムは持っていません。")
        return

    player = data[user_id]
    item = SHOP_ITEMS[item_key]

    if item['effect'] == "heal":
        player['hp'] = min(player['max_hp'], player['hp'] + item['power'])
        await ctx.send(f"{item['name']} を使用して HP が回復しました！")
    elif item['effect'] == "attack":
        player['equipped']['weapon'] = item_key
        await ctx.send(f"{item['name']} を装備しました（攻撃力上昇）！")
    elif item['effect'] == "defense":
        player['equipped']['armor'] = item_key
        await ctx.send(f"{item['name']} を装備しました（防御力上昇）！")

    player['items'].remove(item_key)
    save_data(data)

# バトルUI（攻撃、アイテム使用、逃げる）
class BattleView(discord.ui.View):
    def __init__(self, ctx, player, monster_key, monster):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.user_id = str(ctx.author.id)
        self.player = player
        self.monster_key = monster_key
        self.monster = monster
        self.monster["current_hp"] = monster["hp"]

    @discord.ui.button(label="たたかう", style=discord.ButtonStyle.danger)
    async def fight(self, interaction: discord.Interaction, button: discord.ui.Button):
        if str(interaction.user.id) != self.user_id:
            await interaction.response.send_message("あなたのバトルではありません。", ephemeral=True)
            return

        data = load_data()
        player = data[self.user_id]
        weapon_bonus = 0
        if player['equipped']['weapon']:
            weapon_bonus = SHOP_ITEMS[player['equipped']['weapon']]['power']
        attack = player['attack'] + weapon_bonus
        damage = max(1, attack - self.monster['defense'])
        self.monster['current_hp'] -= damage

        if self.monster['current_hp'] <= 0:
            exp = self.monster['exp']
            gold = self.monster['gold']
            player['exp'] += exp
            player['gold'] += gold
            leveled_up, old_level = check_level_up(player)
            player['battle'] = None
            player['current_monster'] = None
            save_data(data)
            result = f"{self.monster_key} を倒した！ 経験値 {exp}、ゴールド {gold} を獲得！"
            if leveled_up:
                result += f"\nレベルアップ！ {old_level} → {player['level']}"
            await interaction.response.edit_message(content=result, view=None)
            return

        # 敵の反撃
        armor_bonus = 0
        if player['equipped']['armor']:
            armor_bonus = SHOP_ITEMS[player['equipped']['armor']]['power']
        monster_damage = max(1, self.monster['attack'] - (player['defense'] + armor_bonus))
        player['hp'] -= monster_damage

        if player['hp'] <= 0:
            player['hp'] = 1
            player['battle'] = None
            player['current_monster'] = None
            save_data(data)
            await interaction.response.edit_message(content=f"{self.monster_key} に負けてしまった……HPが1で復活。", view=None)
            return

        save_data(data)
        await interaction.response.edit_message(content=f"{self.monster_key} に {damage} ダメージを与えた！\n{self.monster_key} のHP: {self.monster['current_hp']}\n{self.monster_key} の反撃で {monster_damage} ダメージを受けた！", view=self)

    @discord.ui.button(label="アイテム使用", style=discord.ButtonStyle.success)
    async def use_item(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("/use <アイテム名キー> を使ってアイテムを使用してください。", ephemeral=True)

    @discord.ui.button(label="にげる", style=discord.ButtonStyle.secondary)
    async def run(self, interaction: discord.Interaction, button: discord.ui.Button):
        data = load_data()
        player = data[self.user_id]
        player['battle'] = None
        player['current_monster'] = None
        save_data(data)
        await interaction.response.edit_message(content="戦闘から逃げた！", view=None)

@bot.command()
async def battle(ctx, monster_name):
    user_id = str(ctx.author.id)
    data = load_data()
    if user_id not in data:
        data[user_id] = init_player(user_id)

    if monster_name not in MONSTERS:
        await ctx.send("そのモンスターは存在しません。")
        return

    player = data[user_id]
    player['battle'] = monster_name
    player['current_monster'] = {"current_hp": MONSTERS[monster_name]['hp']}
    save_data(data)

    monster = MONSTERS[monster_name]
    embed = discord.Embed(title=f"{monster_name} が現れた！", description="戦闘開始！")
    file = discord.File(monster['image'], filename="monster.png")
    embed.set_image(url="attachment://monster.png")

    await ctx.send(file=file, embed=embed, view=BattleView(ctx, player, monster_name, monster))

# 実行
bot.run(os.environ['DISCORD_TOKEN'])
