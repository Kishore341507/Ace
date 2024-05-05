from http import client
import discord
from discord.ext import commands 
from database import *
from discord.ui import Button, View
from discord.ext.commands import BucketType, cooldown
import random
import typing
from datetime import datetime
from comp.ui import *
import math


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
        self.message_cooldown = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.member)
        
    async def check_channel_pvc(ctx) ->bool : 
        return client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0  or ctx.channel.id in client.data[ctx.guild.id]['channels'] or client.data[ctx.guild.id]['pvc_channel'] == ctx.channel.id
    
    #used in Work , Crime and Rob command
    
    def cooldown_funtion(ctx):
        if client.data[ctx.guild.id]['economy'] :
            return commands.Cooldown(1, client.data[ctx.guild.id]['economy'][str(ctx.command.name)]['cooldown'])
        else :
            return commands.Cooldown(1, defult_economy[str(ctx.command.name)]['cooldown'])
    
#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                            AUTOCOINS     


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
    async def bug(self, ctx, screenshot: typing.Optional[discord.Attachment] = None, *, message):
        channel  = client.get_channel(1209630599472750622)
        invite = ctx.guild.vanity_url or (await ctx.guild.invites())[0] if ctx.guild.me.guild_permissions.manage_guild and await ctx.guild.invites() else await (ctx.guild.channels[0].create_invite() if ctx.guild.me.guild_permissions.create_instant_invite else '')
        dis = f"Author: [{ctx.author.name}](https://discordapp.com/users/{ctx.author.id})\nServer: [{ctx.guild.name}]({invite or ctx.guild.id})\nMessage: {ctx.message.jump_url}\nReport: {message}"

        embed = bembed(dis, discord.Color.brand_red())
        embed.set_author(name= client.user.name, icon_url= client.user.avatar.url)
        embed.title = ctx.author.name
        if screenshot:
            embed.set_image(url = screenshot.url)
        await channel.send(content=f"**A new bug report for {client.user.name}**", embed = embed )
        await ctx.reply(embed = bembed("Thanks for the report, we will look into it soon and fix it appropriately!"))
         
   
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
            embed.set_footer(text=f"Use /bug to report a bug")
            
        await ctx.send( embed=embed  ) 
        
        
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
        req = await client.http.request(discord.http.Route("GET", "/users/{uid}", uid=user.id))
        banner_id = req["banner"]
        banner_url = ""
        if banner_id:
            banner_url = f"https://cdn.discordapp.com/banners/{user.id}/{banner_id}.gif?size=1024"
        embed.set_image(url=banner_url)
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
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2' , user.id , ctx.guild.id)
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
    @commands.dynamic_cooldown( cooldown_funtion , type = BucketType.member)
    async def work(self , ctx):
        ecoembed = discord.Embed(color=  0x08FC08)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        
        amount = (random.randint( client.data[ctx.guild.id]['economy']['work']['min'] if client.data[ctx.guild.id]['economy'] else defult_economy['work']['min'] , client.data[ctx.guild.id]['economy']['work']['max'] if client.data[ctx.guild.id]['economy'] else defult_economy['work']['max'])) 
           
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
        

# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               crime COMMAND 
                    
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_channel)
    @commands.dynamic_cooldown( cooldown_funtion , type= BucketType.member )
    async def crime(self , ctx):
        ecoembed = discord.Embed()
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        crime_amount = client.data[ctx.guild.id]['economy']['crime']['max'] if client.data[ctx.guild.id]['economy'] else defult_economy['crime']['max']   
        amount = (random.randint(-int(crime_amount/2) , crime_amount))    
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
    @commands.dynamic_cooldown( cooldown_funtion , BucketType.member  )
    async def rob(self, ctx, user:   discord.Member):
        ecoembed = discord.Embed(color= 0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        if user.id == ctx.author.id:
            await ctx.reply(embed=bembed('Trying to rob yourself?', discord.Color.brand_red()))
            ctx.command.reset_cooldown(ctx)
            return
        else:
            user_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
            member_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
            if user_bal is None:
                await open_account( ctx.guild.id , user.id)
                user_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
            if member_bal is None:
                await open_account( ctx.guild.id , ctx.author.id)
                member_bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
            if member_bal['stocks'] > 0:
                embed=bembed('Sorry! You cannot rob someone while owning stocks from the market. Sell them first :c', discord.Color.brand_red())
                embed.set_author(name=ctx.author.display_name, icon_url= ctx.author.display_avatar)
                await ctx.reply(embed=embed)
                ctx.command.reset_cooldown(ctx)
                return
            if member_bal['bank'] < 0 or member_bal['cash'] < 0:
                embed=bembed('Balance in bank and cash should be positive :c', discord.Color.brand_red())
                embed.set_author(name=ctx.author.display_name, icon_url= ctx.author.display_avatar)
                embed.set_footer(text="use resetmoney command to reset your economy")
                await ctx.reply(embed=embed)
                ctx.command.reset_cooldown(ctx)
                return
            mem_total = member_bal["bank"] + member_bal["cash"]
            user_cash = user_bal["cash"]

            rob_amount = client.data[ctx.guild.id]['economy']['rob']['percent'] if client.data[ctx.guild.id]['economy'] else defult_economy['rob']['percent'] 
            if mem_total < 5000:
                if user_cash < 1000:
                    await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , int(abs(mem_total) * rob_amount)  , ctx.author.id , ctx.guild.id) 
                    ecoembed.description = f"❎ | You've been fined {coin(ctx.guild.id)} {int(abs(mem_total) * rob_amount) : ,} for trying to rob a poor person."
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
                        await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , (int(abs(mem_total) *  rob_amount))  , ctx.author.id , ctx.guild.id) 
                        ecoembed.description = f"❎ | You've been fined {coin(ctx.guild.id)} {(int(abs(mem_total) * rob_amount)): ,} for trying to rob a poor person."
                        await ctx.send(embed = ecoembed)
                    else:
                        await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , int(user_cash * rob_amount)  , ctx.author.id , ctx.guild.id) 
                        await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , int(user_cash * rob_amount)  , user.id , ctx.guild.id) 
                        ecoembed.description = f"✅ | You robbed {coin(ctx.guild.id)} {(int(user_cash * rob_amount)): ,} from {user}."
                        ecoembed.color = 0x08FC08
                        await ctx.send (embed = ecoembed)  
                else :
                    await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , (int(abs(mem_total) *  rob_amount))  , ctx.author.id , ctx.guild.id) 
                    ecoembed.description = f"❎ | You've been fined {coin(ctx.guild.id)} {(int(abs(mem_total) * rob_amount)): ,} **better luck next time.**"
                    await ctx.send (embed = ecoembed)
            elif mem_total > 10000:
                await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , (int(abs(mem_total) *  rob_amount))  , ctx.author.id , ctx.guild.id) 
                ecoembed.description = f"❎ | You've been fined {coin(ctx.guild.id)} {(int(abs(mem_total) * rob_amount)): ,} Rich people dont rob."
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
                await self.client.db.execute('UPDATE users SET cash = 0 , bank = 0, stocks = 0 WHERE id = $1 AND guild_id = $2'  , user.id , ctx.guild.id) 
                await ctx.send( embed = bembed(f"{user.name}'s Economy Reset "))
    
        else :    
            view = Confirm(ctx.author)
            await ctx.send(embed = bembed("Are You Sure ?") , view = view )
            await view.wait()
            if view.value :
                await self.client.db.execute('UPDATE users SET cash = 0 , bank = 0, stocks = 0 WHERE id = $1 AND guild_id = $2', ctx.author.id , ctx.guild.id) 
                await ctx.send( embed = bembed(f"{ctx.author.name}'s Economy Reset "))
    @resetmoney.error
    async def er(self , ctx , error ):
        await ctx.reply(embed=bembed(error))   
            
