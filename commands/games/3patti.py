import discord
from discord.ext import commands
import typing
from datetime import datetime , date , time , timedelta
import re
import asyncio
import json
from discord.ext.commands import BucketType, cooldown
from itertools import cycle
import random
from database import *
import traceback
from utils import  check_channel

async def get_bal(user_id , guild_id) :
    bal = await client.db.fetchrow('SELECT cash , pvc FROM users WHERE id = $1 AND guild_id = $2 ', user_id , guild_id)
    return bal or {"cash" : 0 , "pvc" : 0}

class myview(discord.ui.View):

    def __init__(self , timeout , user , amount , embed):
        super().__init__(timeout=timeout)
        self.user = user
        self.player = cycle([ user[1]['user'] , user[0]['user'] ])
        self.cards = ['<:10C:1147776234466590810>', '<:10D:1147776375269380106>', '<:10H:1147776402050011236>', '<:10S:1147776426846736504>', '<:2C:1147776461877563412>', '<:2D:1147776571520864286>', '<:2H:1147776602919411763>', '<:2S:1147776656661037056>', '<:3C:1147776740748439662>', '<:3D:1147776779059212318>', '<:3H:1147776801624572006>', '<:3S:1147776840342179922>', '<:4C:1147776866942459964>', '<:4D:1147776891621757011>', '<:4H:1147776931887071364>', '<:4S:1147776969778397305>', '<:5C:1147777008017870889>', '<:5D:1147777032625852506>', '<:5H:1147777070542372874>', '<:5S:1147777094491848726>', '<:6C:1147777136678158406>', '<:6D:1147777171037896815>', '<:6H:1147777204651040768>', '<:6S:1147777234841645126>', '<:7C:1147777270677770321>', '<:7D:1147777310066479105>', '<:7H:1147777337673400390>', '<:7S:1147777379368976474>', '<:8C:1147777413254742077>', '<:8H:1147777546138693632>', '<:8D:1147777589793005669>', '<:8S:1147777642611875921>', '<:9C:1147777674790588508>', '<:9D:1147777706268831794>', '<:9H:1147777744302780416>', '<:9S:1147777779216158730>', '<:AC:1147777810979631125>', '<:AD:1147777839282794576>', '<:AH:1147777870173851688>', '<:AS:1147777908027445330>' , '<:JC:1147783707319615518>', '<:JD:1147783757470904370>', '<:JH:1147783825917743135>', '<:JS:1147783870499000420>', '<:KC:1147783909338259466>', '<:KD:1147783938379616346>', '<:KH:1147783968909963354>', '<:KS:1147784005584961606>', '<:QC:1147784027072372746>', '<:QD:1147784060677136395>', '<:QH:1147784089399722026>', '<:QS:1147784116499120138>']
        self.amounts = {user[0]['user'] : [amount , amount , user[0]['bank_amount'] ] , user[1]['user'] : [amount , amount , user[1]['bank_amount']]}
        self.betamount = amount
        self.current = user[0]['user']
        self.embed = embed 
        self.player_cards = None
        self.compair = { self.user[0]['user'] : None , self.user[1]['user'] :None}
        self.blind_info = { self.user[0]['user'] : False , self.user[1]['user'] : False}
    
    def info( self , card : str ):
        if card[2] == "A":
            value = 14
        elif card[2] == "K":
            value = 13
        elif card[2] == "Q":
            value = 12 
        elif card[2] == "J":
            value = 11
        else  :
            value = int(card[2])
        colour = card[3]  
        if card[2] == "1":
            value = 10
            colour = card[4]
        return value , colour 

    def pattern(self , user):
        det = {1 : "(High Card)" , 2 : "(Pair)" , 3 : "(Color)" , 4 : "(Sequence)" , 5 : "(Pure Sequence)" , 6 : "(Trail)" } 
        try :
            return det[self.compair[user][0]]
        except :
            return " "

    def winner(self):
        if self.player_cards is None :
            self.set_cards()
        for key in self.player_cards:
            value_lis = []
            colour_lis = [] 
            for i in self.player_cards[key] :
               value , colour = self.info(i)
               value_lis.append(value)
               colour_lis.append(colour)
            value_lis.sort()   
            if value_lis[0] == value_lis[1] == value_lis[2]:
                self.compair[key] = (6 , value_lis[2] , 0 , 0)
            elif (colour_lis[0] ==  colour_lis[1] ==  colour_lis[2]) and (((value_lis[2]-2) == (value_lis[1]-1) == value_lis[0]) or (value_lis[2] == 14 and value_lis[1] == 3 and value_lis[0]== 2 )):
                self.compair[key] = (5 , value_lis[2] , value_lis[1] , 0) 
            elif  ((value_lis[2]-2) == (value_lis[1]-1) == value_lis[0]) or (value_lis[2] == 14 and value_lis[1] == 3 and value_lis[0]== 2 ):
                self.compair[key] = (4 , value_lis[2] , value_lis[1] , 0)  
            elif (colour_lis[0] ==  colour_lis[1] ==  colour_lis[2]) :
                self.compair[key] = (3 ,value_lis[2] , value_lis[1] , value_lis[0] )                  
            elif value_lis[0] == value_lis[1] or value_lis[1] == value_lis[2] :
                self.compair[key] = (2 , value_lis[1] , sum(value_lis) ,  0)
            else :
                self.compair[key] = (1 ,value_lis[2] , value_lis[1] , value_lis[0])    
                
        if self.compair[self.user[0]['user']] > self.compair[self.user[1]['user']]:
            return self.user[0]['user']
        elif  self.compair[self.user[0]['user']] < self.compair[self.user[1]['user']] :
            return self.user[1]['user']  
            
            
            
    async def update_embed(self , current , to = False):
        if self.user[0]['channel'].id ==  self.user[1]['channel'].id and to is False:
            return
        for i in self.user :
            if i['user'] == current :
                try: 
                    await i['message'].edit(embed = self.embed , view = self )
                except:
                    pass    
    
    def set_cards(self):
        self.player_cards =  { self.user[0]['user'] : [] , self.user[1]['user'] : []}
        for i in range(3):
            for key in self.player_cards:
                item = random.choice(self.cards)
                self.cards.remove(item)
                self.player_cards[key].append(item)    
       
    def y(self , value : bool):
            if value :
                return " "
            else:
                return "(playing blind)\n"  
    
    def get_embed(self):
        if self.user[0]['user'] == self.current :
            text1 = f"*<t:{int(datetime.now().timestamp() + self.timeout)}:R>"
            text2 = " "
        elif  self.user[1]['user'] == self.current:
            text1 = " "
            text2 = f"*<t:{int(datetime.now().timestamp() + self.timeout)}:R>"  
                
        self.embed.set_field_at(0 , name = f"{self.user[0]['user'].name} {text1}" , value= f"{self.y(self.blind_info[self.user[0]['user']])}Last Bet : +{self.amounts[self.user[0]['user']][0]:,}\n\nTotal Bet : {self.amounts[self.user[0]['user']][1]:,}")
        self.embed.set_field_at(1 , name = f"{ self.user[1]['user'].name} {text2}" , value= f"{self.y(self.blind_info[self.user[1]['user']])}Last Bet : +{self.amounts[self.user[1]['user']][0]:,}\n\nTotal Bet : {self.amounts[self.user[1]['user']][1]:,}")
    
    async def winner_update(self , winner):
        
        # coll = db["966022734398246963"]
        
        # await coll.update_one({"id" :self.user[0]['user'].id } , {"$inc" : { "pvc" : + self.amounts[self.user[0]['user']][2] }})
        # await coll.update_one({"id" :self.user[1]['user'].id } , {"$inc" : { "pvc" : + self.amounts[self.user[1]['user']][2] }})
        
        text03 = text13 = " "
        if self.user[0]['user'] == winner :
            text1 = "👑"
            text2 = " "
            text03 = self.pattern( self.user[0]['user'])
            await client.db.execute("UPDATE users SET pvc = pvc + $1 WHERE id = $2 AND guild_id = $3", (self.amounts[self.user[0]['user']][1] + self.amounts[self.user[1]['user']][1]) , self.user[0]['user'].id , self.user[0]['channel'].guild.id)
            
        elif  self.user[1]['user'] == winner :
            text1 = " "
            text2 = "👑"   
            text13 = self.pattern( self.user[1]['user'])
            await client.db.execute("UPDATE users SET pvc = pvc + $1 WHERE id = $2 AND guild_id = $3", (self.amounts[self.user[0]['user']][1] + self.amounts[self.user[1]['user']][1]) , self.user[1]['user'].id , self.user[1]['channel'].guild.id)
            
        self.embed.description = f"{self.user[0]['user']} vs {self.user[1]['user']}\n\n{winner.name} **wins** `{self.amounts[self.user[0]['user']][1] + self.amounts[self.user[1]['user']][1]:,}`"  
        c1 = " ".join(self.player_cards[self.user[0]['user']]) 
        c2 = " ".join(self.player_cards[self.user[1]['user']]) 
        self.embed.set_field_at(0 , name = f"{self.user[0]['user'].name} {text1}" , value= f"Last Bet : +{self.amounts[self.user[0]['user']][0]:,}\n\nTotal Bet : {self.amounts[self.user[0]['user']][1]:,}\n\n{c1}\n{text03}")
        self.embed.set_field_at(1 , name = f"{ self.user[1]['user'].name} {text2}" , value= f"Last Bet : +{self.amounts[self.user[1]['user']][0]:,}\n\nTotal Bet : {self.amounts[self.user[1]['user']][1]:,}\n\n{c2}\n{text13}")
        for child in self.children:
            child.disabled = True   
                         
    @discord.ui.button( label = "2xBet" , style = discord.ButtonStyle.blurple) 
    async def bet_2(self , interaction , button):
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return
        if self.user[0]['message'] == None and interaction.user == self.user[0]['user']:
            self.user[0]['message'] = interaction.message
            
        self.amounts[self.current][2] = (await get_bal(self.current.id , interaction.guild.id ))['pvc']    
        
        if ((2*self.betamount) ) >  self.amounts[self.current][2]:
            self.embed.set_footer(text= f"🛑 {self.current.name} You Can't Bet 2x Now , Bet 1x Or Show")
            await interaction.response.edit_message(embed = self.embed)
            self.embed.set_footer(text=None)
            return  
        
        # if ((4*self.betamount) ) >  self.amounts[self.current][2]:
        #     self.embed.set_footer(text= f"⚠️ {self.current.name} you have limited money , be aware of bankrupt")
        #     await interaction.response.edit_message(embed = self.embed)
        #     self.embed.set_footer(text=None)
        
        self.betamount *= 2  
        if not self.blind_info[self.current]  :
            self.amounts[self.current][1] += int(self.betamount/2)
            await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3", int(self.betamount/2), self.current.id , interaction.guild.id)
        else :    
            self.amounts[self.current][1] += self.betamount
            await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3", int(self.betamount), self.current.id , interaction.guild.id)
        self.amounts[self.current][0] = self.betamount
        self.current = next(self.player)
        self.get_embed()
        await self.update_embed(self.current)
        await interaction.response.edit_message(embed = self.embed) 
        self.timeout = 30     
        
    @discord.ui.button( label = "Bet" , style = discord.ButtonStyle.green) 
    async def bet(self , interaction , button):
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return
        
        self.amounts[self.current][2] = (await get_bal(self.current.id , interaction.guild.id ))['pvc']    
               
        if ( self.betamount ) >  self.amounts[self.current][2]:
            self.embed.set_footer(text= f"🛑 {self.current.name} No More Money In pvc , Last option Is Pack")
            await interaction.response.edit_message(embed = self.embed)
            self.embed.set_footer(text=None)
            return  
        
        # if ((3*self.betamount) ) >  self.amounts[self.current][2]:
        #     self.embed.set_footer(text= f"⚠️ {self.current.name} you have limited money , be aware of bankrupt")
        #     await interaction.response.edit_message(embed = self.embed)
        #     self.embed.set_footer(text=None)
        
        if self.user[0]['message'] == None and interaction.user == self.user[0]['user']:
            self.user[0]['message'] = interaction.message
         
        if not self.blind_info[self.current]  :
            self.amounts[self.current][1] += int(self.betamount/2)
            await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3", int(self.betamount/2), self.current.id , interaction.guild.id)
        else :    
            self.amounts[self.current][1] += self.betamount
            await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3", int(self.betamount), self.current.id , interaction.guild.id)
            
        self.amounts[self.current][0] = self.betamount
        self.current = next(self.player)
        self.get_embed()
        await self.update_embed(self.current)
        await interaction.response.edit_message(embed = self.embed)
        self.timeout = 30
       
        
    @discord.ui.button( label = "Show" , style = discord.ButtonStyle.gray) 
    async def show(self , interaction , button):    
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return
        if self.user[0]['message'] == None and interaction.user == self.user[0]['user']:
            self.user[0]['message'] = interaction.message
        
        self.amounts[self.current][2] = (await get_bal(self.current.id , interaction.guild.id ))['pvc']    

        if (self.betamount ) >  self.amounts[self.current][2]:
            self.embed.set_footer(text= f"{self.current.name} No More Money In pvc , Last Option Is Pack")
            await interaction.response.edit_message(embed = self.embed)
            self.embed.set_footer(text=None)
            return
 
        await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3", int(self.betamount), self.current.id , interaction.guild.id)
        
        self.amounts[self.current][1] += self.betamount
        
        self.amounts[self.current][0] = self.betamount
        self.current = next(self.player)
        
        win = self.winner()
        
        await self.winner_update(win)
        
        await self.update_embed(self.current)
        await interaction.response.edit_message(embed = self.embed , view = self)
        self.stop() 
    
    @discord.ui.button( label = "Pack" , style = discord.ButtonStyle.red) 
    async def pack(self , interaction , button):
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return
        if self.user[0]['message'] == None and interaction.user == self.user[0]['user']:
            self.user[0]['message'] = interaction.message
        self.current = next(self.player)
        if self.player_cards is None :
            self.set_cards() 
        
        await self.winner_update(self.current)
            
        await self.update_embed(self.current)
        await interaction.response.edit_message(embed = self.embed , view = self)
        self.stop()    
    
    @discord.ui.button( label = "See Cards" , style = discord.ButtonStyle.gray , row = 1) 
    async def show_cards(self , interaction , button):
        if self.user[0]['message'] == None and interaction.user == self.user[0]['user']:
            self.user[0]['message'] = interaction.message
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return
        if self.player_cards is None :
            self.set_cards()
            
        self.blind_info[interaction.user] = True      
        await interaction.response.send_message(f"{self.player_cards[interaction.user][0]} {self.player_cards[interaction.user][1]} {self.player_cards[interaction.user][2]}" , ephemeral = True ) 
        self.blind_info[interaction.user] = True           
    
    @discord.ui.button( label = "?" , style = discord.ButtonStyle.green  , row = 1) 
    async def Replay(self , interaction , button):
        await interaction.response.send_message( "**Blinds Rules**\n\nThe Aces have been ranked as the highest with 2 being the lowest. The goal is to have the top 3-card hand and increase the pot before the game ends. The rankings are as follows:\n\nRanking of the cards from highest to lowest:\n\n ||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| _ _ _ _ _ _ https://cdn.discordapp.com/attachments/1059511042604015696/1066562988590514246/image.png" , ephemeral = True )
        return
       
    
    async def on_timeout(self) :
        self.current = next(self.player)
        if self.player_cards is None :
            self.set_cards() 
        
        await self.winner_update(self.current)
        
        await self.update_embed(self.current , to = True)
        await self.update_embed(next(self.player) , to = True)  
        self.stop()     


    async def on_error(self, interaction, error, item):
        try:
            await interaction.response.send_message(f"{error}")
        except:
               await interaction.followup.send(f"{error}")          

