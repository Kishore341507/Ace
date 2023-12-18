from http import client
import discord
from discord.ext import commands 
from database import *
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
import typing
from datetime import datetime
from comp.ui import *

class Confirm(discord.ui.View):
    def __init__(self , user = None , role = None):
        super().__init__()
        self.value = None
        self.user = user
        self.role = role

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user and self.user != interaction.user :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        if self.role and self.role not in interaction.user.roles :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user and self.user != interaction.user :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        if self.role and self.role not in interaction.user.roles :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()


class Economy(commands.Cog):

    def __init__(self , client):
        self.client = client
        
    async def check_channel_pvc(ctx) ->bool : 
        return client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0  or ctx.channel.id in client.data[ctx.guild.id]['channels'] or client.data[ctx.guild.id]['pvc_channel'] == ctx.channel.id
    
#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                            AUTOCOINS     

    message_cooldown = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.user)    
    @commands.Cog.listener()
    async def on_message(self , message):
      try :    
        if self.client.data[message.guild.id]['am_channels'] is None or len(self.client.data[message.guild.id]['am_channels']) == 0  or message.channel.id in self.client.data[message.guild.id]['am_channels'] :
            if message.author.bot:
                return

            bucket = self.message_cooldown.get_bucket(message)
            retry_after = bucket.update_rate_limit()

            if not retry_after:
                x =  await self.client.db.execute('UPDATE users SET cash = cash + $1 , pvc = pvc + $2 WHERE id = $3 AND guild_id = $4' , random.randint(0, self.client.data[message.guild.id]['am_cash']) , random.randint(0, self.client.data[message.guild.id]['am_pvc']) , message.author.id , message.guild.id) 
                if "0" in x :
                    await open_account( message.guild.id , message.author.id)
      except :
            pass

