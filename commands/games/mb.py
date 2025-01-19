import discord
from discord.ext import commands
import time
import typing
from datetime import datetime , date  , timedelta
import re
import asyncio
import json
from discord.ext.commands import BucketType, cooldown
from itertools import cycle
import random
from database import *
import traceback
from utils import  check_channel

class myview(discord.ui.View):

    def __init__(self , timeout , users , player_iter , current , amount , embed):
        super().__init__(timeout=timeout)
        self.count = len(users)
        self.msg = None
        self.users = users
        self.player_iter = player_iter
        self.cards = ['<:10C:1147776234466590810>', '<:10D:1147776375269380106>', '<:10H:1147776402050011236>', '<:10S:1147776426846736504>', '<:2C:1147776461877563412>', '<:2D:1147776571520864286>', '<:2H:1147776602919411763>', '<:2S:1147776656661037056>', '<:3C:1147776740748439662>', '<:3D:1147776779059212318>', '<:3H:1147776801624572006>', '<:3S:1147776840342179922>', '<:4C:1147776866942459964>', '<:4D:1147776891621757011>', '<:4H:1147776931887071364>', '<:4S:1147776969778397305>', '<:5C:1147777008017870889>', '<:5D:1147777032625852506>', '<:5H:1147777070542372874>', '<:5S:1147777094491848726>', '<:6C:1147777136678158406>', '<:6D:1147777171037896815>', '<:6H:1147777204651040768>', '<:6S:1147777234841645126>', '<:7C:1147777270677770321>', '<:7D:1147777310066479105>', '<:7H:1147777337673400390>', '<:7S:1147777379368976474>', '<:8C:1147777413254742077>', '<:8H:1147777546138693632>', '<:8D:1147777589793005669>', '<:8S:1147777642611875921>', '<:9C:1147777674790588508>', '<:9D:1147777706268831794>', '<:9H:1147777744302780416>', '<:9S:1147777779216158730>', '<:AC:1147777810979631125>', '<:AD:1147777839282794576>', '<:AH:1147777870173851688>', '<:AS:1147777908027445330>' , '<:JC:1147783707319615518>', '<:JD:1147783757470904370>', '<:JH:1147783825917743135>', '<:JS:1147783870499000420>', '<:KC:1147783909338259466>', '<:KD:1147783938379616346>', '<:KH:1147783968909963354>', '<:KS:1147784005584961606>', '<:QC:1147784027072372746>', '<:QD:1147784060677136395>', '<:QH:1147784089399722026>', '<:QS:1147784116499120138>']
        self.betamount = amount
        self.current = current
        self.embed = embed 
        self.result_text = " "
        self.time = time.time()

        
        
        for i in range(3):
            for user in self.users:
                item = random.choice(self.cards)
                self.cards.remove(item)
                self.users[user]['player_cards'].append(item)  
   
                
   
    #Card Info
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
     
    
    def compair_two(self , player1 , player2):
    
        for user in self.users:
            value_lis = []
            colour_lis = [] 
            for i in self.users[user]["player_cards"] :
               value , colour = self.info(i)
               value_lis.append(value)
               colour_lis.append(colour)
            value_lis.sort()   
            if value_lis[0] == value_lis[1] == value_lis[2]:
                self.users[user]["compair"] = (6 , value_lis[2] , 0 , 0)
                
            elif (colour_lis[0] ==  colour_lis[1] ==  colour_lis[2]) and (((value_lis[2]-2) == (value_lis[1]-1) == value_lis[0]) or (value_lis[2] == 14 and value_lis[1] == 3 and value_lis[0]== 2 )):
                self.users[user]["compair"] = (5 , value_lis[2] , value_lis[1] , 0) 
              
            elif  ((value_lis[2]-2) == (value_lis[1]-1) == value_lis[0]) or (value_lis[2] == 14 and value_lis[1] == 3 and value_lis[0]== 2 ):
                self.users[user]["compair"] = (4 , value_lis[2] , value_lis[1] , 0)  
               
            elif (colour_lis[0] ==  colour_lis[1] ==  colour_lis[2]) :
                self.users[user]["compair"] = (3 ,value_lis[2] , value_lis[1] , value_lis[0] )                  
            
            elif value_lis[0] == value_lis[1] or value_lis[1] == value_lis[2] :
                self.users[user]["compair"] = (2 , value_lis[1] , sum(value_lis) ,  0)
                
            else :
                self.users[user]["compair"] = (1 ,value_lis[2] , value_lis[1] , value_lis[0]) 
                   
        if self.users[player1]["compair"] > self.users[player2]["compair"] :
            return player2
        else :
            return player1  
    
     
    #Find Winner    
    def winner(self):
    
    
        for user in self.users:
            value_lis = []
            colour_lis = [] 
            for i in self.users[user]["player_cards"] :
               value , colour = self.info(i)
               value_lis.append(value)
               colour_lis.append(colour)
            value_lis.sort()   
            if value_lis[0] == value_lis[1] == value_lis[2]:
                self.users[user]["compair"] = (6 , value_lis[2] , 0 , 0)
                self.result_text = "(Trail)"
            elif (colour_lis[0] ==  colour_lis[1] ==  colour_lis[2]) and (((value_lis[2]-2) == (value_lis[1]-1) == value_lis[0]) or (value_lis[2] == 14 and value_lis[1] == 3 and value_lis[0]== 2 )):
                self.users[user]["compair"] = (5 , value_lis[2] , value_lis[1] , 0) 
                self.result_text = "(Pure Sequence)"
            elif  ((value_lis[2]-2) == (value_lis[1]-1) == value_lis[0]) or (value_lis[2] == 14 and value_lis[1] == 3 and value_lis[0]== 2 ):
                self.users[user]["compair"] = (4 , value_lis[2] , value_lis[1] , 0)  
                self.result_text = "(Sequence)"
            elif (colour_lis[0] ==  colour_lis[1] ==  colour_lis[2]) :
                self.users[user]["compair"] = (3 ,value_lis[2] , value_lis[1] , value_lis[0] )                  
                self.result_text = "(Color)"
            elif value_lis[0] == value_lis[1] or value_lis[1] == value_lis[2] :
                self.users[user]["compair"] = (2 , value_lis[1] , sum(value_lis) ,  0)
                self.result_text = "(Pair)"
            else :
                self.users[user]["compair"] = (1 ,value_lis[2] , value_lis[1] , value_lis[0])    
                self.result_text = "(High Card)"
        
        temp_result = (0,0,0)
        temp_winner = None
        for user in self.users :
            if self.users[user]['in_game'] is False :
                continue
            if self.users[user]["compair"] > temp_result :
                temp_result = self.users[user]["compair"]
                temp_winner = user 
        
        return temp_winner
                    
       
    def y(self , value : bool):
            if value :
                return " "
            else:
                return "(playing blind)\n"  
    
    
    def get_embed(self):
        
        total_amount = 0 
        for user in self.users :
            total_amount += self.users[user]["amounts"][1]
            
        self.embed.description =  f"Game total Bet - {total_amount:,}\nGame Current Bet - {self.betamount:,}"
         
        self.embed.clear_fields()
        for user in self.users :
            if user == self.current :
                self.embed.add_field( name = f"{user.name} {self.users[user]['status']} *<t:{int(datetime.now().timestamp() + 30)}:R>" , value = f"{self.y(self.users[user]['blind_info'])}Last Bet : +{self.users[user]['amounts'][0]:,}\n\nTotal Bet : {self.users[user]['amounts'][1]:,}")
                continue
            self.embed.add_field( name = f"{user.name} {self.users[user]['status']}" , value = f"{self.y(self.users[user]['blind_info'])}Last Bet : +{self.users[user]['amounts'][0]:,}\n\nTotal Bet : {self.users[user]['amounts'][1]:,}") 
    
    async def winner_update(self , winner):
        self.embed.clear_fields()
        for user in self.users :
            if user == winner :
                self.embed.add_field(name = f"{user.name} 👑" , value= f"Last Bet : +{self.users[user]['amounts'][0]:,}\n\nTotal Bet : {self.users[user]['amounts'][1]:,}\n\n{' '.join(self.users[user]['player_cards'])}\n{self.result_text}")
                continue
            self.embed.add_field(name = user.name , value= f"Last Bet : +{self.users[user]['amounts'][0]:,}\n\nTotal Bet : {self.users[user]['amounts'][1]:,}\n\n{' '.join(self.users[user]['player_cards'])}")
        #self.embed.description = f"{self.user[0]['user']} vs {self.user[1]['user']}\n\n{winner.name} **wins** `{self.amounts[self.user[0]['user']][1] + self.amounts[self.user[1]['user']][1]:,}`"
        for child in self.children:
            child.disabled = True   
                  
    def remove_iter(self  , iter , element):
        current_element = next(iter)
        temp_dict = {}
        temp_dict[current_element] = self.users[current_element]
        
        for i in iter :
            if i == current_element :
                break
            temp_dict[i] = self.users     
        temp_dict.pop(element) 
        self.player_iter = cycle(temp_dict)
        self.current = next(self.player_iter)
        self.count -= 1
           
    @discord.ui.button( label = "2xBet" , style = discord.ButtonStyle.blurple) 
    async def bet_2(self , interaction , button):
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return 
 
        self.betamount *= 2  
        if not self.users[self.current]['blind_info'] :
            self.users[self.current]["amounts"][1] += int(self.betamount/2)
        else :    
            self.users[self.current]["amounts"][1] += self.betamount
        self.users[self.current]["amounts"][0] = self.betamount
        self.current = next(self.player_iter)
        self.get_embed()
        # await self.update_embed(self.current)
        await interaction.response.edit_message(embed = self.embed) 
        
        
    @discord.ui.button( label = "Bet" , style = discord.ButtonStyle.green) 
    async def bet(self , interaction , button):
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return
        
        if not self.users[self.current]['blind_info'] :
            self.users[self.current]["amounts"][1] += int(self.betamount/2)
        else :    
            self.users[self.current]["amounts"][1] += self.betamount
            
        self.users[self.current]["amounts"][0] = self.betamount
        self.current = next(self.player_iter)
        self.get_embed()
        await interaction.response.edit_message(embed = self.embed)
        
        
        
    @discord.ui.button( label = "Show" , style = discord.ButtonStyle.gray) 
    async def show(self , interaction , button):    
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return  
        
        if self.count != 2 :
            self.embed.set_footer(text= f"Show Only Enable In Last 2 Players" )
            await interaction.response.edit_message(embed = self.embed) 
            self.embed.set_footer(text= " ")
            return    
        
        if not self.users[self.current]['blind_info'] :
            self.users[self.current]["amounts"][1] += int(self.betamount/2)
        else :    
            self.users[self.current]["amounts"][1] += self.betamount
            
        self.users[self.current]["amounts"][0] = self.betamount
        
        self.current = next(self.player_iter)
        
        win = self.winner()
        
        await self.winner_update(win)
        
        # await self.update_embed(self.current)
        await interaction.response.edit_message(embed = self.embed , view = self)
        self.stop() 
    
    @discord.ui.button( label = "Pack" , style = discord.ButtonStyle.red) 
    async def pack(self , interaction , button):
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return
        if self.count == 2 : 
            self.current = next(self.player_iter)
            await self.winner_update(self.current) 
        # await self.update_embed(self.current)
            await interaction.response.edit_message(embed = self.embed , view = self)
            self.stop()
        else :
            self.users[self.current]['status'] = "(PACK)"
            self.users[self.current]['in_game'] = False
          
            self.remove_iter(self.player_iter, self.current)
            self.get_embed()
            await interaction.response.edit_message(embed = self.embed , view = self)


    @discord.ui.button( label = "Show Cards" , style = discord.ButtonStyle.gray , row = 1) 
    async def show_cards(self , interaction , button):
      
        if interaction.user not in self.users :
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return
        
        self.users[interaction.user]['blind_info'] = True
      
        await interaction.response.send_message(' '.join(self.users[interaction.user]['player_cards']) , ephemeral = True )            

    @discord.ui.button( label = "Side Show" , style = discord.ButtonStyle.red , row = 1) 
    async def side_show(self , interaction , button):
        
        if interaction.user != self.current:
            await interaction.response.send_message(f"{self.current}'s Turn" , ephemeral = True)
            return
        
        if self.count == 2 :
            self.embed.set_footer(text= f"Side Show Only Enable In At Least 3 Players" )
            await interaction.response.edit_message(embed = self.embed) 
            self.embed.set_footer(text= " ")
            return    
        
        if not self.users[self.current]['blind_info'] :
            self.users[self.current]["amounts"][1] += int(self.betamount/2)
        else :    
            self.users[self.current]["amounts"][1] += self.betamount 
        self.users[self.current]["amounts"][0] = self.betamount
        
        current_player = self.current
        next_player = next(self.player_iter)
        for i in self.player_iter :
            if i == current_player :
                break
        
        lost = self.compair_two(current_player, next_player)    
            
        self.users[lost]['status'] = "(PACK)"
        self.users[lost]['in_game'] = False
        self.remove_iter(self.player_iter, lost)
        self.get_embed()
        self.embed.set_footer(text= f"❎ {lost} is Lost in Side Show")
        await interaction.response.edit_message(embed = self.embed , view = self)
        self.embed.set_footer(text= " ")
        
    
    @discord.ui.button( label = "?" , style = discord.ButtonStyle.red  , row = 1) 
    async def Replay(self , interaction , button):
        await interaction.response.send_message( "**Blinds Rules**\n\nThe Aces have been ranked as the highest with 2 being the lowest. The goal is to have the top 3-card hand and increase the pot before the game ends. The rankings are as follows:\n\nRanking of the cards from highest to lowest:\n\n ||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​|| _ _ _ _ _ _ https://cdn.discordapp.com/attachments/1059511042604015696/1066562988590514246/image.png" , ephemeral = True )
        return

    async def interaction_check(self, interaction):
        if interaction.user == self.current : 
            self.time = time.time()
        if interaction.user in self.users :
            if (time.time() - self.time) > 30 :
                if self.count == 2 : 
                    self.current = next(self.player_iter)
                    await self.winner_update(self.current) 
                    await interaction.response.edit_message(embed = self.embed , view = self)
                    self.stop()
                    return False        
                else :
                    self.users[self.current]['status'] = "(PACK)"
                    self.users[self.current]['in_game'] = False
                    self.remove_iter(self.player_iter, self.current)
                    self.get_embed()
                    await interaction.response.edit_message(embed = self.embed , view = self)
                    self.time = time.time()
                    return False
            return True    


    async def on_error(self, interaction, error, item):
        full_error = traceback.format_exception(error)
        try:
            await interaction.response.send_message(f"{full_error}")
        except:
               await interaction.followup.send(f"{full_error}")          

