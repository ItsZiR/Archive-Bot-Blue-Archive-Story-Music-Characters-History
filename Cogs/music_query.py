import discord
from discord import app_commands
from discord.ext import commands
import sqlite3
import sys, os
import random, asyncio, time
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

        self.channels_in_game : set = set()

    def get_track_model(self, sql_result) -> models.SoundTrack:
        #------------ 資料表欄位相關更新 ------------
        track = models.SoundTrack(
                file_path = sql_result['File_path'],
                number = sql_result['Number'],
                name = sql_result['Name'],
                key = sql_result['Key'],
                bpm = sql_result['BPM'],
                duration = sql_result['Duration'],
                composer = sql_result['Composer'],
                type = sql_result['Type'],
                comment1 = sql_result['Comment1'],
                comment2 = sql_result['Comment2'],
                style = sql_result['Style'],
                genre = sql_result['Genre'],
                song_type = sql_result['Song_type'],
                server = sql_result['Server'],
                released_day = sql_result['Released_day'],
                first_use = sql_result['First_use'],
                mtime = sql_result['mtime'],
                last_sync_time = sql_result['last_sync_time']
            )
        
        return track

    #------------ 用編號查詢 ------------
    @app_commands.command(name="ost_num_query", description="以編號查詢OST")
    @app_commands.describe(number="您想查詢的編號為？")
    async def ost_num_query(self, interaction: discord.Interaction, number: int):
        await interaction.response.defer()

        self.cursor.execute(sql_commands.ost_num_query_sql(self.table, number))

        result = self.cursor.fetchone()
        if not result: await interaction.response.send_message("該編號不存在，或是尚未公開")
        else:
            track : models.SoundTrack = self.get_track_model(result)

            if not track.name: track.name = "未命名"
            if not track.composer: track.composer = "未公布"

            embed = discord.Embed(
                title = (f"歌曲資訊 : {track.name}"),
                color = discord.Color.from_str("#00F1FF")
            )
            if track.comment1:
                embed.description = f"**{track.comment1}**"

            track_data = f"- No. {track.number}, Key: {track.key}, BPM: {track.bpm}, 長度: {track.duration}"
            track_data.join(f"\n作者: {track.composer}\n首次使用日期: {track.released_day}, 首次使用場合: {track.first_use}")

            embed.add_field(name="歌曲基本資訊", value=track_data, inline=False)
            embed.add_field(name="歌曲風格:", value=track.style, inline=False)

            if track.first_use:
                embed.add_field(name="首次使用場合:", value=track.first_use, inline=True)

            embed.add_field(name="首次出現時間:", value=track.released_day, inline=True)

            if track.comment2:
                embed.add_field(name="", value=(f"{track.comment2}"), inline=False)
            
            embed.set_footer(text=f"Developed by ItsZir, via Discord.py")

            await interaction.followup.send(
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
        await interaction.response.defer()

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
            data : models.SoundTrack = self.get_track_model(track)
            
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
        await interaction.followup.send(embed=embed)

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
    @app_commands.command(name="ost_num_random", description="隨機推播一首有編號的OST")
    async def ost_num_random(self, interaction: discord.Interaction):
        await interaction.response.defer()

        self.cursor.execute(sql_commands.ost_num_random_sql())
        data = self.cursor.fetchall()
        random.shuffle(data)
        result = data[random.randint(0, (len(data)-1))]

        track : models.SoundTrack = self.get_track_model(result)

        if not track.name: track.name = "未命名"
        if not track.composer: track.composer = "未公布"

        embed = discord.Embed(
            title = (f"隨機歌曲推播 : No. {track.number}, {track.name}"),
            color = discord.Color.from_str("#00F1FF")
        )
        if track.comment1:
            embed.description = f"**{track.comment1}**"

        track_data = f"- Key: {track.key}, BPM: {track.bpm}, 長度: {track.duration}"
        track_data.join(f"\n作者: {track.composer}\n首次使用日期: {track.released_day}, 首次使用場合: {track.first_use}")

        embed.add_field(name="歌曲基本資訊", value=track_data, inline=False)
        embed.add_field(name="歌曲風格:", value=track.style, inline=False)

        if track.first_use:
            embed.add_field(name="首次使用場合:", value=track.first_use, inline=True)

        embed.add_field(name="首次出現時間:", value=track.released_day, inline=True)

        if track.comment2:
            embed.add_field(name="", value=(f"{track.comment2}"), inline=False)
        
        embed.set_footer(text=f"Developed by ItsZir, via Discord.py")

        await interaction.followup.send(
            embed=embed,
            file=discord.File(
                track.file_path,
                filename=f"No. {track.number}, {track.name}.mp3"
            )
        )

    #------------ 猜OST小遊戲 ------------
    @app_commands.command(name="guess_ost_game", description="隨機猜OST的小遊戲")
    async def guess_ost_game(self, interaction: discord.Interaction):
        #偵測當前頻道有無進行中的遊戲
        current_channel_id = interaction.channel_id
        if current_channel_id in self.channels_in_game:
            await interaction.response.send_message("當前頻道已有進行中的遊戲。", ephemeral=True)
            return
        else:
            self.channels_in_game.add(current_channel_id)
        
        #隨機抽選ost
        #------
        self.cursor.execute(sql_commands.ost_num_random_sql())
        data = self.cursor.fetchall()
        random.shuffle(data)
        result = data[random.randint(0, (len(data)-1))]

        track : models.SoundTrack = self.get_track_model(result)
        answer : int = track.number
        #------

        #遊戲資訊
        GAME_TIMEOUT_SECONDS = 30.0
        start_time = time.time()

        #使用command後傳送mp3跟訊息
        await interaction.response.send_message(
            content="猜猜以下ost的編號, 限制時間: 30秒",
            file=discord.File(
                track.file_path,
                filename="Blue Archive OST.mp3"
            )
        )
        print(answer)

        #給bot.wait_for來做確認的check function, 過濾掉其他頻道傳送的跟bot的訊息
        def check_msg(msg: discord.Message):
            return (
                (not msg.author.bot)
                and (msg.channel == interaction.channel)
            )
        try:
            #在時間內重複做判斷
            while True:
                elapsed_time = time.time() - start_time #計算遊戲開始後, 當下過了幾秒
                remaining_time = GAME_TIMEOUT_SECONDS - elapsed_time #計算離遊戲結束還剩下幾秒

                try:
                    #偵測用戶輸入
                    msg = await self.bot.wait_for('message', check=check_msg, timeout=remaining_time)
                    
                    #移除多餘空格並判斷是否為數字, 否則跳過本次判斷
                    cleaned_msg = msg.content.replace(" ", "")
                    if not cleaned_msg.isdigit(): continue

                    #答案正確
                    elif int(cleaned_msg) == answer:
                        await interaction.followup.send(f"🎉 正確！{interaction.user.mention}")
                        break
                
                #前面msg在timeout時的動作, 結束遊戲
                except asyncio.TimeoutError:
                    await interaction.followup.send(f"⏰ 時間到！正確答案是 **No. {answer}**！！！")
                    break
        finally:
            self.channels_in_game.discard(current_channel_id) #不論遊戲結果都釋放當前頻道id
    
#setup function for each Cog file
async def setup(bot: commands.Bot):
    await bot.add_cog(Music_Query(bot))