#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                              BALANCE

 
    @commands.hybrid_command(aliases=["report"])
    @commands.guild_only()
    # @commands.check(check_channel_pvc)
    @cooldown(1, 5, BucketType.user)
    async def bug(self, ctx, message :str , screenshot : discord.Attachment):
        user  = client.get_user(591011843552837655)
        embed = bembed(message)
        embed.set_image(url = screenshot.url)
        await user.send( embed = embed )
        await ctx.send(embed = bembed("Done , Thanks for Report , we will Fix it Soon !"))

         
   
    @commands.hybrid_command(aliases=["bal"])
    @commands.guild_only()
    @commands.check(check_channel_pvc)
    @cooldown(1, 5, BucketType.user)
    async def balance(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        if bal is None:
                await open_account(ctx.guild.id , user.id)
                bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        rank = await self.client.db.fetchval("SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (cash + bank) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2" , ctx.guild.id ,  user.id)
        embed = discord.Embed(
                timestamp=ctx.message.created_at,
                title=f"{user.name}'s Balance",
                color= 0xF7C906 )
        embed.description =f"[Leaderboard Rank: #{rank}](https://tickap.com/user/{user.id})"       
        embed.add_field(
                name="Cash",
                value=f"{coin(ctx.guild.id)} {bal['cash']:,}", )
        embed.add_field(
                name="Bank",
                value=f"{coin(ctx.guild.id)} {bal['bank']:,}", )
        if client.data[ctx.guild.id]['pvc'] :
            if client.data[ctx.guild.id]['pvc_channel'] == ctx.channel.id and ( client.data[ctx.guild.id]['channels'] != None and ctx.channel.id not in client.data[ctx.guild.id]['channels'] ):
                embed.clear_fields()
                embed.description = ''
            embed.add_field(
                    name= pvc_coin(ctx.guild.id)[1] ,
                    value=f"{pvc_coin(ctx.guild.id)[0]} {bal['pvc']:,}",)     
        if ctx.author != user :
            embed.set_footer(
                    text=f"Requested By: {ctx.author.name} | use /bug to report a bug", icon_url=f"{ctx.author.display_avatar.url}") 
        else :
            embed.set_footer(
                    text=f"Use /bug to report a bug") 


        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/1023642824551444694/1144091334760730704/20230824_052021.jpg")
        await ctx.send( embed=embed) 
        
    @commands.hybrid_command(aliases=["up"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 5, BucketType.user)
    async def userprofile(self,ctx,user:typing.Optional[discord.Member]=None):
        user = user or ctx.author
        embed = discord.Embed(color=0x00000 , description = user.mention, timestamp = datetime.now())
        embed.set_author(name = user, icon_url = user.display_avatar)
        embed.add_field(name = "User ID", value = int(user.id))
        embed.add_field(name = "Joined Discord", value = f"<t:{int(user.created_at.timestamp())}:F>\n<t:{int(user.created_at.timestamp())}:R>", inline = False)
        embed.add_field(name = "Joined Server", value = f"<t:{int(user.joined_at.timestamp())}:F>\n<t:{int(user.joined_at.timestamp())}:R>", inline = False)
        embed.add_field(name = "Highest Role", value = (user.top_role).mention, inline = False)
        embed.set_thumbnail(url = user.display_avatar)
        await ctx.send(embed=embed) 
          
#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                              WITHDRAW

    @commands.hybrid_command(aliases=["with"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 5, BucketType.user)
    async def withdraw(self, ctx, amount: amountconverter ):
        user = ctx.author
        ecoembed = discord.Embed(color= 0xF90651 )
        ecoembed.set_author(name = user , icon_url= user.display_avatar.url)
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        if bal is None:
                await open_account( ctx.guild.id , user.id)
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = int(bal["bank"] ) 
            elif amount == "half":
                amount = int(0.5 * bal["bank"])
        if amount > bal['bank']:
            ecoembed.description='You do not have enough money to withdraw that much'
            await ctx.send (embed = ecoembed)
        elif amount < 0:
            ecoembed.description='You cannot withdraw 0 or less'
            await ctx.send (embed = ecoembed)
        else:
            # await coll.update_one({"id": user.id}, {"$inc": {"cash": +amount, "bank": -amount}})
            await client.db.execute("UPDATE users SET cash = cash + $1 , bank = bank - $1 WHERE id = $2 AND guild_id = $3" , amount , ctx.author.id , ctx.guild.id )
            ecoembed.description = f':white_check_mark: Withdrew {coin(ctx.guild.id)} {amount:,} from your bank !'
            await ctx.send (embed = ecoembed)
            
#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                              DEPOSIT

    @commands.hybrid_command(aliases=["dep"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(3, 3, BucketType.user)
    async def deposit(self, ctx, amount:  amountconverter ):
        user = ctx.author
        ecoembed = discord.Embed(color= 0x08FC08)
        ecoembed.set_author(name = user , icon_url= user.display_avatar.url)
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        if bal is None:
                await open_account( ctx.guild.id , user.id)
                bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        if amount == "all":
            amount = int(bal["cash"])
            await client.db.execute("UPDATE users SET cash = cash - $1 , bank = bank + $1 WHERE id = $2 AND guild_id = $3" , amount , ctx.author.id , ctx.guild.id )
            ecoembed.description = f':white_check_mark: deposit {coin(ctx.guild.id)} {amount:,} to your bank !'
            await ctx.send (embed = ecoembed)
            return
        else:    
          try:
               amount = int(amount)
          except ValueError:
            if amount == "half":
                amount = int(0.5 * bal["cash"])   

        if 0 <= amount <= bal['cash']  :
            await client.db.execute("UPDATE users SET cash = cash - $1 , bank = bank + $1 WHERE id = $2 AND guild_id = $3" , amount , ctx.author.id , ctx.guild.id )
            ecoembed.description = f':white_check_mark: deposit {coin(ctx.guild.id)} {amount:,} to your bank !'
            await ctx.send (embed = ecoembed)             
        elif amount > bal['cash']:
            ecoembed.description='You do not have enough money to deposit that much'
            await ctx.send (embed = ecoembed)
        elif amount < 0:
            ecoembed.description='You cannot ds 0 or less'
            await ctx.send (embed = ecoembed)

# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               WORK COMMAND 

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_channel)
    @commands.cooldown(1 , 600 ,BucketType.member )
    # @commands.dynamic_cooldown( cooldown_funtion , type = BucketType.member)
    async def work(self , ctx):
        ecoembed = discord.Embed(color=  0x08FC08)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        work_amount = 15000
        amount = (random.randint(0, work_amount))    
        x =  await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , amount  , ctx.author.id , ctx.guild.id) 
        if "0" in x :
            await open_account( ctx.guild.id , ctx.author.id)
            await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , amount  , ctx.author.id , ctx.guild.id) 
        ecoembed.description = f"good work , you get {coin(ctx.guild.id)} **{amount:,}** cash"  
        await ctx.send(embed = ecoembed)  

    @work.error
    @commands.guild_only()
    @commands.check(check_channel)
    async def work_error(self,ctx , error):
        ecoembed = discord.Embed(color= 0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        if isinstance(error, commands.CommandOnCooldown):
            sec = int(error.retry_after)
            min , sec = divmod(sec, 60)
            ecoembed.description = f"⌚ | why to much work rest for {min}min {sec}seconds."
            await ctx.send (embed = ecoembed)
            return    
        else :
            await ctx.send(error)

# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               crime COMMAND 
                    
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 600, BucketType.member)
    async def crime(self , ctx):
        ecoembed = discord.Embed()
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        work_amount = 15000   
        amount = (random.randint(-int(work_amount/2) , work_amount))    
        x =  await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , amount  , ctx.author.id , ctx.guild.id) 
        if "0" in x :
            await open_account( ctx.guild.id , ctx.author.id)
            await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , amount  , ctx.author.id , ctx.guild.id) 
        
        crime_win = [ f"you beat a server admin and find {coin(ctx.guild.id)} **{amount:,}** cash"  ,
        f"you triggered a mod successfully and found {coin(ctx.guild.id)} **{amount:,}** cash" ,
         f"you hacked casino bot and added {coin(ctx.guild.id)} **{amount:,}** cash to your account" ,
         f"you won the server e-lafda , congo {coin(ctx.guild.id)} **{amount:,}**",
         f"you won spammer of the day contest  and found {coin(ctx.guild.id)} **{amount:,}** cash" ,
         f"bata nhi sakta kya kand kiya h tune uff , {coin(ctx.guild.id)} **{amount:,}**"]

        crime_lose =  [  f"you got caught while hacking casino bot and lost {coin(ctx.guild.id)} **{amount:,}** your cash" ,
                    f"you became a pervert and lost {coin(ctx.guild.id)} **{amount:,}** cash" ,
                    f"you lost spammer of the day contest  and lost {coin(ctx.guild.id)} **{amount:,}** cash", 
                    f"you have been caught and lost {coin(ctx.guild.id)} **{amount:,}** cash",
                     ]
        if amount > 0 :
            ecoembed.description =  random.choice(crime_win)
            ecoembed.color = discord.Color.green()
        else :
            ecoembed.description =  random.choice(crime_lose)
            ecoembed.color = discord.Color.red()
        await ctx.send(embed = ecoembed)

    @crime.error
    @commands.guild_only()
    @commands.check(check_channel)
    async def crime_error(self,ctx , error):
        ecoembed = discord.Embed(color= 0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        if isinstance(error, commands.CommandOnCooldown):
            sec = int(error.retry_after)
            min , sec = divmod(sec, 60)
            ecoembed.description = f"⌚ | why to much crimes rest for {min}min {sec}seconds."
            await ctx.send (embed = ecoembed)
            return  


# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                            ROB COMMAND 

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 600 , BucketType.user)
    async def rob(self, ctx, user:   discord.Member):
        ecoembed = discord.Embed(color= 0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        if user.id == ctx.author.id:
            await ctx.send('Trying to rob yourself?')
            ctx.command.reset_cooldown(ctx)
            return
        # elif user is client.user:
        #     await ctx.send('Trying to rob ME?')     
        #     ctx.command.reset_cooldown(ctx)
        #     return
        else:
            user_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
            member_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
            if user_bal is None:
                await open_account( ctx.guild.id , user.id)
                user_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
            if member_bal is None:
                await open_account( ctx.guild.id , ctx.author.id)
                member_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
    
            mem_total = member_bal["bank"] + member_bal["cash"]
            user_cash = user_bal["cash"]

            rob_amount = 0.8
            if mem_total < 5000:
                if user_cash < 1000:
                    await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , int(mem_total * rob_amount)  , ctx.author.id , ctx.guild.id) 
                    ecoembed.description = f"❎ | You've been fined {coin(ctx.guild.id)} {int(mem_total * rob_amount) : ,} for trying to rob a poor person."
                    await ctx.send(embed = ecoembed)
                else :
                    await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , int(user_cash * rob_amount)  , ctx.author.id , ctx.guild.id) 
                    await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , int(user_cash * rob_amount)  , user.id , ctx.guild.id) 
                    ecoembed.description = f"✅ | You robbed {coin(ctx.guild.id)} {(int(user_cash * rob_amount)): ,} from {user}."
                    ecoembed.color = 0x08FC08
                    await ctx.send (embed = ecoembed)    
            elif mem_total >= 5000 and mem_total <= 10000 :
                x = random.randint(1, 2 )
                if x==1:
                    if user_cash < 1000:
                        await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , (int(mem_total *  rob_amount))  , ctx.author.id , ctx.guild.id) 
                        ecoembed.description = f"❎ | You've been fined {coin(ctx.guild.id)} {(int(mem_total * rob_amount)): ,} for trying to rob a poor person."
                        await ctx.send(embed = ecoembed)
                    else:
                        await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , int(user_cash * rob_amount)  , ctx.author.id , ctx.guild.id) 
                        await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , int(user_cash * rob_amount)  , user.id , ctx.guild.id) 
                        ecoembed.description = f"✅ | You robbed {coin(ctx.guild.id)} {(int(user_cash * rob_amount)): ,} from {user}."
                        ecoembed.color = 0x08FC08
                        await ctx.send (embed = ecoembed)  
                else :
                    await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , (int(mem_total *  rob_amount))  , ctx.author.id , ctx.guild.id) 
                    ecoembed.description = f"❎ | You've been fined {coin(ctx.guild.id)} {(int(mem_total * rob_amount)): ,} **better luck next time.**"
                    await ctx.send (embed = ecoembed)
            elif mem_total > 10000:
                await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , (int(mem_total *  rob_amount))  , ctx.author.id , ctx.guild.id) 
                ecoembed.description = f"❎ | You've been fined {coin(ctx.guild.id)} {(int(mem_total * rob_amount)): ,} Rich people dont rob."
                await ctx.send(embed = ecoembed)
  
    
    @rob.error
    @commands.guild_only()
    @commands.check(check_channel)
    async def rob_error(self,ctx , error):
        if isinstance(error, commands.CommandOnCooldown):
            ecoembed = discord.Embed(color= 0xF90651)
            ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
            sec = int(error.retry_after)
            min , sec = divmod(sec, 60)
            ecoembed.description = f":watch: | You cannot attempt to rob another member for {min}min {sec}seconds."
            await ctx.send (embed = ecoembed)
            return
        if isinstance(error, commands.MemberNotFound): 
            ctx.command.reset_cooldown(ctx)
            await ctx.send(embed = discord.Embed( description= "cant find user !!!"))
            return      
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(embed = discord.Embed( description= "Not enough arguments passed !!!"))
            ctx.command.reset_cooldown(ctx)
            return      
