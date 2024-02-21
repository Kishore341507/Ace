import discord
from discord.ext import commands 
from database import *
from discord.ui import button, Button, View
from discord.ext.commands import BucketType, cooldown
import asyncio

class BankRob(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.participants = {}

    class HeistView(View):
        def __init__(self, heist_data, timeout):
            super().__init__(timeout=timeout)
            self.data = heist_data
            self.reports = []
     
        @button(label="Join Heist", emoji="💰", style=discord.ButtonStyle.blurple, custom_id="join_heist")
        async def join_heist(self, interaction: discord.Interaction, Button: discord.Button):
            await interaction.response.defer()
            if int(datetime.now().timestamp()) > self.data["end_timestamp"]:
                return await interaction.response.send_message("The heist has ended and you can't participate in the heist anymore", ephemeral=True)
            elif interaction.user.id in self.data['participants']:
                return await interaction.response.send_message("You are already a participant of this heist.", ephemeral = True)
            elif len(self.data['participants']) >= self.data['limit']:
                return await interaction.response.send_message("This heist has finished gathering all the heist members, they are not looking for any more participants.", ephemeral=True)
            else:
                self.data[participants].append(interaction.user)
                await interaction.response.edit_message(embed=bembed(f"<@{data['leader']}> has initiated a heist against <@{data['target']}>. `{len(self.data['participants'])}/{self.data['participants']}` members have joined the heist. The heist ends <t:{self.participants[ctx.guild.id]['end_timestamp']}:R>."))
                await interaction.followup.send("You have successfully joined the heist. ✅", ephemeral = True)

        @button(label="Report Heist", emoji="⌚", style=discord.ButtonStyle.red, custom_id="report_heist")
        async def report_heist(self, interaction: discord.Interaction, Button: discord.Button):
            await interaction.response.defer()
            self.reports.append(interaction.user.id)
            if interaction.user.id == self.data['target'] or len(self.reports) >= self.data['reports']:
                self.stop
            else:
                interaction.response.send_message("The report has been recieved successfully.")

    @commands.command(aliases=['h'])
    @commands.check(check_perms)
    @cooldown(1, 1, BucketType.member)
    async def heist(self, ctx, target:discord.Member = None, timeout: int = 15, required_members: int = 2, required_reports: int = 2):
        target = target or ctx.author
        if ctx.guild.id in self.participants:
            await ctx.send(embed=bembed(f"{ctx.author.mention}, a heist is already in progress at the moment.!"))
            ctx.command.reset_cooldown(ctx)
            return
        else:
            self.participants[ctx.guild.id] = {"leader": ctx.author.id ,"participants": [ctx.author.id], "target": target.id, "end_timestamp": int(datetime.now().timestamp()+timeout), "limit": required_members, "reports": required_reports}
        
        view = BankRob.HeistView(self.participants[ctx.guild.id], timeout)
        msg = await ctx.send(embed=bembed(f"{ctx.author.mention} has initiated a heist against {target.mention}. `{len(self.participants[ctx.guild.id]['participants'])}/{required_members}` members have joined the heist. The heist ends <t:{int(self.participants[ctx.guild.id]['end_timestamp'])}:R>."), view=view)

        await view.wait()
        for item in view.children:
            item.disabled = True
        await msg.edit(content="**This heist has already ended.**", embed=bembed(f"{ctx.author.mention} has initiated a heist against {target.mention}. `{len(self.participants[ctx.guild.id]['participants'])}/{required_members}` members have joined the heist. The heist ended <t:{int(self.participants[ctx.guild.id]['end_timestamp'])}:R>."), view=view)
        participants = [f"<@{participant}>" for participant in view.data['participants']]
        participants = ','.join(participants)
        if view.reports and len(view.reports) > view.data['reports']:
            await msg.reply(f"{participants} a lot of user have suspected something suspicious was going an and the police has been made aware regarding the heist resulting in the failure of the heist.")
        if len(view.data['participants']) >= view.data['limit']:
            await msg.reply(f"{participants}, the heist was successful.")
        else:
            await msg.reply(f"{participants}, the heist failed.")
        self.participants.pop(ctx.guild.id, None)

async def setup(client):
    await client.add_cog(BankRob(client))