#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                                 LB

    async def generate_lb_emb(self, guild , user , page, type):
        last_page = int(math.ceil(int(await client.db.fetchval("SELECT COUNT(*) FROM users WHERE guild_id = $1" , guild.id))/10))
        offset = (page-1)*10
        coin_icon = coin(guild.id)
        
        if type in ["total" ,"-total"]:
            type = "total"
            docs = await client.db.fetch("SELECT id , (bank + cash) AS total FROM users WHERE guild_id = $1 ORDER BY total DESC LIMIT 50 OFFSET $2;" , guild.id , offset)
            rank = await client.db.fetchval("SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (bank + cash) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2" , guild.id , user.id)
            
        
        elif  type in ["bank","-bank"]:
            type = "bank"
            docs = await client.db.fetch("SELECT id , bank FROM users WHERE guild_id = $1 ORDER BY bank DESC LIMIT 50 OFFSET $2;" , guild.id , offset)
            rank = await client.db.fetchval("SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (bank) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2" , guild.id , user.id)
        elif type in ["cash" , "-cash"]:
            type = "cash"
            docs = await client.db.fetch("SELECT id , cash FROM users WHERE guild_id = $1 ORDER BY cash DESC LIMIT 50 OFFSET $2;" , guild.id , offset)
            rank = await client.db.fetchval("SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (cash) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2" , guild.id , user.id)
                
        elif type == "pvc":
            type = "pvc"
            docs = await client.db.fetch("SELECT id , pvc FROM users WHERE guild_id = $1 ORDER BY pvc DESC LIMIT 50 OFFSET $2;" , guild.id , offset)
            rank = await client.db.fetchval("SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (pvc) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2" , guild.id , user.id)
            coin_icon = pvc_coin(guild.id)[0]
            
        elif type in ["market", "-market", "shares", "-shares", "stocks", "-stocks"] and client.data[guild.id]['market'] and client.data[guild.id]['market']['status']:
            type = "stocks"
            docs = await client.db.fetch("SELECT id , stocks FROM users WHERE guild_id = $1 ORDER BY stocks DESC LIMIT 50 OFFSET $2;" , guild.id , offset)
            rank = await client.db.fetchval("SELECT position FROM (SELECT id, ROW_NUMBER() OVER (ORDER BY (stocks) DESC) AS position FROM users WHERE guild_id = $1 ) ranked WHERE id = $2" , guild.id , user.id)
            coin_icon = "📈"
            
        dis =  ""   
        temp = offset
        for x in docs:
            amount = x[type]
            user = guild.get_member(x['id'])
            if user is None:
                continue
            else :
                offset = offset+1   
            v = f"**{offset}**. [{user}](https://tickap.com/user/{user.id}) **:** {coin_icon} {amount:,}\n"
            dis = dis + v
            if offset - temp == 10:
                break

        embed = discord.Embed(description=dis, color=discord.Colour.blue())
        title = f"{guild.name}'s Leaderboard" if type == "total" else f"{guild.name}'s Leaderboard for {type}"
        embed.set_author(name=f"{title}", icon_url= guild.icon) 
        embed.set_footer(
                      text=f"Page {page}/{last_page} , Your leaderboard rank: {rank}")
        return embed, last_page
    
    class leaderboardPanelView(View):
        def __init__(self, user,message , page, last_page, type):
            super().__init__(timeout=180)
            self.user = user
            self.message = message
            self.current_page = page
            self.last_page = last_page
            self.type = type
        
            previous_pg_button = Button(label="Previous Page", style=discord.ButtonStyle.blurple, disabled=True if self.current_page <= 1 else False)
            previous_pg_button.callback = self.lb_backwards_button
            self.add_item(previous_pg_button)
            
            next_pg_button = Button(label="Next Page", style=discord.ButtonStyle.blurple, disabled=True if self.current_page >= self.last_page else False)
            next_pg_button.callback = self.lb_forwards_button
            self.add_item(next_pg_button)
            
            if random.randint(1,3) == 2 :
                self.add_item(Button(label= client.user.name ,
                                        style=discord.ButtonStyle.url,
                                        url="https://discord.com/api/oauth2/authorize?client_id=1165310965710082099&permissions=288706064&scope=bot+applications.commands"))

        async def interaction_check(self, interaction: discord.Interaction):
            if self.message is None:
                self.message = interaction.message
            
            if interaction.user == self.user:
                return True
            else:
                await interaction.response.send_message( embed = discord.Embed(description="This is not your panel. You need to run the command yourself.", color=0x2b2c31), ephemeral=True)
                return False

        async def on_timeout(self):
            if self.message is not None:
                for item in self.children:
                    item.disabled = True
                await self.message.edit(content="**This message is now inactive.**", view=self)

        async def lb_backwards_button(self,interaction: discord.Interaction):
            
            self.current_page -= 1

            if self.current_page <= 1:
                for item in self.children:
                    if item.label == "Previous Page":
                        item.disabled = True
                
            if self.current_page < self.last_page:
                for item in self.children:
                    if item.label == "Next Page":
                        item.disabled = False
            
            embed, last_page = await Economy.generate_lb_emb(self, interaction.guild , interaction.user , self.current_page, self.type)
            await interaction.response.edit_message(embed=embed, view=self)

        async def lb_forwards_button(self,interaction: discord.Interaction):          
            
            self.current_page += 1

            if self.current_page > 1:
                for item in self.children:
                    if item.label == "Previous Page":
                        item.disabled = False
                
            if self.current_page >= self.last_page:
                for item in self.children:
                    if item.label == "Next Page":
                        item.disabled = True
            
            embed, last_page = await Economy.generate_lb_emb(self,interaction.guild , interaction.user , self.current_page, self.type)
            await interaction.response.edit_message(embed=embed, view=self)

    
    @commands.hybrid_command(aliases=["lb"])
    @commands.guild_only()
    @commands.check(check_channel_pvc)
    @cooldown(3, 60, BucketType.user)
    async def leaderboard(self , ctx ,page: typing.Optional[int] = 1, type : str = "total" ):
        if self.client.data[ctx.guild.id]['pvc_channel'] == ctx.channel.id and ( self.client.data[ctx.guild.id]['channels'] != None and ctx.channel.id not in self.client.data[ctx.guild.id]['channels'] ):
            type = 'pvc'
      
        embed, last_page = await self.generate_lb_emb(ctx.guild , ctx.author, page, type)
        if not embed.description:
            page = last_page
            embed, last_page = await self.generate_lb_emb(ctx.guild , ctx.author, page, type)
        view = self.leaderboardPanelView(ctx.author,None, page, last_page, type)
        message = await ctx.send("Lb may not work till Intent not verifyed , will fix soon" , embed=embed , view = view)
        view.message = message

async def setup(client):
   await client.add_cog(Economy(client))                       