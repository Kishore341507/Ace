import discord
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown
import time 
from database import client
from utils import bembed, open_account, pvc_coin, coin, check_channel

class income(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.income_cooldown = { }

    @commands.hybrid_command(aliases=["collect-income" , "income"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1,5 , BucketType.member)     
    async def collect(self , ctx ):
        ecoembed = discord.Embed(color= discord.Color.blue())
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)
        dis = "✅ Role income successfully collected!\n\n"   
        docs = await client.db.fetch('SELECT role_id ,bank , cash , pvc , cooldown FROM  income WHERE guild_id = $1 ORDER BY cash DESC' , ctx.guild.id)        
        bal = await self.client.cache.get_user(ctx.guild.id, ctx.author.id)
        
        bank = ""
        cash = ""
        pvc = ""
        bank_add = 0
        cash_add = 0 
        pvc_add = 0        
        self.income_cooldown.setdefault(ctx.guild.id , { }).setdefault( ctx.author.id , { } )
        for x in docs:
            if ctx.guild.get_role(x["role_id"]) in ctx.author.roles and time.time() > self.income_cooldown.get(ctx.guild.id,{}).get(ctx.author.id,{}).get(x['role_id'],0) :
                if x['bank'] != 0 :
                    bank_add += x['bank']
                    bank += f"{ctx.guild.get_role(x['role_id']).mention} | {coin(ctx.guild.id)} {x['bank']:,} bank\n"                
                if x['cash'] != 0 :
                    cash_add += x['cash']
                    cash += f"{ctx.guild.get_role(x['role_id']).mention} | {coin(ctx.guild.id)} {x['cash']:,} cash\n"
                if client.data[ctx.guild.id]['pvc'] and x['pvc'] != 0 :
                    pvc_add += x['pvc']
                    pvc += f"{ctx.guild.get_role(x['role_id']).mention} | {pvc_coin(ctx.guild.id)[0]} {x['pvc']:,} {pvc_coin(ctx.guild.id)[1]}\n"                  
                self.income_cooldown[ctx.guild.id][ctx.author.id][x['role_id']] = time.time() + x['cooldown']
        if bank_add + cash_add + pvc_add != 0 :
            await self.client.cache.increment_user_balance(ctx.guild.id, ctx.author.id, cash=cash_add, bank=bank_add, pvc=pvc_add)
        
        output = "🤷🏾‍♂️ But Nothing To Collect"
        
        collects_to_remove = []
        if len(self.income_cooldown.get(ctx.guild.id,{}).get(ctx.author.id,{}) ) != 0:
            for c in self.income_cooldown[ctx.guild.id][ctx.author.id] :
                if self.income_cooldown[ctx.guild.id][ctx.author.id][c] < time.time( ):
                    collects_to_remove.append(c)
            for c in collects_to_remove:
                del self.income_cooldown[ctx.guild.id][ctx.author.id][c]
            output = f"Next Collect Will Be <t:{int(min(self.income_cooldown.get(ctx.guild.id,{}).get(ctx.author.id,{}).values()))}:R>"
        ecoembed.description = dis + ( (f"{bank}\n{cash}\n{pvc}") if cash + bank + pvc != "" else output )
        await ctx.send(embed = ecoembed) 

    @collect.error
    async def collect_error(self ,ctx ,error):
        if isinstance(error, commands.CommandOnCooldown):
            sec = int(error.retry_after)
            min , sec = divmod(sec, 60)
            await ctx.send (embed = discord.Embed( description= f"⌚ | command on cooldown for {min}min {sec}seconds." ))
        # else :
        #     await ctx.send (embed = discord.Embed( description= error ))
             

async def setup(client):
   await client.add_cog(income(client))         
