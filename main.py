import discord
from discord.ext import commands
import os
import random

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/', intents=intents)

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
        if user_button_click_count[user_id] >= 2:
            await interaction.response.send_message(f"{interaction.user.mention} もう押さないでください。", ephemeral=True)
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

# ✅ コマンド登録
command_map = {
    "hello": hello_command,
    "おはよう": button_command,
    "おやすみ": oyasumi_command
}

for name, handler in command_map.items():
    bot.command(name=name)(handler)

# 🤖 自動応答
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

# 🔁 実行
bot.run(os.environ['DISCORD_TOKEN'])
