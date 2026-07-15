import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import sys, os, time
import re
import emoji as emoji_lib #pip install emoji
from zoneinfo import ZoneInfo #pip install tzdata
from typing import Optional

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from SQL_Commands import sql_commands
from Data_Models import models
from Graphic_Tools import graphic_tools

#--------------------------------------------------------------------------------------------------

class Analytics(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

        self.db = sqlite3.connect("Bot_DB.db")
        self.db.row_factory = sqlite3.Row #可直接讀取column的名稱

    class Analytics_PageView(graphic_tools.PageView):
        def __init__(self, pages, topic, exe_time):
            super().__init__(pages)
            self.pages = pages #表示分頁方式
            self.current = 0 #目前頁碼
            self.prev.disabled = True
            self.next.disabled = len(pages) <= 1
            self.topic = topic
            self.exe_time = exe_time

        def make_embed(self):
            embed = discord.Embed(
                title = self.topic,
                description=f"第 {self.current+1} / {len(self.pages)} 頁",
                color=discord.Color.from_str("#00F1FF")
            )
            for name, data in self.pages[self.current]:
                embed.add_field(
                name=name,
                value=f"共 {data['count']} 次",
                inline=True
            )
            
            embed.set_footer(text=f"耗時{self.exe_time}s,\nDeveloped by ItsZir, via Discord.py")
            return embed

    @app_commands.command(name="analytics_get_history", description="取得當前頻道的歷史紀錄")
    @app_commands.describe(limit="目前設定上限為30則訊息")
    async def group_get_history(self, interaction: discord.Interaction, limit: int):
        if limit > 30: 
            await interaction.response.send_message("超過設定的訊息數量上限，請重新輸入!", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)

        custom_emoji_pattern = re.compile(r"<a?:\w+:\d+>")
        url_pattern = re.compile(r"https?://\S+")
        # 移除不可見字元的 pattern
        invisible_pattern = re.compile(
            r"[\u200b\u200c\u200d\u200e\u200f"  # 零寬字元、方向控制
            r"\u202a\u202b\u202c\u202d\u202e"   # 方向嵌入控制
            r"\u2060\u2061\u2062\u2063\u2064"   # 文字連接符
            r"\ufeff"                            # BOM
            r"\u00ad"                            # 軟連字符
            r"\u034f]"                           # 組合用間距符
        )

        results = []
        async for msg in interaction.channel.history(limit=limit):
            types = []
            content = msg.content or ""

            # 逐步移除各種非純文字成分
            clean = content
            clean = custom_emoji_pattern.sub("", clean)       # 移除自訂表情
            clean = url_pattern.sub("", clean)                # 移除連結
            clean = emoji_lib.replace_emoji(clean, replace="") # 移除內建 emoji
            clean = invisible_pattern.sub("", clean)          # 移除不可見字元
            clean = clean.strip()

            # 判斷各類型
            has_custom_emoji = bool(custom_emoji_pattern.search(content))
            has_builtin_emoji = bool(emoji_lib.emoji_list(
                custom_emoji_pattern.sub("", content)         # 先移除自訂表情再偵測內建
            ))
            has_url = bool(url_pattern.search(content))
            has_text = bool(clean)                            # 移除所有非文字後還有內容

            if has_text:
                types.append("文字")
            if has_custom_emoji:
                types.append("自訂Emoji")
            if has_builtin_emoji:
                types.append("內建Emoji")
            if has_url:
                types.append("連結")

            # 附件
            for a in msg.attachments:
                ct = a.content_type or ""
                if ct == "image/gif":
                    types.append("GIF")
                elif ct.startswith("image/"):
                    types.append("圖片")
                elif ct.startswith("video/"):
                    types.append("影片")
                elif ct.startswith("audio/"):
                    types.append("音訊")
                elif ct:
                    types.append("檔案")

            # Embed
            for e in msg.embeds:
                if e.type == "gifv":
                    types.append("GIF(Embed)")
                elif e.type == "rich":
                    types.append("Embed")
                elif e.type == "link":
                    pass  # 已被連結偵測涵蓋，不重複標記
                elif e.type == "image":
                    types.append("圖片(Embed)")

            # 其他
            if msg.stickers:
                types.append(f"Sticker({', '.join(s.name for s in msg.stickers)})")
            if msg.poll:
                types.append("投票")

            # 時間
            time_str = msg.created_at.astimezone(
                ZoneInfo("Asia/Taipei")
            ).strftime("%m/%d %H:%M")

            # 純文字長度（移除 emoji 和連結後）
            text_length = len(clean) if has_text else 0

            results.append(
                f"`{msg.author.display_name}` | "
                f"{time_str} | "
                f"{', '.join(types) if types else '（空）'} | "
                f"文字長度:{text_length} | "
                f"內容: {msg.content if text_length > 0 else '（空）'}"
            )
            print(msg.id)

        await interaction.followup.send("\n".join(results), ephemeral=True)

    @app_commands.command(name="analyze_stickers", description="統計頻道貼圖使用紀錄")
    @app_commands.describe(limit="目前上限設定為1000則訊息")
    async def analyze_stickers(self, interaction: discord.Interaction, limit: Optional[int] = 1000):
        if limit > 1000: 
            await interaction.response.send_message("超過設定的訊息數量上限，請重新輸入!", ephemeral=True)
            return
        await interaction.response.defer(ephemeral=True)
        start = time.time()
        from collections import defaultdict

        sticker_stats = defaultdict(lambda: {"count": 0})
        channel = interaction.guild.get_channel(interaction.channel_id)
        guild_sticker_ids = {s.id for s in interaction.guild.stickers}

        #total_count = 0
        async for msg in channel.history(limit=limit):
            for sticker in msg.stickers:
                #total_count += 1
                if sticker.id in guild_sticker_ids:
                    sticker_stats[sticker.name]["count"] += 1
                    #print(f"{total_count}. found sticker msg: {sticker.name}, send by {msg.author.name}, {msg.created_at.astimezone(ZoneInfo("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')}")

        if not sticker_stats:
            await interaction.followup.send("沒有找到任何貼圖訊息", ephemeral=True)
            return

        # 照使用次數排序
        sorted_stats = sorted(sticker_stats.items(), key=lambda x: x[1]["count"], reverse=True)

        per_page = 15 # 切頁
        pages = []
        for i in range(0, len(sorted_stats), per_page):
            pages.append(sorted_stats[i:i+per_page])
        if not pages:
            await interaction.response.send_message("沒有資料")
            return
        
        end = time.time()
        view = self.Analytics_PageView(
            pages,
            topic=f"貼圖使用統計: 共{len(sorted_stats)}種 (最近{limit}筆資料)",
            exe_time=(end - start)
        )
        await interaction.followup.send(embed=view.make_embed(), view=view, ephemeral=True)

    @app_commands.command(name="analytics_get_specific_history", description="取得前面第某筆資料的訊息")
    async def analytics_get_specific_history(self, interaction: discord.Interaction, index: int):
        await interaction.response.defer(ephemeral=True)
        start = time.time()
        i = 0
        async for msg in interaction.channel.history(limit=index):
            if i == index - 1:
                embed = discord.Embed(
                    title=f"前面第{index}筆訊息",
                    color=discord.Color.from_str("#00F1FF")
                )
                embed.add_field(
                    name=f"用戶名稱: {msg.author.display_name}",
                    value=msg.content
                )
                end = time.time()
                embed.set_footer(text=f"傳送時間: {msg.created_at.astimezone(ZoneInfo("Asia/Taipei")).strftime('%Y-%m-%d %H:%M:%S')}\n搜尋耗時{end-start}秒")
                await interaction.followup.send(embed=embed, ephemeral=True)
                break
            
            i += 1

    #------ Detect Message ------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot: return

#setup function for each Cog file
async def setup(bot: commands.Bot):
    await bot.add_cog(Analytics(bot))