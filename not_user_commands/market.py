import discord
from discord.ext import commands , tasks
from database import *
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
import math
import typing
from discord.ui import Button , View
from datetime import datetime
from discord import app_commands
import json

import matplotlib.pyplot as plt
import datetime as dt
from matplotlib.dates import DateFormatter, AutoDateFormatter, AutoDateLocator


class Market(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.stock_data = { 966022734398246963 : { 'total_share' : 100000 ,  'data': [] , 'time' : [] } , 457888455700119552: {'total_share' : 100000 ,  'data': [], 'time': []}}
        self.stock_data_update.start()

    async def cog_unload(self):
        self.stock_data_update.cancel()    

    async def check_channel(ctx) ->bool : 
        return ctx.guild.id in self.stock_data and (client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0  or ctx.channel.id in client.data[ctx.guild.id]['channels'])

#market shit

    @tasks.loop( minutes= 30)
    async def stock_data_update(self):
       for i in self.stock_data : 
        guild = client.get_guild(i)
        total_stocks = self.stock_data[guild.id]['total_share']
        total_economy = 0
        sold_stocks = 0
        economy = db[f"{guild.id}"]
        lb_data = economy.find({"id" :{ "$gt" : 0 }}).sort("bank" , -1)
        docs = await lb_data.to_list(length = 500000)
        for x in docs :
            total_economy += x['bank'] + x['cash']
            try : sold_stocks += x['share'] 
            except : pass
        current_stocks = total_stocks - sold_stocks 
        current_rate =  (total_economy/ current_stocks ) * 1/2   
        if len(self.stock_data[guild.id]['data']) >= 96 :
            self.stock_data[guild.id]['data'].pop(0)
            self.stock_data[guild.id]['data'].append(current_rate)
            self.stock_data[guild.id]['time'].pop(0)
            self.stock_data[guild.id]['time'].append(datetime.now().timestamp())
        else :
            self.stock_data[guild.id]['data'].append(current_rate)
            self.stock_data[guild.id]['time'].append(datetime.now().timestamp())


    @commands.hybrid_command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 5, BucketType.user)
    async def market(self , ctx ):
        sold_stocks = 0
        total_economy = 0
        economy = db[f"{ctx.guild.id}"]
        lb_data = economy.find({"id" :{ "$gt" : 0 }}).sort("bank" , -1)
        docs = await lb_data.to_list(length = 500000)
        for x in docs :
            total_economy += x['bank'] + x['cash']
            try : sold_stocks += x['share'] 
            except : pass
        embed = discord.Embed( description= f"1S = {coin1}{(total_economy/(self.stock_data[ctx.guild.id]['total_share'] - sold_stocks)) * 1/2 }")#\nshare - { self.stock_data[ctx.guild.id]['total_share'] - sold_stocks }" )  
        
        self.stock_data[ctx.guild.id]['data'].append( (total_economy/(self.stock_data[ctx.guild.id]['total_share'] - sold_stocks)) * 1/2 )
        self.stock_data[ctx.guild.id]['time'].append(datetime.now().timestamp())
        
        plt.plot([datetime.fromtimestamp(i) for i in self.stock_data[ctx.guild.id]['time']], self.stock_data[ctx.guild.id]['data'])
        plt.ylim( int(min(self.stock_data[ctx.guild.id]['data'])) -1 , int(max(self.stock_data[ctx.guild.id]['data'])) + 2  )
        plt.xlabel('Time')
        plt.ylabel('Value')
        plt.gca().xaxis.set_major_formatter(DateFormatter('%H'))
        plt.gcf().autofmt_xdate()
        plt.savefig("stock_value.png")
        with open("stock_value.png", "rb") as f:
            file = discord.File(f , filename="image.png")
        embed.set_image(url="attachment://image.png")
        plt.clf()
        self.stock_data[ctx.guild.id]['data'].pop()
        self.stock_data[ctx.guild.id]['time'].pop()
        await ctx.send( file = file , embed =embed )    
    
    @market.error
    async def er(self , ctx , error ):
        await ctx.send(error)
            
    # @commands.hybrid_command(aliases=["bs"])
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 10 , BucketType.user)
    # async def buystocks(self , ctx , amount : int ):
    #     total_stocks = self.stock_data[ctx.guild.id]['total_share']
    #     sold_stocks = 0
    #     economy = db[f"{ctx.guild.id}"]
    #     lb_data = economy.find({"id" :{ "$gt" : 0 }}).sort("bank" , -1)
    #     docs = await lb_data.to_list(length = 500000)
    #     total_economy = 0
    #     for x in docs :
    #         total_economy += x['bank'] + x['cash']
    #         try : sold_stocks += x['share'] 
    #         except : pass
    #     current_stocks = total_stocks - sold_stocks    
    #     current_rate =  (total_economy/ current_stocks ) * 1/2   
        
    #     total_cost = 0
    #     number = 0
        
    #     for x in range( current_stocks - 1 , current_stocks - amount -1 , -1 ):
    #         total_cost += current_rate
    #         number += 1
    #         total_economy = total_economy - current_rate
    #         current_rate = ( total_economy - current_rate ) / (x*2)
        
    #     bal = await economy.find_one({"id": ctx.author.id})
    #     if bal is None:
    #             await self.open_account(ctx.guild.id , ctx.author.id)
    #             bal = await economy.find_one({"id": ctx.author.id})
        
    #     if bal['cash'] < 0 :
    #         await ctx.send('Cash must be +ve!')
    #         return
        
    #     elif bal['bank'] < total_cost :
    #         await ctx.send(f"You dont have enough Money , You need {coin1}{total_cost}")
    #         return
        
    #     elif number >= current_stocks -5 or number <= 0  :
    #         await ctx.send(f"You can't buy stockes more than or equal to {current_stocks} or -ve")
    #         return
        
    #     else :
    #         await economy.update_one({"id": ctx.author.id} , { "$inc" : { 'bank' : -int(total_cost) , 'share' : +number  }})
    #         await ctx.send(f"Congratulations, your purchase of **{number}** shares has been successful. The total cost was {coin1}{total_cost} coins.")

    #     # await ctx.send(f"total cost = {total_cost} , number = {number} , current_rate = {current_rate} , current_stock = {current_stocks}")
     
    # @buystocks.error
    # @commands.guild_only()
    # @commands.check(check_channel)
    # async def crime_error(self,ctx , error):
    #     ecoembed = discord.Embed(color= 0xF90651)
    #     ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
    #     if isinstance(error, commands.CommandOnCooldown):
    #         sec = int(error.retry_after)
    #         min , sec = divmod(sec, 60)
    #         ecoembed.description = f"⌚ | try after {min}min {sec}seconds."
    #         await ctx.send (embed = ecoembed)
    #         return    
             
        
    @commands.hybrid_command(aliases=["ss"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 10 , BucketType.user)
    async def sellstocks(self , ctx , amount : int ):
        total_stocks = self.stock_data[ctx.guild.id]['total_share']
        sold_stocks = 0
        economy = db[f"{ctx.guild.id}"]
        lb_data = economy.find({"id" :{ "$gt" : 0 }}).sort("bank" , -1)
        docs = await lb_data.to_list(length = 500000)
        total_economy = 0
        for x in docs :
            total_economy += x['bank'] + x['cash']
            try : sold_stocks += x['share'] 
            except : pass
            
        current_stocks = total_stocks - sold_stocks + amount  
        current_rate =  (total_economy/ current_stocks ) * 1/2   
        
        total_cost = 0
        number = 0
        
        # for x in range(  current_stocks - amount - 1 , current_stocks -1 ):
        #     total_economy = total_economy + current_rate
        #     current_rate = ( total_economy + current_rate ) / (x*2)
        #     total_cost += current_rate
        #     number += 1
        
        for x in range( current_stocks - amount - 1 , current_stocks - 1   ): #current_stocks - amount  , -1 ):
            total_economy = total_economy + current_rate
            current_rate = ( total_economy + current_rate ) / (x*2)
            number += 1
            total_cost += current_rate
        
        bal = await economy.find_one({"id": ctx.author.id})
        if bal is None:
                await self.open_account(ctx.guild.id , ctx.author.id)
                bal = await economy.find_one({"id": ctx.author.id})
        
        try : 
            user_shares = bal['share']
        except :
            await ctx.send('You Have 0 shares In yor Account!')  
            return
            
              
        if bal['cash'] < 0 :
            await ctx.send('Cash must be +ve!')
            return
        
        elif number > user_shares or number <= 0 :
            await ctx.send(f"You can't sell stockes more than or equal to {user_shares} or -ve")
            return
        
        else :
            await economy.update_one({"id": ctx.author.id} , { "$inc" : { 'bank' : + int(total_cost) , 'share' : -number  }})
            await ctx.send(f"Congratulations, your purchase of **{number}** shares has been successful. The total cost was {coin1}{total_cost} coins.")

        # await ctx.send(f"total cost = {total_cost} , number = {number} , current_rate = {current_rate} , current_stock = {current_stocks}")  
    
    
    @sellstocks.error
    @commands.guild_only()
    @commands.check(check_channel)
    async def crime_error(self,ctx , error):
        ecoembed = discord.Embed(color= 0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        if isinstance(error, commands.CommandOnCooldown):
            sec = int(error.retry_after)
            min , sec = divmod(sec, 60)
            ecoembed.description = f"⌚ | try after {min}min {sec}seconds."
            await ctx.send (embed = ecoembed)
            return   
    
    
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 10 , BucketType.user)
    # async def cal(self , ctx , type :  typing.Literal['buy' , 'sell'] ,  amount : int ):
    #    if type == 'buy':
    #     total_stocks = self.stock_data[ctx.guild.id]['total_share']
    #     sold_stocks = 0
    #     economy = db[f"{ctx.guild.id}"]
    #     lb_data = economy.find({"id" :{ "$gt" : 0 }}).sort("bank" , -1)
    #     docs = await lb_data.to_list(length = 500000)
    #     total_economy = 0
    #     for x in docs :
    #         total_economy += x['bank'] + x['cash']
    #         try : sold_stocks += x['share'] 
    #         except : pass
    #     current_stocks = total_stocks - sold_stocks    
    #     current_rate =  (total_economy/ current_stocks ) * 1/2   
        
    #     total_cost = 0
    #     number = 0
        
    #     for x in range( current_stocks - 1 , current_stocks - amount -1 , -1 ):
    #         total_cost += current_rate
    #         number += 1
    #         total_economy = total_economy - current_rate
    #         current_rate = ( total_economy - current_rate ) / (x*2)
    #     await ctx.send(f"total cost = {total_cost} , \nnumber = {number} , \ncurrent_rate = {current_rate} , \ncurrent_stock = {current_stocks}")    
    #     return
    #    elif type == "sell" :
    #     total_stocks = self.stock_data[ctx.guild.id]['total_share']
    #     sold_stocks = 0
    #     economy = db[f"{ctx.guild.id}"]
    #     lb_data = economy.find({"id" :{ "$gt" : 0 }}).sort("bank" , -1)
    #     docs = await lb_data.to_list(length = 500000)
    #     total_economy = 0
    #     for x in docs :
    #         total_economy += x['bank'] + x['cash']
    #         try : sold_stocks += x['share'] 
    #         except : pass
            
    #     current_stocks = total_stocks - sold_stocks + amount  
    #     current_rate =  (total_economy/ current_stocks ) * 1/2   
        
    #     total_cost = 0
    #     number = 0
        
    #     # for x in range(  current_stocks - amount - 1 , current_stocks -1 ):
    #     #     total_economy = total_economy + current_rate
    #     #     current_rate = ( total_economy + current_rate ) / (x*2)
    #     #     total_cost += current_rate
    #     #     number += 1
        
    #     for x in range( current_stocks - amount - 1 , current_stocks - 1   ): #current_stocks - amount  , -1 ):
    #         number += 1
    #         total_cost += current_rate
    #         total_economy = total_economy + current_rate
    #         current_rate = ( total_economy + current_rate ) / (x*2)
    #     await ctx.send(f"total cost = {total_cost} \nnumber = {number} , \ncurrent_rate = {current_rate} , \ncurrent_stock = {current_stocks}")  
    #     return

async def setup(client):
   await client.add_cog(Market(client))                       