#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                            Give Command

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 2, BucketType.user)
    async def give(self, ctx, user: discord.Member , amount:  amountconverter ):
        ecoembed = discord.Embed(color=  0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        member_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
        
        if member_bal is None:
                await open_account(ctx.guild.id , ctx.author.id)
                member_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
        
        mem_cash = member_bal["cash"]
        
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = mem_cash
            elif amount == "half":
                amount = int(0.5 * mem_cash)       
        if amount > mem_cash:
            ecoembed.description = 'You do not have enough money to send that much'
            await ctx.send (embed = ecoembed)
        elif amount <= 0:
            ecoembed.description = 'You cannot send 0 or less'
            await ctx.send (embed = ecoembed)
        else:
            
            await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , amount , ctx.author.id , ctx.guild.id) 
            x = await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , amount , user.id , ctx.guild.id) 
            if "0" in x :
                await open_account(ctx.guild.id , user.id)
                await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , amount , user.id , ctx.guild.id) 
            
            ecoembed.description = f'You have sent {coin(ctx.guild.id)} {amount :,} to {user}'
            ecoembed.color = 0x08FC08
            await ctx.send (embed = ecoembed)

#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                            RESET PAODS

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(3,300 , BucketType.user)
    async def resetmoney(self , ctx , user : discord.Member = None):
        
        if user and check_perms(ctx) :
            view = Confirm(ctx.author)
            await ctx.send(embed = bembed(f"Do You Want Reset {user}'s Money ?") , view = view )
            await view.wait()
            if view.value :
                await self.client.db.execute('UPDATE users SET cash = 0 , bank = 0 WHERE id = $1 AND guild_id = $2'  , user.id , ctx.guild.id) 
                await ctx.send( embed = bembed(f"{user.name}'s Economy Reset "))
    
        else :    
            view = Confirm(ctx.author)
            await ctx.send(embed = bembed("Are You Sure ?") , view = view )
            await view.wait()
            if view.value :
                await self.client.db.execute('UPDATE users SET cash = 0 , bank = 0 WHERE id = $1 AND guild_id = $2'  , ctx.author.id , ctx.guild.id) 
                await ctx.send( embed = bembed(f"{ctx.author.name}'s Economy Reset "))
    @resetmoney.error
    async def er(self , ctx , error ):
        await ctx.send(error)   
            
