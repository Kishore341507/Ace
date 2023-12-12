import discord
from discord.ext import commands
from discord.ui import Button , View , Select , TextInput
from database import *
from discord.ext.commands import BucketType, cooldown
from datetime import datetime 
from discord import app_commands

class helpview(discord.ui.View):
    def __init__(self):
        super().__init__()


    @discord.ui.select(placeholder='Select Catogory', min_values=1, max_values=1, options= [
            discord.SelectOption(label='ECONOMY' , emoji= "⚙️"),
            discord.SelectOption(label='INCOME' , emoji= "⚙️"),
            discord.SelectOption(label='GAMES' , emoji= "⚙️"),
            discord.SelectOption(label='PVC' , emoji= "⚙️"),
            discord.SelectOption(label='STORE' , emoji= "⚙️"),
            discord.SelectOption(label='ADMIN COMMANDS' , emoji= "⚙️"),
        ])
    async def callback1(self, interaction: discord.Interaction , select):
        embed = discord.Embed(color= discord.Color.blue() , title= "HELP SECTION" )
        if select.values[0] == 'ECONOMY':
            embed.description = "```ECONOMY```\n***__deposit__:*** Deposit money to your bank\n\n*USAGE:*\n``deposit <amount or all>``\n\n*Example*\ndeposit 500\ndeposit all\n---------------------------------------------------------------------------------------------- \n***__withdraw__:*** Withdraw money from your bank\n\n*USAGE*\n``withdraw <amount or all>``\n\n*Example*\nwithdraw 100\nwithdraw all\n---------------------------------------------------------------------------------------------- \n***__give:__*** Give money to your bank \n\n*USAGE*\n``give-money [user] <amount or all>``\n\n*Example*\ngive-money @user 480\n---------------------------------------------------------------------------------------------- \n***__reseteconomy__ :*** Reset a member balance\n\n*USAGE*\n``reseteconomy [user]``\n---------------------------------------------------------------------------------------------- \n***__leaderboard:__*** View your server money leaderboard \n\n*USAGE*\n``leaderboard [page] [-cash | -bank | -total]``\n---------------------------------------------------------------------------------------------- \n***__profile:__*** It shows your casino profile \n\n*USAGE*\n``profile ``\n---------------------------------------------------------------------------------------------- \n"
            await interaction.response.edit_message(embed = embed , view = self)
        elif select.values[0] == 'INCOME':
            embed.description = "```INCOME```\n***__collect__:*** Collect your income role\n\n*USAGE*\n``collect``\n---------------------------------------------------------------------------------------------- \n***__work__:*** Quick cash command\n\n*USAGE*\n``work``\n---------------------------------------------------------------------------------------------- \n***__crime__:*** Quick cash command\n\n*USAGE*\n``crime``\n---------------------------------------------------------------------------------------------- \n***__rob__:*** Attempt to rob another user money\n\n*USAGE*\n``rob [user]``\n---------------------------------------------------------------------------------------------- \n"
            await interaction.response.edit_message(embed = embed , view = self)
        elif select.values[0] == 'GAMES':
            embed.description = "```GAMES```\n**__BJ:__** Play a game of blackjack \n\n*USAGE*\n``bj <amount>``\n-----------------------------------------------------------------------------------------------\n***__ST:__*** Play a game of slot \n\n*USAGE*\n``st <amount> ``\n---------------------------------------------------------------------------------------------- \n***__BF:__*** Play a game of bankflip \n\n*USAGE*\n``bf <user> <amount> ``\n---------------------------------------------------------------------------------------------- \n***__CF__:*** Play a game of coinflip \n\n*USAGE*\n``cf <amount> < head | tail \ H | T>``\n---------------------------------------------------------------------------------------------- \n***__ROLL:__ ***Play a game of dice roll \n\n*USAGE*\n``roll <amount> [odd | even \ number (1to 6)]`` \n----------------------------------------------------------------------------------------------\n***__PF__:*** Play a game of petfight \n\n*USAGE*\n``pf <amount> ``\n\n---------------------------------------------------------------------------------------------- \n***__RF__:*** Bet in the slot machine \n\n*USAGE*\n``rf [user] <amount>`` \n---------------------------------------------------------------------------------------------- \n***__RR__:*** Play a game of russian roulette \n\n*USAGE*\n``rr <amount> ``\n---------------------------------------------------------------------------------------------- \n"
            await interaction.response.edit_message(embed = embed , view = self)
        elif select.values[0] == 'PVC':
            embed.description = "```PVC```\n***__pvc:__*** Used to create  PVC\n\n*USAGE*\n``pvc <duration>``\n---------------------------------------------------------------------------------------------- \n***__adduser:__*** Add a member to your PVC\n\n*USAGE*\n``au < user >``\n---------------------------------------------------------------------------------------------- \n***__extend:__*** Extend your PVC\n\n*USAGE*\n``e < duration >``\n----------------------------------------------------------------------------------------------\n***__removeuser:__*** Remove a member from your PVC\n\n*USAGE*\n``ru < user >``\n----------------------------------------------------------------------------------------------\n***__rename:__*** Renames your PVC\n\n*USAGE*\n``rename < name >``\n----------------------------------------------------------------------------------------------\n***__transferownership:__*** Transfer your PVC ownership  \n\n*USAGE*\n``to < user >``\n----------------------------------------------------------------------------------------------\n"
            await interaction.response.edit_message(embed = embed , view = self)
        elif select.values[0] == 'STORE':
            embed.description = "```STORE```\n***__buyitem:__*** Buy item from the store\n\n*USAGE*\n``[buyitem | buy] <itemid>``\n----------------------------------------------------------------------------------------------\n***__iteminfo:__*** View information on an item in the shop \n\n*USAGE*\n``iteminfo <id>``\n----------------------------------------------------------------------------------------------\n***__sellitem:__*** Sell item from your inventory \n\n*USAGE*\n``[sellitem | sell] <item_id>``\n----------------------------------------------------------------------------------------------\n:gear: ***__addpet:__*** Add pet to Pet shop \n\n*USAGE*\naddpet <emoji>\n----------------------------------------------------------------------------------------------\n:gear: ***__removepet:__*** Remove pet from pet shop\n\n*USAGE*\n``removepet <emoji>``\n----------------------------------------------------------------------------------------------\n***__buypet:__*** Buy pet from pet shop \n\n*USAGE*\n``[buypet | petshop] [no=None]``\n----------------------------------------------------------------------------------------------\n***__setpetname:__*** Set your pet nick name\n\n*USAGE*\n``setpetname <name>``\n----------------------------------------------------------------------------------------------\n***__sellpet:__*** Sell pet from your inventory \n\n*USAGE*\n``sellpet ``\n----------------------------------------------------------------------------------------------\n"
            await interaction.response.edit_message(embed = embed , view = self)
        elif select.values[0] == 'ADMIN COMMANDS':
            embed.description = "```ADMIN COMMANDS```\n:gear: ***__ addmoney__:*** Add money to a member\n\n*USAGE:*\n``addmoney <user> <amount> [bank | cash | pvc = bank]``\n\n*EXAMPLE*\naddmoney @user 350\n----------------------------------------------------------------------------------------------\n:gear: ***__ addchannel__:*** Enable bot command in particular channel\n\n*USAGE:*\n``addchannel <channel>``\n----------------------------------------------------------------------------------------------\n:gear: ***__removemoney__:*** Remove money from a member\n\n*USAGE:*\n``addmoney <user> <amount> [bank | cash | pvc = bank]``\n\n*EXAMPLE*\nremovemoney @user 350\n----------------------------------------------------------------------------------------------\n```INCOME```\n:gear: ***__chatmoney__:*** Set the amount for chat moeny\n\n*USAGE*\n``chatmoney <cash | pvc > <amount>``\n----------------------------------------------------------------------------------------------\n:gear: ***__roleincome__:*** Set the amount for role \n\n*USAGE*\n``roleincome <add | remove | list> [role=None] [amount=None]``\n```OTHER```\n:gear: ***__rebootbot:__*** Reset all the bot settings\n\n*USAGE*\n``rebootbot ``\n----------------------------------------------------------------------------------------------\n:gear: ***__prefix:__*** Change bot prefix \n\n*USAGE*\n``prefix <new prefix>``\n----------------------------------------------------------------------------------------------\n:gear: ***__manager:__*** Can manage casino\n\n*USAGE*\n``manager <role>``\n----------------------------------------------------------------------------------------------\n```PVC```\n:gear: *** __pvcchannel:__*** Command to be executed in particular channel\n\n*USAGE*\n``pvcchannel <channel>``\n----------------------------------------------------------------------------------------------\n:gear: ***__pvccategory:__*** Create PVC for a particular category \n\n*USAGE*\n``pvccategory <channel>``\n----------------------------------------------------------------------------------------------\n:gear: ***__enablepvc:__*** Enable PVC for the server \n\n*USAGE*\n``enablepvc <channel>``\n----------------------------------------------------------------------------------------------\n:gear: ***__disablepvc:__*** Disable PVC for the server \n\n*USAGE*\n``disablepvc ``\n----------------------------------------------------------------------------------------------\n:gear: ***__pvcbuttons:__*** Create PVC buttons\n\n*USAGE*\n``pvcbuttons ``\n----------------------------------------------------------------------------------------------\n:gear: ***__rate:__*** PVC rate \n\n*USAGE*\n``rate <amountperhr>``\n----------------------------------------------------------------------------------------------\n```STORE```\n:gear: ***__additem:__*** Add item for your store\n\n*USAGE*\n``[additem | createitem] <name>``\n----------------------------------------------------------------------------------------------\n:gear: ***__edit item__***: Edit item in the store \n\n*USAGE*\n``edititem <item_id> <attribute> <details>``\n----------------------------------------------------------------------------------------------\n:gear: ***__removeitem:__*** Remove item from your store   \n\n*USAGE*\n``removeitem <item_id>``\n----------------------------------------------------------------------------------------------"
            await interaction.response.edit_message(embed = embed , view = self)


