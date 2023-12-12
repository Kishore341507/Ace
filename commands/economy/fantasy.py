import discord
from discord.ext import commands , tasks
from database import *
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
import typing
from discord.ui import Button , View , Select
from discord import app_commands
import requests
from bs4 import BeautifulSoup
import datetime


class Fantasy(commands.Cog):

    def __init__(self , client):
        self.client = client       
        self.match_id = 66190
        self.messages = { }
        self.embed = None
        
    # async def check_channel(ctx) ->bool : 
    #     return ctx.channel.id in channel or ctx.author.id == 591011843552837655

    # async def cog_unload(self):
    #     self.live_score.cancel() 
    
    # @tasks.loop( minutes= 1)
    # async def live_score(self):
    #     if self.match_id == 0 :
    #       return
    #     dis = ' ' 
    #     batsman = []
    #     bowler = [] 
    #     list1 = []
        
    #     # finding match_id
        # page = requests.get(url = f"https://www.cricbuzz.com")
        # soup = BeautifulSoup(page.content, 'html.parser')
        # data  = soup.find('li' , class_ = 'cb-view-all-ga cb-match-card cb-bg-white')
        # link = data.find('a').get('href')
        # match_id = link.split('/')[2]
        
        # #gatting match data
        # page = requests.get(url = f"https://www.cricbuzz.com/live-cricket-scores/{match_id}")
        # soup = BeautifulSoup(page.content, 'html.parser')
        # score = soup.find('div' , class_ = 'cb-col-100 cb-col cb-col-scores')
        
        # try :
        #   score_divs = score.find_all('div')
        #   for div in score_divs :
        #       list1.append(div.get_text().replace('\xa0', '').strip())
          
        #   dis = dis + f"{'**' +list1[1].replace(' ', '** ', 1)}\n"
        #   if len(list1) > 4 :
        #     dis = dis + f"{'**' +list1[2].replace(' ', '** ', 1)}\n"        
        # except : pass
        
        # bord =  soup.find('div' , class_ = 'cb-col-67 cb-col')
        # try : 
        #   divs = bord.find_all('div' )
        #   status = None
        #   for div in divs :
        #     try : 
        #       if div.get_text() == 'Batter':
        #         status = True
        #       if div.get_text() == 'Bowler':
        #         status = False  
            
        #       if status is None :
        #          continue
        #       elif status is True : 
        #          batsman.append(div.get_text())
        #       elif status is False : 
        #         bowler.append(div.get_text())
        #     except : pass 
            
        # except : pass      
        
        # try :
        #   dis = dis + f"{'**' +list1[1].replace(' ', '** ', 1)}\n"
        #   if len(list1) > 4 :
        #     dis = dis + f"{'**' +list1[2].replace(' ', '** ', 1)}\n"
        # except : pass    
          
        # #batsman
        # try :
        #     dis = dis + f"\n`{'Batter':^17s}` `{'R':^3s}` `{'B':^3s}` `{'4s':^3s}` `{'6s':^3s}` `{'SR':^6s}`\n"  
        #     dis = dis + f"\n`{batsman[7]:^17s}` `{batsman[8]:^3s}` `{batsman[9]:^3s}` `{batsman[10]:^3s}` `{batsman[11]:^3s}` `{batsman[12]:^6s}`"  
        # except : 
        #   guild = await client.fetch_guild(966022734398246963)
        #   user = await guild.fetch_member(591011843552837655)
        #   await user.send("failed set match 0")
        #   return
        # try : dis = dis + f"\n`{batsman[14]:^17s}` `{batsman[15]:^3s}` `{batsman[16]:^3s}` `{batsman[17]:^3s}` `{batsman[18]:^3s}` `{batsman[19]:^6s}`"  
        # except : pass
        
        
        # #bowler
        # try : 
        #     dis = dis + f"\n\n`{'Bowler':^17s}` `{'O':^3s}` `{'M':^3s}` `{'R':^3s}` `{'W':^3s}` `{'ECO':^6s}`\n"  
        #     dis = dis + f"\n`{bowler[7]:^17s}` `{bowler[8]:^3s}` `{bowler[9]:^3s}` `{bowler[10]:^3s}` `{bowler[11]:^3s}` `{bowler[12]:^6s}`"  
        # except : pass    
        # try : dis = dis + f"\n`{bowler[14]:^17s}` `{bowler[15]:^3s}` `{bowler[16]:^3s}` `{bowler[17]:^3s}` `{bowler[18]:^3s}` `{bowler[19]:^6s}`"  
        # except : pass
        
        # try :
        #  rcnt =  soup.find('div' , class_ = 'cb-min-rcnt')
        #  rcnt_span = rcnt.find_all('span' )
        #  rcnt_list = []
        #  for div in rcnt_span :
        #   rcnt_list.append(div.get_text())
        #  dis = dis + f"\n\n{rcnt_list[1]}" 
        # except : pass 
        
        # self.embed = discord.Embed(color= 123456 , title= "🛑 Live Score" , description= dis , timestamp= datetime.datetime.now() )
        # try : 
        #   self.embed.set_footer( text =  list1[-2])
        # except : pass  
        
        # for guild in self.messages :
        #   try : await self.messages[guild].edit( embed = self.embed )
        #   except : pass
          
    # @live_score.error
    # async def task_error(self, error):
    #     guild = await client.fetch_guild(966022734398246963)
    #     user = await guild.fetch_member(591011843552837655)
    #     await user.send(error)
          
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 5, BucketType.user)
    # async def pointtable(self , ctx ):
    #     def get_emoji(name) :
    #       for emoji in self.client.emojis :
    #         if emoji.name == name:
    #           return emoji
    #       return self.client.get_emoji(995169982633750648)

    #     data = f"{get_emoji('india')} `{'TEAM':^6s}` `{'M':^3s}` `{'W':^3s}` `{'L':^3s}` `{'T':^3s}` `{'NR':^3s}` `{'Pts':^3s}` `{'NRR':^6s}`\n\n"

    #     page = requests.get(url = "https://www.cricbuzz.com/cricket-series/5945/indian-premier-league-2023/points-table")
    #     soup = BeautifulSoup(page.content, 'html.parser')
    #     score = soup.find('table' , class_ = 'table cb-srs-pnts')
    #     score_rows = score.find_all('tr')

    #     for row in score_rows:
    #       cells = row.find_all('td')
    #       row_data = []
    #       for cell in cells:
    #         row_data.append(cell.text)
    #       if len(row_data) == 9 :   
    #         data = data + f"{get_emoji(''.join([word[0].upper() for word in row_data[0].split()]))} `{''.join([word[0].upper() for word in row_data[0].split()]):^6s}` `{row_data[1]:^3s}` `{row_data[2]:^3s}` `{row_data[3]:^3s}` `{row_data[4]:^3s}` `{row_data[5]:^3s}` `{row_data[6]:^3s}` `{row_data[7]:^6s}`\n" 
            
    #     embed = discord.Embed(color= 123456 , title= ":flag_in: IPL Point-Table" , description= data )
    #     await ctx.send(embed = embed ) 
        
         
        
    # @commands.hybrid_command()
    # @commands.guild_only()
    # # @commands.is_owner()
    # async def livescore(self , ctx , messages_id : str = None):
      
    #   if messages_id is not None :
    #     msg = await ctx.channel.fetch_message(int(messages_id))
    #     await msg.edit( embed = self.embed)
    #     self.messages[ctx.guild.id] = msg 
    #     await ctx.author.send(self.messages)
    #     return
      
    #   msg = await ctx.send(embed = self.embed)
    #   self.messages[ctx.guild.id] = msg 
    #   await ctx.author.send(self.messages)
    
    # @livescore.error
    # async def livescore_error(self , ctx , error):
    #   await ctx.send(error)
    
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.is_owner()
    async def updatematch(self , ctx , number : int):
      self.match_id = number 
      await ctx.send(self.match_id)
    
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 5, BucketType.user)
    # async def info(self , ctx ,* , name : str ):
    #     img = None
    #     title = None
        
    #     for i in self.team_players :
    #         if name.upper() == i['shortname'] :
    #             data = f"`{'Name':^20s}`\n\n"
    #             title = i['teamName']
    #             img = i['img']
    #             for i in i['players'] :
    #                 data = data + f"`{i['name']:^20s}`\n" 
    #             break 
    #         for j in i['players'] :
    #           if name.lower() in j['name'].lower() :
    #               title = j['name']
    #               img = j["playerImg"]
    #               data = f"`{'Role':^12}` : `{j['role']:^18}`\n`{'battingStyle':^12}` : `{j['battingStyle']:^18}`\n`{'bowlingStyle':^12}` : `{j.get('bowlingStyle' , '-'):^18}`\n`{'country':^12}` : `{j['country']:^18}`\n"
    #               break   
                    
                        
    #     embed = discord.Embed(color= 123456 , title= title , description= data)
    #     embed.set_thumbnail(url = img) 
    #     await ctx.send(embed = embed )
    
    
    @commands.hybrid_command()
    @commands.guild_only()
    # @commands.check(check_channel)
    @cooldown(1, 10, BucketType.user)
    async def score(self , ctx  ): 

        def check_perms(ctx) -> bool:
            return client.data[ctx.guild.id]['manager'] in [role.id for role in ctx.author.roles] or ctx.author.guild_permissions.manage_guild

        def check_channel(ctx) ->bool : 
            return client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0  or ctx.channel.id in client.data[ctx.guild.id]['channels'] 

        if not check_perms(ctx) and not check_channel(ctx) :
          return

        
        dis = ' ' 
        batsman = []
        bowler = [] 
        list1 = []
        
        page = requests.get(url = f"https://www.cricbuzz.com")
        soup = BeautifulSoup(page.content, 'html.parser')
        data  = soup.find('li' , class_ = 'cb-view-all-ga cb-match-card cb-bg-white')
        link = data.find('a').get('href')
        match_id = link.split('/')[2]
        
        page = requests.get(url = f"https://www.cricbuzz.com/live-cricket-scores/{match_id}")
        soup = BeautifulSoup(page.content, 'html.parser')

        score = soup.find('div' , class_ = 'cb-col-100 cb-col cb-col-scores')
        
        try :
          score_divs = score.find_all('div')
          for div in score_divs :
              list1.append(div.get_text().replace('\xa0', '').strip())
          dis = dis + f"{'**' +list1[1].replace(' ', '** ', 1)}\n"
          if len(list1) > 4 :
            dis = dis + f"{'**' +list1[2].replace(' ', '** ', 1)}\n"    
        except : pass

        bord =  soup.find('div' , class_ = 'cb-col-67 cb-col')
        try : 
          divs = bord.find_all('div' )
          status = None
          for div in divs :
            try : 
              if div.get_text() == 'Batter':
                status = True
              if div.get_text() == 'Bowler':
                status = False  
            
              if status is None :
                 continue
              elif status is True : 
                 batsman.append(div.get_text())
              elif status is False : 
                bowler.append(div.get_text())
            except : pass 
          #batter  
          dis = dis + f"\n`{'Batter':^17s}` `{'R':^3s}` `{'B':^3s}` `{'4s':^3s}` `{'6s':^3s}` `{'SR':^6s}`\n"  
          dis = dis + f"\n`{batsman[7]:^17s}` `{batsman[8]:^3s}` `{batsman[9]:^3s}` `{batsman[10]:^3s}` `{batsman[11]:^3s}` `{batsman[12]:^6s}`"  
          try : dis = dis + f"\n`{batsman[14]:^17s}` `{batsman[15]:^3s}` `{batsman[16]:^3s}` `{batsman[17]:^3s}` `{batsman[18]:^3s}` `{batsman[19]:^6s}`"  
          except : pass
          #bowler
          dis = dis + f"\n\n`{'Bowler':^17s}` `{'O':^3s}` `{'M':^3s}` `{'R':^3s}` `{'W':^3s}` `{'ECO':^6s}`\n"  
          dis = dis + f"\n`{bowler[7]:^17s}` `{bowler[8]:^3s}` `{bowler[9]:^3s}` `{bowler[10]:^3s}` `{bowler[11]:^3s}` `{bowler[12]:^6s}`"
          try : dis = dis + f"\n`{bowler[14]:^17s}` `{bowler[15]:^3s}` `{bowler[16]:^3s}` `{bowler[17]:^3s}` `{bowler[18]:^3s}` `{bowler[19]:^6s}`"  
          except : pass 
          
        except : pass      
        
        try :
         rcnt =  soup.find('div' , class_ = 'cb-min-rcnt')
         rcnt_span = rcnt.find_all('span' )
         rcnt_list = []
         for div in rcnt_span :
          rcnt_list.append(div.get_text())
         dis = dis + f"\n\n{rcnt_list[1]}" 
        except : pass
      
        if dis == " ":
          dis = f'Start <t:{data.find("div" , class_ = "cb-ovr-flo cb-mtch-crd-time cb-font-12 cb-text-preview").get("ng-if").split(" ")[0][1:-3]}:R>'
          #cb-ovr-flo cb-mtch-crd-time cb-font-12 cb-text-preview ng-binding ng-scope
          # dis = "match will start soon"
        
        embed = discord.Embed(color= 123456 , title= "Live Score" , description= dis )
        try :embed.set_footer( text =  list1[-2])
        except : pass
        await ctx.send(embed = embed)

    @score.error
    async def pt_error(self , ctx , error ):
        await ctx.send(error)
        
    
    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 10, BucketType.user)
    # async def score(self , ctx  ): 
    #   embed = discord.Embed(color= 123456 , title= "MATCHES" )
    #   page = requests.get(url = "https://www.cricbuzz.com")
    #   soup = BeautifulSoup(page.content, 'html.parser')
    #   ul = soup.find('ul' , class_ = "cb-mtch-crd-rt-itm")
    #   list = ul.find_all('li')
    #   for lis in list :
    #       a = lis.find('a' , recursive=False)
    #       divs = a.find_all('div',recursive=False)
    #       r = []
    #       for div in divs :
    #           for di in div.find_all('div' ,recursive=False):
    #               r.append(di.get_text())
    #       embed

async def setup(client):
   await client.add_cog(Fantasy(client))                       