#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                                 LB

    @commands.hybrid_command(aliases=["lb"])
    @commands.guild_only()
    @commands.check(check_channel_pvc)
    @cooldown(3, 60, BucketType.user)
    async def leaderboard(self , ctx ,page: typing.Optional[int] = 1, type1 : str = "bank" ):
      i=0

      view = None 
      if client.data[ctx.guild.id]['pvc_channel'] == ctx.channel.id and ( client.data[ctx.guild.id]['channels'] != None and ctx.channel.id not in client.data[ctx.guild.id]['channels'] ):
        type1 = 'pvc'
 
      if  type1 == "bank" or type1 == "-bank":
        docs = await client.db.fetch("SELECT id , bank FROM users WHERE guild_id = $1 ORDER BY bank DESC" , ctx.guild.id)
        type2 = "bank"
        rank = await self.client.db.fetchval("SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (bank) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2" , ctx.guild.id ,  ctx.author.id)
      
      elif type1 == "cash" or type1 == "-cash":
        docs = await client.db.fetch("SELECT id , cash FROM users WHERE guild_id = $1 ORDER BY cash DESC" , ctx.guild.id)
        type2 = "cash"
        rank = await self.client.db.fetchval("SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (cash) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2" , ctx.guild.id ,  ctx.author.id)
      
    #   elif type1 == "pvc" or type1 == client.data[ctx.guild.id]['pvc_name'].lower() :
      elif type1 == "pvc"  :
        docs = await client.db.fetch("SELECT id , pvc FROM users WHERE guild_id = $1 ORDER BY pvc DESC" , ctx.guild.id)
        type2 = "pvc"
        rank = await self.client.db.fetchval("SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (pvc) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2" , ctx.guild.id ,  ctx.author.id)



    # view = Lbcash(timeout=240 , page = page , ctx = ctx ) 
    
    #   elif type1 == "share":
    #     lb_data = economy.find({"id" :{ "$gt" : 0 }}).sort("share" , -1)
    #     docs = await lb_data.to_list(length = 500000)
    #     type2 = "share"
        # view = Lbcash(timeout=240 , page = page , ctx = ctx ) 
  
    #   dis =  f"Leaderboard for **{pvc_coin(ctx.guild.id)[1] if type1=='pvc' or type1 == client.data[ctx.guild.id]['pvc_name'].lower()  else type2 }** \n\n"                  
      dis =  f"Leaderboard for **{pvc_coin(ctx.guild.id)[1] if type1=='pvc' else type2 }** \n\n"                  
      for x in docs:
            amount = int(x[type2])
            user = ctx.guild.get_member(x['id'])
            if user is None :
                 continue 
            else :
                i = i+1    
            if i == page*10 + 1:
                break
            if i <= (page-1)*10:
                continue
            # v = f"**{i}**. [{user}](https://tickap.com/user/{user.id}) **:** {pvc_coin(ctx.guild.id)[0] if type1 == 'pvc' or type1 == client.data[ctx.guild.id]['pvc_name'].lower() else coin(ctx.guild.id) } {amount:,}\n"
            v = f"**{i}**. [{user}](https://tickap.com/user/{user.id}) **:** {pvc_coin(ctx.guild.id)[0] if type1 == 'pvc' else coin(ctx.guild.id) } {amount:,}\n"
            dis = dis + v
      embed = discord.Embed(description=dis, color=discord.Colour.blue())
      embed.set_author(name=f"{ctx.guild.name} Leaderboard" , icon_url= ctx.guild.icon) 
      embed.set_footer(
                text=f"Page {page} , Your leaderboard rank: {rank}")
      await ctx.send(embed=embed , view = view)
    
    # @leaderboard.error
    # async def er(self , ctx , error ):
    #     await ctx.send(error)
    
# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                            COINflip COMMAND 

    @commands.hybrid_command(aliases=["cf"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(2, 60, BucketType.user)
    async def flip(self , ctx , amount : amountconverter  ,  side : typing.Literal[ 'head', 'tail' , 'h','t','H','T' ] = "head"): 
        user = ctx.author
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = bal["cash"]
                if amount > 75000:
                    amount=75000  
            elif amount == "half":
                amount = int(0.5 * bal["cash"])
                if amount > 75000:
                    amount=75000        
        if bal is None:
                await open_account( ctx.guild.id , user.id)
                bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        if amount > bal['cash']:
                await ctx.send('You do not have enough money to coinflip that much')
        elif amount <= 0 or amount > 75000:
                await ctx.send('You cannot flip 0 , less or more then 50000') 
        else:   
                await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , amount , ctx.author.id , ctx.guild.id) 
                coin_flip = 0.5
                x = random.choices([1,2] , weights = [coin_flip ,(1- coin_flip)])[0]  
                msg = await ctx.send(f"**{ctx.author.mention}** spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe coin flips... <a:coinflip:1007007819490406573>")
                await asyncio.sleep(random.randint(1,4))
                if x == 1:
                  await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , 2*amount , ctx.author.id , ctx.guild.id) 
                  await msg.edit(content= f'**{ctx.author.mention}** spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe coin flips... {coin(ctx.guild.id)} and you Won {coin(ctx.guild.id)} **{amount*2:,}** ')
                else: 
                  await msg.edit(content=f'**{ctx.author.mention}** spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe coin flips... {coin(ctx.guild.id)} and you lost it all... :c ')    
           
    @flip.error
    @commands.guild_only()
    @commands.check(check_channel)
    async def flip_error(self,ctx , error):
        ecoembed = discord.Embed(color= 0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        if isinstance(error, commands.CommandOnCooldown):
            sec = int(error.retry_after)
            min , sec = divmod(sec, 60)
            ecoembed.description = f"⌚ | You cannot flip coin for {min}min {sec}seconds."
            await ctx.send (embed = ecoembed)
            return

#------------------------------------------------xxx---------------------------------------------------------------------------------------------------------------------
#                                            sloth Command


    @commands.hybrid_command(aliases=["st"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 3, BucketType.user)
    async def slot( self , ctx , amount : amountconverter ):
        ecoembed = discord.Embed(color=  0x08FC08)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        all = ctx.guild.emojis
        if len(all) < 3 :
            all =  [  *all ,  "😉" , "🙂" , "😐" ]
        emoji = random.choices(all , k=3)        
        first = random.choice(emoji)
        second = random.choice(emoji)
        third = random.choice(emoji)
        outupt = f"{first} | {second} | {third}"
        
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
        
        st_amount = 50000
        
        if bal is None:
            await open_account( ctx.guild.id ,ctx.author.id)
            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
        try:
            amount = int(amount)    
        except ValueError:
            if amount == "all":
                amount = bal["cash"]
                if amount > st_amount:
                    amount=st_amount
            elif amount == "half":
                amount = int(0.5 * bal["cash"])
                if amount > st_amount:
                    amount=st_amount          
        if amount > bal['cash']:
                await ctx.send('You do not have enough money to slots that much')
        elif amount <= 0 or amount > st_amount:
                await ctx.send(f'You cannot slot 0 , less or more then {st_amount}') 
        else :
                if first == second == third:
                    ecoembed.description=f"you won {coin(ctx.guild.id)} {2*amount}\n\n{outupt}" 
                    await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , amount , ctx.author.id , ctx.guild.id) 
                    await ctx.send(embed=ecoembed)
                elif first == second or second  == third:
                    ecoembed.description=f"you won {coin(ctx.guild.id)} {int(1.7*amount)} \n\n{outupt}"
                    await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , (int(0.7*amount)) , ctx.author.id , ctx.guild.id) 
                    await ctx.send(embed=ecoembed)
                else:
                    ecoembed.description=f"you lost {coin(ctx.guild.id)} {amount}\n\n{outupt}" 
                    await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , amount , ctx.author.id , ctx.guild.id) 
                    ecoembed.color =  discord.Color.red()
                    await ctx.send(embed=ecoembed)
                     


