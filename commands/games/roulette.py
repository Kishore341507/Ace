import discord
from discord.ext import commands
from database import *
import random
from discord.ext.commands import BucketType, cooldown
import typing
import asyncio
from discord import app_commands

class roulette_space(commands.Converter):
    async def convert(self , ctx , argument):
        try : 
            argument = int(argument)
        except :
            pass    
        if argument not in ["odd" , "even","red" , "black","1-18" , "19-36","1st", "2nd", "3rd","1-12" , "13-24" , "25-36",0, 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36]:
            raise commands.BadArgument("Invalid space to bet upon.") 
        else :
            return argument         


class Roulette(commands.Cog):

    def __init__(self , client ):
        self.client = client
        self.game = [{'number' : 0, 'colour' : ''}, {'number': 1, 'colour': 'red'}, {'number': 2, 'colour': 'black'}, {'number': 3, 'colour': 'red'}, {'number': 4, 'colour': 'black'}, {'number': 5, 'colour': 'red'}, {'number': 6, 'colour': 'black'}, {'number': 7, 'colour': 'red'}, {'number': 8, 'colour': 'black'}, {'number': 9, 'colour': 'red'}, {'number': 10, 'colour': 'black'}, {'number': 11, 'colour': 'black'}, {'number': 12, 'colour': 'red'}, {'number': 13, 'colour': 'black'}, {'number': 14, 'colour': 'red'}, {'number': 15, 'colour': 'black'}, {'number': 16, 'colour': 'red'}, {'number': 17, 'colour': 'black'}, {'number': 18, 'colour': 'red'}, {'number': 19, 'colour': 'red'}, {'number': 20, 'colour': 'black'}, {'number': 21, 'colour': 'red'}, {'number': 22, 'colour': 'black'}, {'number': 23, 'colour': 'red'}, {'number': 24, 'colour': 'black'}, {'number': 25, 'colour':'red'}, {'number': 26, 'colour': 'black'}, {'number': 27, 'colour': 'red'}, {'number': 28, 'colour': 'black'}, {'number': 29, 'colour': 'black'}, {'number': 30, 'colour': 'red'}, {'number': 31, 'colour': 'black'}, {'number': 32, 'colour': 'red'}, {'number': 33, 'colour': 'black'}, {'number': 34, 'colour': 'red'}, {'number': 35, 'colour': 'black'}, {'number': 36, 'colour': 'red'}]
        self.players = []

    async def check_channel(ctx) -> bool:
        return client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0 or ctx.channel.id in client.data[ctx.guild.id]['channels']

    def roulette_result( self , result , user) -> int: 
        if result["number"] != 0 and user["space"] == "odd" and result["number"] % 2 != 0 :
            return 2
        elif result["number"] != 0 and user["space"] == "even" and result["number"] % 2 == 0 : 
            return 2
        elif (user["space"] == "red") and (result["colour"]  == "red") :
            return 2
        elif user["space"] == "black" and result["colour"]  == "black" :
            return 2
        elif user["space"] == "1-18" and result["number"] in range(1,19):
            return 2 
        elif user["space"] == "19-36" and result["number"] in range(19,37):
            return 2
        elif user["space"] == "1st" and result["number"] in [1,4,7,10,13,16,19,22,25,28,31,34]:
            return 3
        elif user["space"] == "2nd" and result["number"] in [2,5,8,11,14,17,20,23,26,29,32,35]:
            return 3
        elif user["space"] == "3rd" and result["number"] in [3,6,9,12,15,18,21,24,27,30,33,36]:
            return 3
        elif user["space"] == "1-12" and result["number"] in range(1,13):
            return 3
        elif user["space"] == "13-24" and result["number"] in range(13,25):
            return 3
        elif user["space"] == "13-24" and result["number"] in range(13,25):
            return 3
        elif user["space"] == "25-36" and result["number"] in range(25,37):
            return 3
        elif user["space"] in range(0,37) and result["number"] == user["space"] :
            return 36
        else :
            return 0 


    roulette_cooldown = commands.CooldownMapping.from_cooldown(1.0, 30.0, commands.BucketType.channel)
    """
    , description="Spin the roulette wheel and gamble on a given space.", 
    help="Valid spaces include 1st, 2nd, 3rd, 1-12, 13-24, 25-36, 1-18, 19-36 and all numbers from range 0 to 36.", usage = "<amount> [space]")
    """
    @commands.hybrid_command(aliases=["r"]) 
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(10, 30, BucketType.user)
    async def roulette(self , ctx  , amount : amountconverter , space : roulette_space = "random" ):
        flag = True
        if space == "random":
            space = random.randint(0, 37)
            
        _max = client.data[ctx.guild.id]['games']['roulette']['max'] if client.data[ctx.guild.id]['games'] else defult_games['roulette']['max']
        _min = client.data[ctx.guild.id]['games']['roulette']['min'] if client.data[ctx.guild.id]['games'] else defult_games['roulette']['min']       

        game_limit = _max
        
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', ctx.author.id, ctx.guild.id)
        if bal is None:
            await open_account( ctx.guild.id , user.id)
            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        if amount == "all":
            amount = bal['cash']
        elif amount == "half":
            amount = int(bal['cash'] * 0.5)
        else:
            amount = int(amount)

        if amount > game_limit:
            amount = game_limit
        
        total_bet_amount = 0
        for user in self.players:
            if user['user_id'] == ctx.author.id and user['guild'] == ctx.guild.id :
                total_bet_amount += user['amount']
        if total_bet_amount < game_limit:
            more_to_bet  = game_limit - total_bet_amount
            if amount > more_to_bet:
                amount = more_to_bet
        else:
            return await ctx.send(embed=bembed(f'You already bet the max amount i.e {coin(ctx.guild.id)} {game_limit:,}', discord.Color.brand_red())) 

        if amount > bal['cash']:
            return await ctx.send(embed=bembed(f'You do not have enough money to roulette that much', discord.Color.brand_red())) 
        elif amount <= _min:
            return await ctx.send(embed=bembed(f'You cannot roulette {_min} or less', discord.Color.brand_red()))
        
        bucket = self.roulette_cooldown.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after is None :
                flag = False
                retry_after = 30 
        
        embed = discord.Embed(color=discord.Color.blue() , description= f"You have placed a bet of {coin(ctx.guild.id)} {amount} on `{space}`.")
        embed.set_author(name= ctx.author , icon_url= ctx.author.display_avatar)
        embed.set_footer(text= f"Time remaining: {int(retry_after)} seconds {'| if bet place after result , it will count in next result' if int(retry_after) == 0 else '' }")        
        self.players.append({"guild" : ctx.guild.id  , "channel" : ctx.channel.id , "user_id" : ctx.author.id , "amount" : int(amount) , "space" : space })
        await client.db.execute("UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3", amount, ctx.author.id, ctx.guild.id)

        await ctx.send(embed = embed)

        if flag : 
            return

        await asyncio.sleep(retry_after)
        result = random.choice(self.game)
        win_msg = f"The ball landed on: **{result['colour']} {result['number']}**!\n\n"
        dis = "**Winners:**"
        
        utsav = []
        for user in self.players:
            if user["guild"] == ctx.guild.id and user["channel"] == ctx.channel.id :
                x = ctx.guild.get_member(user['user_id'])
                multi = self.roulette_result(result ,user)
                if multi != 0 :
                    await client.db.execute("UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3", (multi*user['amount']), x.id , ctx.guild.id)
                    # await coll.update_one({"id": x.id} , {"$inc" : {"cash": + (multi*user['amount']) , "gambler" : + int((multi*user['amount'])/100) }})
                    dis = dis + f"\n{x.mention} won {coin(ctx.guild.id)} {multi * user['amount']}"

                utsav.append(user)

        for i in utsav :
            if i in self.players:
                self.players.remove(i)

        if dis == "**Winners:**":
            dis = "**No Winners  :(**"
        await ctx.send(win_msg + dis)

    @roulette.autocomplete('space')
    async def roulette_auto( self, ctx  , current : str )-> list[app_commands.Choice[str]]:
        lis = ["odd" , "even","red" , "black","1-18" , "19-36","1st", "2nd", "3rd","1-12" , "13-24" , "25-36" ]
        return [
        app_commands.Choice(name=space, value=space)
        for space in lis if current.lower() in space.lower()
        ]

    @roulette.error
    async def bj_error(self ,ctx ,error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(color=discord.Color.blue() , description= f"You are on cooldown try after {int(ctx.command.get_cooldown_retry_after(ctx)) } seconds")
            embed.set_author(name= ctx.author , icon_url= ctx.author.display_avatar)
            await ctx.send(embed = embed)
        else:
            return

async def setup(client):
   await client.add_cog(Roulette(client))        