import discord
from discord.ext import commands
from database import *
from discord.ext.commands import BucketType, cooldown
import time 

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
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        if bal is None:
            await open_account(ctx.guild.id, ctx.author.id)
            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        
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
            await client.db.execute("UPDATE users SET bank = bank + $1 , cash = cash + $2 , pvc = pvc + $3 WHERE id = $4 AND guild_id = $5", bank_add , cash_add , pvc_add , ctx.author.id, ctx.guild.id)
        
        output = "🤷🏾‍♂️ But Nothing To Collect"
        
        if len(self.income_cooldown.get(ctx.guild.id,{}).get(ctx.author.id,{}) ) != 0  :
            for c in self.income_cooldown[ctx.guild.id][ctx.author.id] :
                if self.income_cooldown[ctx.guild.id][ctx.author.id][c] < time.time( ) :
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