class join_blind(discord.ui.View):
    
    def __init__(self , timeout , temp_self ,user , amount):
        super().__init__(timeout=timeout)
        self.temp_self = temp_self
        self.user = user
        self.amount = amount
    
    @discord.ui.button(label = "Join" , style = discord.ButtonStyle.gray )
    async def join_button(self , interaction , button):
        # if interaction.user.id == self.user.id:
            # await interaction.response.send_message("you cant join your own match" , ephemeral = True)
            # return
        await Mb.blind_fun( self.temp_self, interaction.channel , interaction.user , self.amount )
        await interaction.response.defer()



class Mb(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.players = {}
    
    # async def check_channel(ctx) ->bool : 
    #     return ctx.channel.id in channel or ctx.author.id in [591011843552837655 , 572606210776236052]    
        
    async def blind_fun(self , channel , author , amount ):
        
        amount = 1000
        
        try :
            if author in self.players[channel] :
                await channel.send(F"{author.mention} You are already in game" , delete_after = 3)
                return
            if len(self.players[channel]) < 5 :
                self.players[channel][author] = {"amounts" : [amount , amount] , "compair" : None , 'blind_info' : False , 'player_cards' : [] , "in_game" : True , "status" : ' ' }
                await channel.send(f"{author.mention} joined the game {len(self.players[channel])}/4 " , delete_after = 3 )
            else :
                await channel.send(f"{author.mention} game is full , try after some time" , delete_after = 3 )    
        except KeyError :     
            self.players[channel] = {}
            self.players[channel][author] = {"amounts" : [amount , amount] , "compair" : None , 'blind_info' : False , 'player_cards' : [] , "in_game" : True ,  "status" : ' ' }
            # self.players["channel"]["user"] = {"a" : 5 , "b" : 6}
        # if len(self.players[channel]) == 0:
            view = join_blind(30, self , author , amount)
            msg = await channel.send(embed = discord.Embed(description=f"<a:dcload:1330518199372091473> waiting for other player (exp <t:{int(datetime.now().timestamp()+30)}:R>)") , view = view)
            
            await asyncio.sleep(30)
            
            if  len(self.players[channel]) == 1 :
                self.players.pop(channel)
                await msg.edit(embed = discord.Embed(description="No match found") , view = None)
                return
            else : 
                users = self.players[channel]
                self.players.pop(channel)
                embed = discord.Embed(description= f"Game total Bet - {len(users)*amount:,}\nGame Current Bet - {amount}")
                # embed.set_thumbnail( url = "https://media.discordapp.net/attachments/976542645801328681/1067027599387283526/sky247_logo_1.png")
                
                player_iter = cycle(users)
                current = next(player_iter)
                for user in users :
                    if user == current :
                        embed.add_field(name = f"{user.name} *<t:{int(datetime.now().timestamp() + 30)}:R>" , value= f"*Last Bet : +{amount:,}\n\nTotal Bet : {amount:,}"  )
                        continue
                    embed.add_field(name = f"{user.name}" , value= f"*Last Bet : +{amount:,}\n\nTotal Bet : {amount:,}" )
            # embed.add_field(name = f"{author.name} *<t:{int(datetime.now().timestamp() + 30)}:R>" , value= f"*Last Bet : +{amount:,}\n\nTotal Bet : {amount:,}")
            # embed.add_field(name = element['user'].name , value= f"*Last Bet : +{amount:,}\n\nTotal Bet : {amount:,}")
                view = myview(timeout = None , users = users , player_iter = player_iter , current = current , amount = amount , embed = embed) 
                msg1 = await channel.send( f" ".join([i.mention for i in users]) ,embed = embed, view = view)  #f" ".join([i.mention for i in users])
                view.msg = msg1
                await msg.delete()
                return
    
    @commands.hybrid_command()#aliases = ['blinds' , '3patti'])
    @commands.check(check_channel)
    @commands.cooldown(1, 40 , BucketType.user)
    async def mb(self , ctx , amount : typing.Literal[100 , 1000 , 10000] = 1000):

        '''
        This game is not part of economy system , economy will be added soon
        '''
        
        await self.blind_fun( ctx.channel,  ctx.author  , amount )
        

    @mb.error
    async def error(self , ctx , error):
        if isinstance(error, commands.CommandOnCooldown ):
            await ctx.send(embed = discord.Embed(description= f"You are on cooldown , retry in {int(error.retry_after)}seconds.") , delete_after=3)
        else : 
            full_error = traceback.format_exception(error)
            await ctx.author.send(full_error)    
         

async def setup(client):
   await client.add_cog(Mb(client))