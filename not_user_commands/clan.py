import discord
from discord.ext import commands
from database import *
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
import math
import typing
from discord.ui import Button , View
from datetime import datetime
from pm2py import PM2
import openai



class Clan(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.role = ["Leader"]

    async def check_channel(ctx) ->bool : 
        return ctx.channel.id in channel

    async def open_account(self , guild_id : int , id : int):
            newuser = {"id": id, "cash": 0 , "bank" : 1000 , "pvc" : 0 , "pet" : None}
            coll = db[f"{guild_id}"]
            await coll.insert_one(newuser)

    async def get_clan_embed(self , guild_id , clan_id): 
        coll = db[f"{guild_id}"]
        clan = await coll.find_one({"category" : "clan" , "clan_id" : clan_id})
        if clan is None :
            return None

        embed = discord.Embed(color=discord.Color.blue() ,  )
        embed.set_author(name = clan['clan_name'] , icon_url= "https://cdn.discordapp.com/attachments/999186452757872701/1059536339336441866/1007213-200.png")
        embed.set_thumbnail(url = clan["clan_icon"])

        guild = self.client.get_guild(guild_id)

        online = 0
        total_bank = 0
        i = 1
        temp = " "
        for data in clan["members"]:
            member = guild.get_member(data['id'])
            
            if data["role"] is None :
                role = " "
            else :
                role = f"({self.role[data['role']]})"    
            temp = temp + f"**{i}**. {member} {role}\n"
            bal = await coll.find_one({"id" : member.id})
            total_bank = total_bank + bal["bank"]
            if member.status is not discord.Status.offline:
                online = online + 1 
            i = i + 1 
        await coll.update_one(clan , {"$set" : { "clan_bank" : total_bank } })
        embed.description = f"**Clan Members**<:inv:1009518335416881182><:inv:1009518335416881182><:inv:1009518335416881182>🟢 _{online}_**/**_{i-1}_\n\n{temp}<:inv:1009518335416881182><:inv:1009518335416881182>" 
        embed.add_field(name= "Clan bank" , value = f"{coin1} {total_bank:,}")  
        embed.add_field(name= "Clan Description" , value= clan["description"] , inline=False) 
        embed.set_footer(text = f"id - {clan['clan_id']} ,XP ,Roles ,Level, Wars Coming soon") 
        return embed

    async def get_user_clan(self , guild_id , user_id ):
        coll = db[f"{guild_id}"]
        bal = await coll.find_one({"id": user_id})

        try :
            clan_id = bal["clan_id"]
        except KeyError :
            await coll.update_one({"id": user_id} , {"$set" : { "clan_id" : None  }})
            clan_id = None
        if clan_id == None :
            clan = None 
        else : 
            clan = await coll.find_one({"category" : "clan" , "clan_id" : clan_id}) 
        return clan 


#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               CLAN 

    # @commands.hybrid_command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 5, BucketType.user)
    # async def clan(self , ctx , user : typing.Optional[discord.Member] = None , clan : typing.Optional[str] = None ):
    #     coll = db[f"{ctx.guild.id}"]
    #     user = user or ctx.author
    #     if clan is None :
    #         clan = await self.get_user_clan(ctx.guild.id, user.id)
    #         if clan is None :
    #             await ctx.send(f"{user} is not in a clan")
    #             return
    #         else:
    #             embed = await self.get_clan_embed( ctx.guild.id , clan["clan_id"])
    #             await ctx.send(embed = embed)
    #             return

    # @commands.hybrid_command(aliases=["create-clan"])
    # @commands.guild_only()
    # @commands.has_permissions(administrator =True)
    # @cooldown(1, 5, BucketType.user)
    # async def createclan(self , ctx , clan_name : str , description : str , clan_icon : typing.Optional[str] ):
    #     coll = db[f"{ctx.guild.id}"]
    #     clan = await self.get_user_clan(ctx.guild.id, ctx.author.id)

    #     if clan is not None :
    #         await ctx.send("you are already in a clan")
    #         return

    #     y= True
    #     while y  :
    #         x = random.randint(0, 1000)
    #         clan = await coll.find_one({"category" : "clan" , "clan_id" : x})
    #         if clan is None:
    #             y = False
    #     await coll.insert_one({"category" : "clan" , "clan_id" : x , "clan_name" : clan_name[:25] , "leader" : ctx.author.id , "clan_icon" : clan_icon , "members" : [{"id" : ctx.author.id , "role" : 0 }] , "description" : description[:200]})
    #     await coll.update_one({"id" : ctx.author.id} , {"$set" : {"clan_id" : x}})
    #     await ctx.send("Done")

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_permissions(administrator =True)
    async def pm2list(self , ctx ):
        pm2 = PM2()
        dis = " "
        embed = discord.Embed()
        for i in pm2.list():
            embed.add_field(name= f"{i.name}" , value= f"**pid : **{i.pid}\n**pm_id :** {i.pm_id}\n**monit : **\n----**memory : **{int(((i.monit['memory'])/1024)/1024)}mb\n----**cpu : **{i.monit['cpu']}%\n**autorestart : **{i.autorestart}\n**version : **{i.version}\n**mode : **{i.mode}\n**uptime : **<t:{int(datetime.now().timestamp() - i.uptime)}:R>\n**created_at :** <t:{i.created_at}:R>\n**restart : **{i.restart}\n**status :** {i.status}\n**user : **{i.user}\n\n")

        await ctx.send(embed = embed)

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.is_owner()
    async def pm2stop(self , ctx , name : str ):
        pm2 = PM2()
        x= pm2.stop(name)
        await ctx.send(f"{x} done")
    
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.is_owner()
    async def pm2start(self , ctx , name : str ):
        pm2 = PM2()
        x= pm2.start(name)
        await ctx.send(f"{x} done")
    
    @commands.hybrid_command()
    @commands.guild_only()
    @commands.is_owner()
    async def pm2restart(self , ctx , name : str ):
        pm2 = PM2()
        x= pm2.restart(name)
        await ctx.send(f"{x} done")


    @pm2list.error
    async def error_clan(self ,ctx , error ):
        await ctx.send(error)
    # @clan.error
    # async def error_clan(self ,ctx , error ):
    #     await ctx.send(error)
        # try :
        #     clan = int(clan)
        # except :
        #     pass

        # if clan is int :

    # ai_cooldown = commands.CooldownMapping.from_cooldown(1.0, 60.0, commands.BucketType.user)    
    # @commands.Cog.listener()
    # async def on_message(self , message):
    #   if message.author.bot :
    #     return
    #   if message.channel.id == 966022735333572647 :
    #     bucket = self.ai_cooldown.get_bucket(message)
    #     retry_after = bucket.update_rate_limit()  
    #     if not retry_after:
    #         await message.channel.typing()
    #         openai.api_key = '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'
    #         prompt = message.content
    #         response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=64 ,  organization= "org-YRkuHtofli59Agv3PwEedDxb" )
    #         if response.choices[0].text.find("@here") != -1 or response.choices[0].text.startswith("!"):
    #             return

    #         await message.reply(response.choices[0].text , allowed_mentions = discord.AllowedMentions(everyone= False , roles=False , users= False) )




    @commands.hybrid_command()
    @commands.guild_only()
    @cooldown(1, 20 , BucketType.user)
    async def ask(self , ctx , * , message ):
        # if (ctx.channel.id != 966022735333572647) or (ctx.channel.id != 1081275128224161792) :
        #     await ctx.reply("not there")
        #     return
        if ctx.channel.id == 966022735333572647 :
            pass 
        elif ctx.channel.id == 1081275128224161792 :
            pass
        else :
            return
        
        await ctx.channel.typing()
        openai.api_key = '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'
        prompt = message
        response = openai.Completion.create(engine="text-davinci-003", prompt=prompt, max_tokens=64 )

        if response.choices[0].text.find("@here") != -1 or response.choices[0].text.startswith("!"):
            return

        await ctx.reply(response.choices[0].text , allowed_mentions = discord.AllowedMentions(everyone= False , roles=False , users= False) )

    @ask.error
    async def error_clan(self ,ctx , error ):
        await ctx.reply(error)

async def setup(client):
   await client.add_cog(Clan(client))                       