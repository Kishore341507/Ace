import discord
from discord.ext import commands
import typing
from datetime import datetime , date , time , timedelta
import re
import asyncio
import json
from database import *
from discord.ext.commands import BucketType, cooldown
from itertools import cycle
from utils import  check_channel

class myview(discord.ui.View):

    def __init__(self , timeout , user):
        super().__init__(timeout=timeout)
        self.user = user
        self.player = [ user[0]['user'] , user[1]['user'] ]
        self.choice = [ None , None ]

    async def winners(self ):
        lis = ["🪨" , "📰" , "✂️"]
        if self.choice[0] == self.choice[1]:
            result = f"games is tie , both chose {lis[self.choice[0]]}"
        elif (self.choice[0] == 0 and self.choice[1] == 2 )  or (self.choice[0] == 1 and self.choice[1] == 0 ) or (self.choice[0] == 2 and self.choice[1] == 1 ) :
            result = f"{self.player[0]} select - {lis[self.choice[0]]}\n{self.player[1]} select - {lis[self.choice[1]]}\n\n**{self.player[0]}** wins" 
        else :
            result = f"{self.player[0]} select - {lis[self.choice[0]]}\n{self.player[1]} select - {lis[self.choice[1]]}\n\n**{self.player[1]}** wins"  
        
        for child in self.children:
            child.disabled = True
        self.stop()
        for i in self.user:
            try :
                await i['message'].edit(embed = discord.Embed(description=result) , view = self)
            except :    
                await i['channel'].send(embed = discord.Embed(description=result))   
            if self.user[0]['channel'].id == self.user[0]['channel'].id :
                break  
        
        
    @discord.ui.button(emoji = "🪨"  ,  style=discord.ButtonStyle.red)
    async def stone(self , interaction , button):
        if interaction.user.id == self.player[1].id:
            self.choice[1] = 0
        elif interaction.user.id == self.player[0].id:
            self.choice[0] = 0
            self.user[0]["message"] = interaction.message
        else : 
            await interaction.response.send_message("Not your interaction", ephemeral = True)
            return 
        await interaction.response.send_message("you select 🪨", ephemeral = True)    
        if self.choice[0] is not None and self.choice[1] is not None :
            await self.winners()

            
    @discord.ui.button(emoji = "📰"  , style=discord.ButtonStyle.blurple)
    async def paper(self , interaction , button):
        if interaction.user.id == self.player[1].id:
            self.choice[1] = 1
        elif interaction.user.id == self.player[0].id:
            self.choice[0] = 1
            self.user[0]["message"] = interaction.message
        else :  
            await interaction.response.send_message("Not your interaction", ephemeral = True)
            return 
        await interaction.response.send_message("you select 📰", ephemeral = True)
        if self.choice[0] is not None and self.choice[1] is not None :
            await self.winners()     
    
    
    @discord.ui.button(emoji = "✂️"  , style=discord.ButtonStyle.green)
    async def scissors(self , interaction , button):
        if interaction.user.id == self.player[1].id:
            self.choice[1] = 2
        elif interaction.user.id == self.player[0].id:
            self.choice[0] = 2
            self.user[0]["message"] = interaction.message
        else : 
            await interaction.response.send_message("Not your interaction", ephemeral = True)
            return  
        await interaction.response.send_message("you select ✂️", ephemeral = True )
        if None not in self.choice :
            await self.winners() 

    async def on_error(self, interaction, error, item):
        try:
            await interaction.response.send_message(f"{item}\n{error}")
        except:
               await interaction.followup.send(f"{item}\n{error}")          




class SPC(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.players = []
 
    @commands.hybrid_command()
    @commands.check(check_channel)
    @commands.cooldown(1, 40 , BucketType.user)
    async def spc(self , ctx ):
        if len(self.players) == 0:
            msg = await ctx.reply(embed = discord.Embed(description=f"<a:dcload:1330518199372091473> waiting for other player (exp <t:{int(datetime.now().timestamp()+30)}:R>)"))
            element = {"user" : ctx.author , "channel" : ctx.channel , "message" : msg }
            self.players.append(element)
            await asyncio.sleep(30)
            if element in self.players :
                await msg.edit(embed = discord.Embed(description="No match found"))
                self.players.remove(element)
                return
        else :
            element = self.players[0]
            self.players.remove(element) 
            view = myview(timeout = None , user = [{"user" : ctx.author , "channel" : ctx.channel , "message" : None} , element ] )
            if ctx.channel.id == element['channel'].id :
                await ctx.send( f"{ctx.author.mention} { element['user'].mention}", embed = discord.Embed(description=f"Match started between {ctx.author} and {element['user']} select one") , view = view)
                await element['message'].delete()
                return
        
            await ctx.send( ctx.author.mention , embed = discord.Embed(description=f"Match started between {ctx.author} and {element['user']} select one") , view = view)
            await element["message"].edit( content = element['user'].mention , embed = discord.Embed(description=f"Match started between {ctx.author} and {element['user']} select one") , view = view) 
            return


    @spc.error
    async def error(self , ctx , error):
        if isinstance(error, commands.CommandOnCooldown ):
            await ctx.send(embed = discord.Embed(description= f"You are on cooldown , retry in {int(error.retry_after)}seconds." , delete_after = 3))
        else :
            await ctx.send(error)    
         

async def setup(client):
   await client.add_cog(SPC(client))         