#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               roll

    @commands.command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(2, 5, BucketType.user)
    async def roll(self , ctx ,amount : amountconverter ,  rang:typing.Literal["odd" , "even" , 1 , 2 , 3 ,4, 5, 6] = "even"):
        ecoembed = discord.Embed(color= discord.Color.green())
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        user = ctx.author
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = bal["cash"]
                if amount > 50000:
                    amount=50000  
            elif amount == "half":
                amount = int(0.5 * bal["cash"])
                if amount > 50000:
                    amount=50000     
        if bal is None:
                await open_account( ctx.guild.id , user.id)
                bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        if amount > bal['cash']:
                await ctx.send('You do not have enough money to roll that much')
        elif amount <= 0 or amount > 50000:
                await ctx.send('You cannot roll 0 , less or more then 50000') 
        else:
            x = random.randint(1, 6)
            if rang == "even" and x in [2,4,6]:
                await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You win {coin(ctx.guild.id)} {2 * amount :,}\n:game_die: You rolled **{x}**"
                await ctx.send(embed = ecoembed)
            elif rang == "odd" and x in [1,3,5]:    
                await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You win {coin(ctx.guild.id)} {2 * amount :,}\n:game_die: You rolled **{x}**"
                await ctx.send(embed = ecoembed)
            elif rang in [1,2,3,4,5,6] and x == rang :
                await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , 4*amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You win {coin(ctx.guild.id)} {5 * amount :,}\n:game_die: You rolled **{x}**"
                await ctx.send(embed = ecoembed)
            else:
                await self.client.db.execute('UPDATE users SET cash = cash - $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You lose {coin(ctx.guild.id)}{amount: ,}\n:game_die: You rolled **{x}**"
                ecoembed.color = discord.Color.red()
                await ctx.send(embed = ecoembed)


async def setup(client):
   await client.add_cog(Economy(client))                       