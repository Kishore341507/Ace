import discord
from discord.ext import commands
from database import *
import asyncio 
from discord.ext.commands import BucketType, cooldown
import random
from discord.ui import Button , View
import time


class MyView(View):
    
    def __init__(self , amount , timeout , author , ctx):
        super().__init__(timeout = timeout)
        self.amount = amount
        self.author = author
        self.ctx = ctx
        self.player = [author]
        self.started = False
        # self.economy = db[f"{self.ctx.guild.id}"]


    async def start(self):
        # economy = self.economy
        self.started = True
        self.player.append(self.author)
        ecoembed = discord.Embed()
        ecoembed.description = "***The Russian Roulette game has begun!***"
        await self.ctx.send(embed=ecoembed)
        x = random.randrange(((len(self.player))-1))
        y = iter(self.player)
        for i in range((len(self.player)-1)):
                    await asyncio.sleep(2)
                    if i == x :
                        item = next(y) 
                        ecoembed.description = f"**{item}** pulls the trigger... and gets hit 🪦"
                        ecoembed.color = discord.Color.red()
                        await self.ctx.send(embed=ecoembed)
                        self.player.pop()
                        self.player.remove(item)
                        text = f"**__Russian Roulette Survivors__**\n"
                        if (len(self.player)) == 0:
                            self.player.append(self.author)
                            await client.db.execute("UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3", self.amount, self.ctx.author.id, self.ctx.guild.id)
                        for i in self.player:
                            await client.db.execute("UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3", (self.amount + (int((self.amount)/(len(self.player))))) , i.id , self.ctx.guild.id)
                            text = text + f"{i.mention} win {(int((self.amount)/(len(self.player))))}\n"
                        await self.ctx.send(text)
                        self.ctx.command.reset_cooldown(self.ctx)
                        break
                    else :
                        item = next(y)
                        ecoembed.description = f"**{item}** pulls the trigger... and survives!"
                        ecoembed.color = discord.Color.green()
                        await self.ctx.send(embed=ecoembed)
    
    @discord.ui.button(label = "Join" , style=discord.ButtonStyle.green )
    async def button1(self ,interaction ,  button ):
        ecoembed = discord.Embed(color= None)
        amount = self.amount
        author = self.author
        player = self.player
        # economy = self.economy
        
        bal2 = await client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', interaction.user.id, interaction.guild.id)
        if bal2 is None:
            await interaction.response.edit_message("ok")
        elif interaction.user == author:
            await interaction.response.send_message("you cant !!" , ephemeral=True)
        elif interaction.user in player:
                self.player.remove(interaction.user)
                await client.db.execute("UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3", amount, interaction.user.id, interaction.guild.id)
                button.label = f"join {len(player)}"
                await interaction.response.edit_message(view=self)
        elif bal2["cash"] >= amount:
            if len(player) < 4 :
                await client.db.execute("UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3", amount, interaction.user.id, interaction.guild.id)
                player.append(interaction.user)
                button.label = f"join {len(player)}"
                await interaction.response.edit_message(view=self)                
            else :
                await interaction.response.edit_message(view = None)
                await client.db.execute("UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3", amount, interaction.user.id, interaction.guild.id)
                player.append(interaction.user) 
                await self.start()
                
        else :
            await interaction.response.send_message("you dont have enough money !!" , ephemeral=True)
    

    @discord.ui.button(label = "Start" , style=discord.ButtonStyle.red )
    async def button2s(self ,interaction ,  button ):
        amount = self.amount
        author = self.author
        player = self.player
        # economy = self.economy
        if interaction.user == self.author and len(player) >= 2:
            await interaction.response.edit_message(view = None)
            await self.start()
        elif interaction.user == self.author and len(player)==1:
            await interaction.response.edit_message(view = None)
            
            await client.db.execute("UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3", amount, interaction.user.id, interaction.guild.id)
            # await economy.update_one({"id": interaction.user.id} , {"$inc" : {"cash": +amount}})
            self.ctx.command.reset_cooldown(self.ctx)
            self.started = True


class russian_roulette(commands.Cog):

    def __init__(self , client):
        self.client = client  
        self.msg = None


    @commands.hybrid_command(aliases=["rr"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 120, BucketType.guild)
    async def russianroulette(self , ctx , amount: amountconverter ):
    
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        if bal is None:
            await open_account(ctx.guild.id, ctx.author.id)
            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
            
        _max = client.data[ctx.guild.id]["games"]["russian-roulette"]["max"] if client.data[ctx.guild.id]["games"] else defult_economy["russian-roulette"]["max"]
        _min = client.data[ctx.guild.id]["games"]["russian-roulette"]["min"] if client.data[ctx.guild.id]["games"] else defult_economy["russian-roulette"]["min"]
        
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = bal["cash"]
                if amount > _max:
                    amount=_max  
            elif amount == "half":
                amount = int(0.5 * bal["cash"])
                if amount > _max:
                    amount=_max 
        if amount > bal['cash']:
            await ctx.send('You do not have enough money to rr in you **cash**')
            ctx.command.reset_cooldown(ctx)
        elif amount <= _min:
            await ctx.send(f'You cannot rr {_min} or less')
            ctx.command.reset_cooldown(ctx)   
        else: 
            await client.db.execute("UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3", amount, ctx.author.id, ctx.guild.id) 
            view = MyView(timeout=240 , amount= amount , author = ctx.author , ctx = ctx)
            ecoembed = discord.Embed(description= f'Russian Roulette from **{ctx.author}** , if you want to accept this tap join\n> **{amount}** {coin(ctx.guild.id)} \n> Autostart(ed) <t:{int(time.time() + 120)}:R>', color=  discord.Color.blurple() )
            # ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
            self.msg = await ctx.reply(embed = ecoembed,view = view)
            await asyncio.sleep(120)
            if not view.started:
               await self.msg.edit(view = None)
               await view.start()

    @russianroulette.error
    async def rr_error(self ,ctx ,error):
        if isinstance(error, commands.CommandOnCooldown):
            await self.msg.reply(f"{ctx.author.mention} game is already going , check replyed message")
        else : 
            # await client.application.owner.send(f'{error}')
            ctx.command.reset_cooldown(ctx)
            return

async def setup(client):
   await client.add_cog(russian_roulette(client))    