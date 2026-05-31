import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import sys, os
import random
'''
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if project_root not in sys.path:
    sys.path.append(project_root)
'''
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from SQL_Commands import sql_commands
from Data_Models import models
from Graphic_Tools import graphic_tools

#--------------------------------------------------------------------------------------------------

class Music_Query(commands.Cog):
    def __init__(self, bot:commands.Bot):
        self.bot = bot

        self.db = sqlite3.connect("Bot_DB.db")
        self.db.row_factory = sqlite3.Row #可直接讀取column的名稱
        self.table = "BA_Music"
        self.cursor = self.db.cursor()

    #------------ 用編號查詢 ------------
    @app_commands.command(name="ost_num_query", description="以編號查詢OST")
    @app_commands.describe(number="您想查詢的編號為？")
    async def ost_num_query(self, interaction: discord.Interaction, number: int):
        self.cursor.execute(sql_commands.ost_num_query_sql(self.table, number))

        result = self.cursor.fetchone()
        if not result: await interaction.response.send_message("該編號不存在，或是尚未公開")
        else:
            #------------ 資料表欄位相關更新 ------------
            track = models.SoundTrack(
                file_path = result['File_path'],
                number = result['Number'],
                name = result['Name'],
                key = result['Key'],
                bpm = result['BPM'],
                duration = result['Duration'],
                composer = result['Composer'],
                type = result['Type'],
                comment1 = result['Comment1'],
                comment2 = result['Comment2'],
                style = result['Style'],
                genre = result['Genre'],
                song_type = result['Song_type'],
                server = result['Server'],
                released_day = result['Released_day'],
                first_use = result['First_use'],
                mtime = result['mtime'],
                last_sync_time = result['last_sync_time']
            )

            if not track.name: track.name = "未命名"
            if not track.composer: track.composer = "未公布"

            embed = discord.Embed(
                title = (f"歌曲資訊 : {track.name}"),
                color = discord.Color.from_str("#00F1FF")
            )
            if track.comment1:
                embed.description = f"**{track.comment1}**"

            track_data = f"- No. {track.number}, Key: {track.key}, BPM: {track.bpm}, 長度: {track.duration}s"
            track_data.join(f"\n作者: {track.composer}\n首次使用日期: {track.released_day}, 首次使用場合: {track.first_use}")

            embed.add_field(name="歌曲基本資訊", value=track_data, inline=False)
            embed.add_field(name="歌曲風格:", value=track.style, inline=False)

            if track.first_use:
                embed.add_field(name="首次使用場合:", value=track.first_use, inline=True)

            embed.add_field(name="首次出現時間:", value=track.released_day, inline=True)

            if track.comment2:
                embed.add_field(name="", value=(f"{track.comment2}"), inline=False)
            
            embed.set_footer(text=f"Developed by ItsZir, via Discord.py")

            await interaction.response.send_message(
                embed=embed,
                file=discord.File(
                    track.file_path,
                    filename=f"No. {track.number}, {track.name}.mp3"
                )
            )

    #------------ 用作者查詢 ------------
    @app_commands.command(name="ost_composer_tracks_query", description="以作曲者查詢OST")
    @app_commands.describe(composer="您想查詢的作曲者為？")
    async def ost_composer_tracks_query(self, interaction: discord.Interaction, composer:str):
        self.cursor.execute(sql_commands.ost_composer_tracks_query_sql(self.table), (composer,))
        result_tracks = self.cursor.fetchall()

        embed = discord.Embed(
            title = (f"- 作曲者 : {composer}"),
            description = (f"### 🎵 OST作品 : {len(result_tracks)}首"),
            color = discord.Color.from_str("#00F1FF"),
            timestamp = interaction.created_at
        )

        soundtrack_list = song_list = ""
        song_count = soundtrack_count = 0
        for track in result_tracks:
            #------------ 資料表欄位相關更新 ------------
            data = models.SoundTrack(
                file_path = track['File_path'],
                number = track['Number'],
                name = track['Name'],
                key = track['Key'],
                bpm = track['BPM'],
                duration = track['Duration'],
                composer = track['Composer'],
                type = track['Type'],
                comment1 = track['Comment1'],
                comment2 = track['Comment2'],
                style = track['Style'],
                genre = track['Genre'],
                song_type = track['Song_type'],
                server = track['Server'],
                released_day = track['Released_day'],
                first_use = track['First_use'],
                mtime = track['mtime'],
                last_sync_time = track['last_sync_time']
            )
            
            if data.type == "Song":
                song_list += (f"\n🎵 `{data.name} | key: {data.key}, BPM: {data.bpm}, 長度: {data.duration}, 公布日期: {data.released_day}`")
                song_count += 1
                
            else:
                num = "-" if not data.number else data.number
                name = "" if not data.name else (f", {data.name}")
                soundtrack_list += (f"\n🎵 `Track No. {num}{name} | key: {data.key}, BPM: {data.bpm}, 長度: {data.duration}, 公布日期: {data.released_day}`")
                soundtrack_count += 1

        #調整輸出song清單的格式
        if song_count <= 10:
            #小於10首則照常列出
            song_title = f"- 歌曲: {song_count}首"
        else:
            #超過10首則啟用隨機推播功能
            song_title = f"- 歌曲: {song_count}首 (隨機推播10首)"
            song_rng = random.sample(song_list.splitlines(), 10)
            song_list = "\n".join(f"{track}" for track in song_rng)
        embed.add_field(name = song_title, value = song_list, inline=False)

        embed.add_field(name="------------", value="", inline=False)

        #調整輸出soundtrack清單的格式
        if soundtrack_count <= 10:
            #小於10首則照常列出
            soundtrack_title = f"- BGM: {soundtrack_count}首"
        else:
            #超過10首則啟用隨機推播功能
            soundtrack_title = f"- BGM: {soundtrack_count}首 (隨機推播10首)"
            soundtrack_rng = random.sample(soundtrack_list.splitlines(), 10)
            soundtrack_list = "\n".join(f"{track}" for track in soundtrack_rng)
        embed.add_field(name = soundtrack_title, value = soundtrack_list, inline=False)

        embed.set_footer(text=f"Developed by ItsZir, via Discord.py")
        await interaction.response.send_message(embed=embed)

    @ost_composer_tracks_query.autocomplete("composer")
    async def ost_composer_tracks_query_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str #user目前輸入值
    ) -> list[app_commands.Choice[str]]:
        query_sql = ''' 
            SELECT Distinct Composer
            FROM {}
            WHERE Composer LIKE ?
            LIMIT 25
        '''.format(self.table)

        self.cursor.execute(query_sql, (f"%{current}%",))
        result = self.cursor.fetchall()

        choice = [
            app_commands.Choice(name=row[0], value=row[0])
            for row in result if row[0]
        ]

        return choice

    #------------ 歌曲隨機推播 ------------
    
#setup function for each Cog file
async def setup(bot: commands.Bot):
    await bot.add_cog(Music_Query(bot))