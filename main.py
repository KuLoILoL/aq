import discord
from discord.ext import commands
import os

# Discordのインテント設定（Botがイベントを受け取るための許可）
intents = discord.Intents.default()
intents.message_content = True  # メッセージ内容の取得を許可

# Bot本体の作成（接頭辞 ! でコマンドを認識）
bot = commands.Bot(command_prefix='/', intents=intents)

# 起動時に表示
@bot.event
async def on_ready():
    print(f'✅ Bot is ready: {bot.user}')

# 🔹 ボタン付きの処理用ビュー
class MyButtonView(discord.ui.View):
    @discord.ui.button(label="挨拶", style=discord.ButtonStyle.primary)
    async def button_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("# ドカーン💥", ephemeral=True)

# 🔹 コマンドごとの処理を関数で用意しておく
async def hello_command(ctx):
    await ctx.send("ハロー")


async def button_command(ctx):
    view = MyButtonView()
    await ctx.send("おはようございます！", view=view)

# 🔹 コマンド名 → 関数 の辞書（ループで登録）
command_map = {
    "hello": hello_command,
    "おはよう": button_command
}

# 🔁 登録ループ（方法②スタイル）
for name, handler in command_map.items():
    bot.command(name=name)(handler)



@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if "大丈夫？" in message.content:
        rand = random.random()  # 0.0 〜 1.0 の浮動小数点数を返す

        if rand < 0.9:
            response = "俺なら大丈夫だぜ 💪"  # 90%
        else:
            response = "大丈夫なわけねえだろ 😡"  # 10%
        await message.channel.send(response)
    await bot.process_commands(message)


# Discordトークンを環境変数から取得
bot.run(os.environ['DISCORD_TOKEN'])