class help(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.count = 1
        
    async def check_channel(ctx) ->bool : 
        return ctx.channel.id in channel or ctx.author.id == 591011843552837655    

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 1000 , BucketType.user)
    # async def help(self, ctx):
    #     view = helpview()
    #     embed = discord.Embed(color= discord.Color.blue() , title= "HELP SECTION" )
    #     embed.description = "```ADMIN COMMANDS```\n:gear: ***__ addmoney__:*** Add money to a member\n\n*USAGE:*\n``addmoney <user> <amount> [bank | cash | pvc = bank]``\n\n*EXAMPLE*\naddmoney @user 350\n----------------------------------------------------------------------------------------------\n:gear: ***__ addchannel__:*** Enable bot command in particular channel\n\n*USAGE:*\n``addchannel <channel>``\n----------------------------------------------------------------------------------------------\n:gear: ***__removemoney__:*** Remove money from a member\n\n*USAGE:*\n``addmoney <user> <amount> [bank | cash | pvc = bank]``\n\n*EXAMPLE*\nremovemoney @user 350\n----------------------------------------------------------------------------------------------\n```INCOME```\n:gear: ***__chatmoney__:*** Set the amount for chat moeny\n\n*USAGE*\n``chatmoney <cash | pvc > <amount>``\n----------------------------------------------------------------------------------------------\n:gear: ***__roleincome__:*** Set the amount for role \n\n*USAGE*\n``roleincome <add | remove | list> [role=None] [amount=None]``\n```OTHER```\n:gear: ***__rebootbot:__*** Reset all the bot settings\n\n*USAGE*\n``rebootbot ``\n----------------------------------------------------------------------------------------------\n:gear: ***__prefix:__*** Change bot prefix \n\n*USAGE*\n``prefix <new prefix>``\n----------------------------------------------------------------------------------------------\n:gear: ***__manager:__*** Can manage casino\n\n*USAGE*\n``manager <role>``\n----------------------------------------------------------------------------------------------\n```PVC```\n:gear: *** __pvcchannel:__*** Command to be executed in particular channel\n\n*USAGE*\n``pvcchannel <channel>``\n----------------------------------------------------------------------------------------------\n:gear: ***__pvccategory:__*** Create PVC for a particular category \n\n*USAGE*\n``pvccategory <channel>``\n----------------------------------------------------------------------------------------------\n:gear: ***__enablepvc:__*** Enable PVC for the server \n\n*USAGE*\n``enablepvc <channel>``\n----------------------------------------------------------------------------------------------\n:gear: ***__disablepvc:__*** Disable PVC for the server \n\n*USAGE*\n``disablepvc ``\n----------------------------------------------------------------------------------------------\n:gear: ***__pvcbuttons:__*** Create PVC buttons\n\n*USAGE*\n``pvcbuttons ``\n----------------------------------------------------------------------------------------------\n:gear: ***__rate:__*** PVC rate \n\n*USAGE*\n``rate <amountperhr>``\n----------------------------------------------------------------------------------------------\n```STORE```\n:gear: ***__additem:__*** Add item for your store\n\n*USAGE*\n``[additem | createitem] <name>``\n----------------------------------------------------------------------------------------------\n:gear: ***__edit item__***: Edit item in the store \n\n*USAGE*\n``edititem <item_id> <attribute> <details>``\n----------------------------------------------------------------------------------------------\n:gear: ***__removeitem:__*** Remove item from your store   \n\n*USAGE*\n``removeitem <item_id>``\n----------------------------------------------------------------------------------------------"
    #     try:
    #         await ctx.author.send(embed = embed , view = view)
    #         await ctx.send("Check your DM's")
    #         ctx.command.reset_cooldown(ctx)
    #     except :
    #         await ctx.send(embed = embed , view = view)
    
    @commands.hybrid_command()
    @commands.is_owner()
    async def update_presence_home(self , ctx , status : str):
        await self.client.change_presence(activity=discord.Game(name=status))
        await ctx.send("done")

    

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 21600.0, key=lambda i: (i.guild_id, i.user.id))
    async def confess(self, interaction :discord.Interaction , *, text:str):

      embed = discord.Embed( title = f"Confession"  , color = discord.Color.blue() , description = text )
      embed.set_footer(text = "Type `/confess` to admit your deepest darkest secrets")
      if len(text) > 900 :
        await interaction.response.send_message(f"too long , limit is 300\nyour text = {text}" , ephemeral= True)
        return

      for user in self.client.application.team.members:
        member = interaction.guild.get_member(user.id)
        try : await member.send(f"{interaction.user.name} , {interaction.user.id} , {interaction.user.guild.name}" , embed = embed)
        except : pass
        
      msg = await interaction.channel.send(embed = embed)
      
      await interaction.response.send_message(f"Confession sended to the channel [click here to read]({msg.jump_url})" , ephemeral= True)    
        

    @confess.error
    async def bj_error(self ,ctx ,error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"cooldown")
        else : 
            await client.application.owner.send(f'{error}')
            await ctx.reply("🤫 Not here , jump into my DM's")
            ctx.command.reset_cooldown(ctx)
            return

async def setup(client):
   await client.add_cog(help(client))