class join_blind(discord.ui.View):
    
    def __init__(self , timeout , temp_self ,user , amount):
        super().__init__(timeout=timeout)
        self.temp_self = temp_self
        self.user = user
        self.amount = amount
    
    @discord.ui.button(label = "Join" , style = discord.ButtonStyle.gray )
    async def join_button(self , interaction , button):
        if interaction.user.id == self.user.id:
            await interaction.response.send_message("You Cant Join Your Own Match" , ephemeral = True)
            return
        await patti.blind_fun( self.temp_self, interaction.channel , interaction.user , self.amount )

class patti(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.players = {  }
                
    async def blind_fun(self , channel , author , amount ):
        amount = amount
        # line 266 dc
        bal = await get_bal(author.id ,  channel.guild.id)
        
        if bal['pvc'] < amount :
            await channel.send(f"{author.mention} Don't have Enough Money" , delete_after = 3)
            return
        else : 
            bank_amount = bal['pvc']
        
        if len(self.players.get(channel , [ ])) == 0:
            view = join_blind(30, self , author , amount)
            msg = await channel.send(embed = discord.Embed(description=f"<a:dcload:1330518199372091473> Waiting For Other Player (Ends In <t:{int(datetime.now().timestamp()+30)}:R>)" , color=0x2a2c30) , view = view)
            element = {"user" : author , 'channel' : channel , "message" : msg , 'bank_amount' : bank_amount }
            
            try : 
                self.players[channel].append(element)
            except : 
                self.players[channel] = [ ]
                self.players[channel].append(element)
            
            await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3", amount, author.id, channel.guild.id)
                        
            await asyncio.sleep(30)
            if element in self.players[channel] :
                await client.db.execute("UPDATE users SET pvc = pvc + $1 WHERE id = $2 AND guild_id = $3", amount, author.id, channel.guild.id)
                self.players[channel].remove(element)
                await msg.edit(embed = discord.Embed(description="No match found" , color=0x2a2c30) , view = None)
                return
        else : 
            element = self.players[channel][0]
            self.players[channel].remove(element)
            embed = discord.Embed(description= f"{author} vs {element['user']}")
            embed.add_field(name = f"{author.name} *<t:{int(datetime.now().timestamp() + 30)}:R>" , value= f"*Last Bet : +{amount:,}\n\nTotal Bet : {amount:,}")
            embed.add_field(name = element['user'].name , value= f"*Last Bet : +{amount:,}\n\nTotal Bet : {amount:,}")
            view = myview(timeout = 30 , user = [{"user" : author , "channel" : channel , "message" : None , 'bank_amount' : bank_amount } , element ] , amount = amount , embed = embed)  #[{"user" : ctx.author , "channel" : ctx.channel , "message" : None} , element ] {ctx.author : { 'channel' : ctx.channel , 'message' : None   } , element['user'] : {'channel' : element['channel'] , 'message' : element['message']} }
           
            await client.db.execute("UPDATE users SET pvc = pvc - $1 WHERE id = $2 AND guild_id = $3", amount, author.id, channel.guild.id)
            
            if channel.id == element['channel'].id :
                msg1 = await channel.send( f"||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| _ _ _ _ _ _ {author.mention} {element['user'].mention}" ,embed = embed, view = view)
                view.user[0]['message'] = msg1
                await element['message'].delete()
                return
            try :
                await element["message"].edit( content=  element['user'].mention ,embed = embed , view = view) 
            except :
                msg2 = await element["channel"].send( content=  element['user'].mention ,embed = embed , view = view)  
                view.user[1]['message'] = msg2   
            msg1 = await channel.send( author.mention ,embed = embed, view = view)
            view.user[0]['message'] = msg1
            return
    
    
    @commands.hybrid_command( aliases = ['blinds' , '3patti'])
    @commands.check(check_channel)
    @commands.cooldown(1, 40 , BucketType.user)
    async def blind(self , ctx , amount : typing.Literal[10 ,100 , 1000 , 10000] = 10): 
        await self.blind_fun(ctx.channel, ctx.author , amount )
        

    @blind.error
    async def error(self , ctx , error):
        if isinstance(error, commands.CommandOnCooldown ):
            await ctx.send(embed = discord.Embed(description= f"You are on cooldown , retry in {int(error.retry_after)}seconds.") , delete_after=3)
        else : 
            print(traceback.format_exc())
            await ctx.author.send(error)    
         

async def setup(client):
   await client.add_cog(patti(client))         
