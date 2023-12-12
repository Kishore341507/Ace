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

class myview(discord.ui.View):

    def __init__(self , timeout , users , player_iter , current , amount , embed):
        super().__init__(timeout=timeout)
        self.count = len(users)
        self.msg = None
        self.users = users
        self.player_iter = player_iter
        self.cards = ['<:10C:1025933874611617792>', '<:10D:1025933876557778954>', '<:10H:1025933878336176158>', '<:10S:1025933880152313936>', '<:2C:1025933882245251112>', '<:2D:1025934063736979527>', '<:2H:1025934066773667850>', '<:2S:1025934068933742602>', '<:3C:1025934071282552923>', '<:4C:1025934073136414790>', '<:4S:1025934712683909172>', '<:5C:1025934714730721372>', '<:5D:1025934716806893649>', '<:5H:1025934718413312135>', '<:5S:1025934720686641283>', '<:6C:1025934898369937448>', '<:6H:1025934900332855326>', '<:6S:1025934902190944338>', '<:7C:1025934903944159333>', '<:7D:1025934906225868800>', '<:7S:1025934984588050473>', '<:8D:1025934986609688598>', '<:8H:1025934988396470313>', '<:8S:1025934990560739381>', '<:9C:1025934992372670466>', '<:9D:1025935114187841668>', '<:9H:1025935115915890828>', '<:9S:1025935118520553522>', '<:aC:1025935120407990332>', '<:aD:1025935122295423017>', '<:aH:1025935205296525343>', '<:aS:1025935207255244940>', '<:jC:1025935209104945222>', '<:jD:1025935210551984279>', '<:jH:1025935213135679488>', '<:kD:1025935302033932288>', '<:kH:1025935304177221712>', '<:kS:1025935306421182544>', '<:qC:1025935308296032328>', '<:qD:1025935310405763172>', '<:qH:1025935400256163921>', '<:qS:1025935402210709585>', '<:8C:1026371928593805312>', '<:3S:1026372016808411146>', '<:jC:1026372126090997800>', '<:kC:1026372201856901151>', '<:3D:1026372278612676618>', '<:4D:1026372531013300305>', '<:4H:1026372680720597012>', '<:7H:1026372817509437520>','<:3H:1065689625609380030>', '<:4D:1065689759407685805>']
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
        if card[2] == "a":
            value = 14
        elif card[2] == "k":
            value = 13
        elif card[2] == "q":
            value = 12 
        elif card[2] == "j":
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
    
    async def check_channel(ctx) ->bool : 
        return ctx.channel.id in channel or ctx.author.id in [591011843552837655 , 572606210776236052]    
        
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
            msg = await channel.send(embed = discord.Embed(description=f"<a:811261898360094730:1063182356913078362> waiting for other player (exp <t:{int(datetime.now().timestamp()+30)}:R>)") , view = view)
            
            await asyncio.sleep(30)
            
            if  len(self.players[channel]) == 1 :
                self.players.pop(channel)
                await msg.edit(embed = discord.Embed(description="No match found") , view = None)
                return
            else : 
                users = self.players[channel]
                self.players.pop(channel)
                embed = discord.Embed(description= f"Game total Bet - {len(users)*amount:,}\nGame Current Bet - {amount}")
                embed.set_thumbnail( url = "https://media.discordapp.net/attachments/976542645801328681/1067027599387283526/sky247_logo_1.png")
                
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