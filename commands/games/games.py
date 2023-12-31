import discord
from discord.ext import commands 
from database import *
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
import typing


class Games(commands.Cog):

    def __init__(self , client):
        self.client = client
        
# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                            COINflip COMMAND 

    @commands.hybrid_command(aliases=["cf"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(2, 60, BucketType.user)
    async def flip(self , ctx , amount : amountconverter  ,  side : typing.Literal[ 'head', 'tail' , 'h','t','H','T' ] = "head"): 
        user = ctx.author
        _max = client.data[ctx.guild.id]['games']['coinflip']['max'] if client.data[ctx.guild.id]['games'] else defult_games['coinflip']['max']
        _min = client.data[ctx.guild.id]['games']['coinflip']['min'] if client.data[ctx.guild.id]['games'] else defult_games['coinflip']['min']
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = bal["cash"]
                if amount > _max:
                    amount=_max  
            elif amount == "half":
                amount = int(0.5 * bal["cash"])
                if amount > _max:
                    amount=_max        
        if bal is None:
                await open_account( ctx.guild.id , user.id)
                bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        if amount > bal['cash']:
                await ctx.send('You do not have enough money to coinflip that much')
        elif amount <= _min or amount > _max:
                await ctx.send(f'You cannot flip {_min} , less or more then {_max}') 
        else:   
                await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , amount , ctx.author.id , ctx.guild.id) 
                coin_flip = 0.5
                x = random.choices([1,2] , weights = [coin_flip ,(1- coin_flip)])[0]  
                msg = await ctx.send(f"**{ctx.author.mention}** spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe coin flips... <a:coinflip:1007007819490406573>")
                await asyncio.sleep(random.randint(1,4))
                if x == 1:
                  await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , 2*amount , ctx.author.id , ctx.guild.id) 
                  await msg.edit(content= f'**{ctx.author.mention}** spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe coin flips... {coin(ctx.guild.id)} and you Won {coin(ctx.guild.id)} **{amount*2:,}** ')
                else: 
                  await msg.edit(content=f'**{ctx.author.mention}** spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe coin flips... {coin(ctx.guild.id)} and you lost it all... :c ')    
           
    @flip.error
    @commands.guild_only()
    @commands.check(check_channel)
    async def flip_error(self,ctx , error):
        ecoembed = discord.Embed(color= 0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        if isinstance(error, commands.CommandOnCooldown):
            sec = int(error.retry_after)
            min , sec = divmod(sec, 60)
            ecoembed.description = f"⌚ | You cannot flip coin for {min}min {sec}seconds."
            await ctx.send (embed = ecoembed)
            return

#------------------------------------------------xxx---------------------------------------------------------------------------------------------------------------------
#                                            sloth Command


    @commands.hybrid_command(aliases=["st"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 3, BucketType.user)
    async def slot( self , ctx , amount : amountconverter ):
        ecoembed = discord.Embed(color=  0x08FC08)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        
        _max = client.data[ctx.guild.id]['games']['slots']['max'] if client.data[ctx.guild.id]['games'] else defult_games['slots']['max']
        _min = client.data[ctx.guild.id]['games']['slots']['min'] if client.data[ctx.guild.id]['games'] else defult_games['slots']['min']
        
        all = ctx.guild.emojis
        if len(all) < 3 :
            all =  [  *all ,  "😉" , "🙂" , "😐" ]
        emoji = random.choices(all , k=3)        
        first = random.choice(emoji)
        second = random.choice(emoji)
        third = random.choice(emoji)
        outupt = f"{first} | {second} | {third}"
        
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
        
        st_amount = _max
        
        if bal is None:
            await open_account( ctx.guild.id ,ctx.author.id)
            bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , ctx.author.id , ctx.guild.id)
        try:
            amount = int(amount)    
        except ValueError:
            if amount == "all":
                amount = bal["cash"]
                if amount > st_amount:
                    amount=st_amount
            elif amount == "half":
                amount = int(0.5 * bal["cash"])
                if amount > st_amount:
                    amount=st_amount          
        if amount > bal['cash']:
                await ctx.send('You do not have enough money to slots that much')
        elif amount <= _min or amount > st_amount:
                await ctx.send(f'You cannot slot {_min} , less or more then {st_amount}') 
        else :
                if first == second == third:
                    ecoembed.description=f"you won {coin(ctx.guild.id)} {3*amount}\n\n{outupt}" 
                    await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , 2*amount , ctx.author.id , ctx.guild.id) 
                    await ctx.send(embed=ecoembed)
                elif first == second or second  == third:
                    ecoembed.description=f"you won {coin(ctx.guild.id)} {int(1.5*amount)} \n\n{outupt}"
                    await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , (int(0.5*amount)) , ctx.author.id , ctx.guild.id) 
                    await ctx.send(embed=ecoembed)
                else:
                    ecoembed.description=f"you lost {coin(ctx.guild.id)} {amount}\n\n{outupt}" 
                    await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , amount , ctx.author.id , ctx.guild.id) 
                    ecoembed.color =  discord.Color.red()
                    await ctx.send(embed=ecoembed)
                     


#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               roll

    @commands.command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(2, 5, BucketType.user)
    async def roll(self , ctx ,amount : amountconverter ,  rang:typing.Literal["odd" , "even" , 1 , 2 , 3 ,4, 5, 6] = "even"):
        ecoembed = discord.Embed(color= discord.Color.green())
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        
        _max = client.data[ctx.guild.id]['games']['roll']['max'] if client.data[ctx.guild.id]['games'] else defult_games['roll']['max']
        _min = client.data[ctx.guild.id]['games']['roll']['min'] if client.data[ctx.guild.id]['games'] else defult_games['roll']['min']
        
        user = ctx.author
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        try:
            amount = int(amount)
        except ValueError:
            if amount == "all":
                amount = bal["cash"]
                if amount > _max:
                    amount=_max  
            elif amount == "half":
                amount = int(0.5 * bal["cash"])
                if amount > _max:
                    amount=_max     
        if bal is None:
                await open_account( ctx.guild.id , user.id)
                bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        if amount > bal['cash']:
                await ctx.send('You do not have enough money to roll that much')
        elif amount <= _min or amount > _max:
                await ctx.send(f'You cannot roll {_min} , less or more then {_max}') 
        else:
            x = random.randint(1, 6)
            if rang == "even" and x in [2,4,6]:
                await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You win {coin(ctx.guild.id)} {2 * amount :,}\n:game_die: You rolled **{x}**"
                await ctx.send(embed = ecoembed)
            elif rang == "odd" and x in [1,3,5]:    
                await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You win {coin(ctx.guild.id)} {2 * amount :,}\n:game_die: You rolled **{x}**"
                await ctx.send(embed = ecoembed)
            elif rang in [1,2,3,4,5,6] and x == rang :
                await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , 4*amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You win {coin(ctx.guild.id)} {5 * amount :,}\n:game_die: You rolled **{x}**"
                await ctx.send(embed = ecoembed)
            else:
                await self.client.db.execute('UPDATE users SET cash = cash - $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You lose {coin(ctx.guild.id)}{amount: ,}\n:game_die: You rolled **{x}**"
                ecoembed.color = discord.Color.red()
                await ctx.send(embed = ecoembed)


async def setup(client):
   await client.add_cog(Games(client))                       