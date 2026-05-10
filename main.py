import discord
from discord import app_commands
from discord.ext import commands
import os, json

class BOT(commands.Bot):
    def __init__(self):
        #設定 Bot 的權限(Intents)
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="~", intents=intents)

    async def setup_hook(self):
        print("------ 初始化 ------")
        count = 0
        for filename in os.listdir('./Cogs'):
            if filename.endswith('.py'):
                if filename.startswith("_"): continue
                await self.load_extension(f'Cogs.{filename[:-3]}')
                print(f'\t已載入模組: {filename}')
                count += 1
        
        print(f"同步了 {count} 個模組......")

        print("載入Command列表指令......")
        self.tree.add_command(
            app_commands.Command(
                name = "cmd_list",
                description = "Command List",
                callback=self.cmd_list
            )
        )

        print("載入手動刷新功能......")
        self.tree.add_command(
            app_commands.Command(
                name = "reload",
                description = "Update Slash Commands",
                callback=self.reload
            )
        )

        print("載入卸載模組功能......")
        unload_cmd = app_commands.Command(
            name = "unload",
            description = "Unload Slash Commands",
            callback=self.unload
            )
        unload_cmd.autocomplete("extension")(self.unload_autocomplete)
        self.tree.add_command(unload_cmd)

        print("------ Slash Command 列表 ------")
        commands_list = self.tree.get_commands()
        print("\n".join([f"• /{cmd.name} : {cmd.description}" for cmd in commands_list]))

        print("...... 初始化結束，開始同步指令 :")

    async def on_ready(self):
        try:
            print("............")
            await self.tree.sync(guild=None)
            print(f"✅ 全域指令同步成功！")
            print(f"Slash Commands 同步完成！共加載了{len(self.tree.get_commands())}個command.")
            print("............")
            await self.change_presence(activity=discord.Game("蘿莉"))
            print(f'機器人已上線: {self.user} (ID: {self.user.id})')
            print('------')
        except Exception as e:
            print(e)
    
    #------------ Core Slash Command ------------
    async def cmd_list(self, interaction: discord.Interaction):
        commands_list = self.tree.get_commands()
        if not commands_list:
            await interaction.response.send_message("目前沒有載入任何指令。", ephemeral=True)
            return
        
        format = "\n".join([f"• `/{cmd.name}`: {cmd.description}" for cmd in commands_list])
        
        embed = discord.Embed(
            title = "📋 目前載入的指令列表",
            description = format,
            color=discord.Color.from_str("#00F1FF")
        )
    
        await interaction.response.send_message(embed=embed, ephemeral=True)

    async def reload(self, interaction: discord.Interaction):
        print("------ 手動刷新指令 ------")
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id != 503484838029033483:
            await interaction.followup.send(" ❌ 未持有執行該指令的權限!")
            return
        try:
            count = 0
            for filename in os.listdir('./Cogs'):
                if filename.endswith('.py'):
                    if filename.startswith("_"): continue
                    try:
                        await self.reload_extension(f'Cogs.{filename[:-3]}')
                    except:
                        await self.load_extension(f'Cogs.{filename[:-3]}')
                    print(f'\t已重新載入模組: {filename}')
                    count += 1
        
            print(f"重新同步了 {count} 個模組......")

            print("全球同步中......")
            await self.tree.sync(guild=None)
            print(f" ✅ Slash Commands 手動同步完成！共加載了{len(self.tree.get_commands())}個command.")

            await interaction.followup.send(f"所有模組與Slash Commands已同步完成！\n共加載了{len(self.tree.get_commands())}個指令。請按Ctrl + R來刷新Discord快取，以使用最新版的指令。")

            print("------ Slash Command 列表 ------")
            commands_list = self.tree.get_commands()
            print("\n".join([f"• /{cmd.name} : {cmd.description}" for cmd in commands_list]))

        except Exception as e:
            print(e)
            await interaction.followup.send(f" ❌ 載入失敗 : {e}")

    async def unload(self, interaction: discord.Interaction, extension:str):
        await interaction.response.defer(ephemeral=True)
        if interaction.user.id != 503484838029033483:
            await interaction.followup.send(" ❌ 未持有執行該指令的權限!")
            return
        else:
            try:
                ext_path = f"{extension}"
            
                await self.unload_extension(ext_path)
                await self.tree.sync()
            
                await interaction.followup.send(f"✅ 已成功卸載模組：`{extension}`", ephemeral=True)
                print(f"系統訊息：模組 {extension} 已手動卸載。")
            except Exception as e:
                print(e)
                await interaction.followup.send(f" ❌ 卸載失敗 : {e}")

    async def unload_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        loaded_ext = list(self.extensions.keys())
        choice = [
            app_commands.Choice(name=ext, value=ext)
            for ext in loaded_ext
        ]

        return choice

    #------ Detect Message ------
    async def on_message(self, message: discord.Message):
        if message.author.bot: return

        if "黑" in message.content or "尼" in message.content:
            await message.reply("欸 嚴厲斥責一切偏激歧視言論 你發瘋了啊 我再說一次 不管你是同性戀雙性戀紙性戀泛性戀非二元性別變裝皇后等等 只要不違反中華民國法律以及圖奇社群規範 我都支持 好嗎", mention_author=False)

bot = BOT()
bot.run(json.load(open("token.json", "r"))["bot_token"])