import discord
from discord.ext import commands
import asyncio
from discord.ext.commands import BucketType, cooldown
import random
import typing
from database import client
from utils import bembed, coin, open_account, default_games, check_channel, amountconverter


class Games(commands.Cog):

    def __init__(self , client):
        self.client = client
        
# ------------------------------------------------xxx--------------------------------------------------------------------------------
#                                            COINflip COMMAND 

    @commands.hybrid_command(aliases=["cf" , "dk"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 6, BucketType.member)
    async def ddakji(self , ctx , amount : amountconverter  ,  side : typing.Literal[ 'blue', 'red' , 'b','r' ] = "blue"):
        user = ctx.author
        _max = client.data[ctx.guild.id]['games']['coinflip']['max'] if client.data[ctx.guild.id]['games'] else default_games['coinflip']['max']
        _min = client.data[ctx.guild.id]['games']['coinflip']['min'] if client.data[ctx.guild.id]['games'] else default_games['coinflip']['min']
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
        if amount > bal['cash']:
                await ctx.send('You do not have enough money')
        elif amount <= _min or amount > _max:
                await ctx.send(f'You cannot bet {_min} , less or more then {_max}') 
        else:
                embed = bembed(f"You spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe ddakji flips... <a:coinflip:1205817149612884028>")
                await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , amount , ctx.author.id , ctx.guild.id) 
                result = random.choice(['blue','red'])
                # result_side = "<:tickapCoin:1191976654042570792>"
                result_side = "🟦" if result == "blue" else "🟥"
                msg = await ctx.send(content = ctx.author.mention, embed=embed)
                await asyncio.sleep(random.randint(1,4))
                if result == side:
                  await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , 2*amount , ctx.author.id , ctx.guild.id)
                  embed.description = f"You spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe ddakji flips... {result_side} and you Won {coin(ctx.guild.id)} **{amount*2:,}**"
                  embed.color = discord.Color.brand_green()
                  await msg.edit(embed=embed)
                else: 
                  embed.description = f"You spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe ddakji flips... {result_side} and you lost it all... :c"
                  embed.color = discord.Color.brand_red()
                  await msg.edit(embed=embed)
           
    @ddakji.error
    @commands.guild_only()
    @commands.check(check_channel)
    async def flip_error(self,ctx , error):
        ecoembed = discord.Embed(color= 0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)
        if isinstance(error, commands.CommandOnCooldown):
            sec = int(error.retry_after)
            min , sec = divmod(sec, 60)
            ecoembed.description = f"⌚ | You cannot flip coin for {min}min {sec}seconds."
            await ctx.send (embed = ecoembed)
            return

    # @commands.hybrid_command(aliases=["cf"])
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(1, 6, BucketType.member)
    # async def flip(self , ctx , amount : amountconverter  ,  side : typing.Literal[ 'head', 'tail' , 'h','t' ] = "head"):
    #     user = ctx.author
    #     _max = client.data[ctx.guild.id]['games']['coinflip']['max'] if client.data[ctx.guild.id]['games'] else default_games['coinflip']['max']
    #     _min = client.data[ctx.guild.id]['games']['coinflip']['min'] if client.data[ctx.guild.id]['games'] else default_games['coinflip']['min']
    #     bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
    #     try:
    #         amount = int(amount)
    #     except ValueError:
    #         if amount == "all":
    #             amount = bal["cash"]
    #             if amount > _max:
    #                 amount=_max  
    #         elif amount == "half":
    #             amount = int(0.5 * bal["cash"])
    #             if amount > _max:
    #                 amount=_max        
    #     if amount > bal['cash']:
    #             await ctx.send('You do not have enough money to coinflip that much')
    #     elif amount <= _min or amount > _max:
    #             await ctx.send(f'You cannot flip {_min} , less or more then {_max}') 
    #     else:
    #             embed = bembed(f"You spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe coin flips... <a:coinflip:1205817149612884028>")
    #             await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , amount , ctx.author.id , ctx.guild.id) 
    #             result = random.choice(['head','tail'])
    #             result_side = "<:tickapCoin:1191976654042570792>"
    #             msg = await ctx.send(content = ctx.author.mention, embed=embed)
    #             await asyncio.sleep(random.randint(1,4))
    #             if result == side:
    #               await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , 2*amount , ctx.author.id , ctx.guild.id)
    #               embed.description = f"You spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe coin flips... {result_side} and you Won {coin(ctx.guild.id)} **{amount*2:,}**"
    #               embed.color = discord.Color.brand_green()
    #               await msg.edit(embed=embed)
    #             else: 
    #               embed.description = f"You spent {coin(ctx.guild.id)} **{amount:,}** and chose **{side}**\nThe coin flips... {result_side} and you lost it all... :c"
    #               embed.color = discord.Color.brand_red()
    #               await msg.edit(embed=embed)
           
    # @flip.error
    # @commands.guild_only()
    # @commands.check(check_channel)
    # async def flip_error(self,ctx , error):
    #     ecoembed = discord.Embed(color= 0xF90651)
    #     ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)
    #     if isinstance(error, commands.CommandOnCooldown):
    #         sec = int(error.retry_after)
    #         min , sec = divmod(sec, 60)
    #         ecoembed.description = f"⌚ | You cannot flip coin for {min}min {sec}seconds."
    #         await ctx.send (embed = ecoembed)
    #         return    

#------------------------------------------------xxx---------------------------------------------------------------------------------------------------------------------
#                                            sloth Command


    @commands.hybrid_command(aliases=["st"])
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(1, 6, BucketType.member)
    async def slot( self , ctx , amount : amountconverter ):
        ecoembed = discord.Embed(color=  0x08FC08)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)
        
        _max = client.data[ctx.guild.id]['games']['slots']['max'] if client.data[ctx.guild.id]['games'] else default_games['slots']['max']
        _min = client.data[ctx.guild.id]['games']['slots']['min'] if client.data[ctx.guild.id]['games'] else default_games['slots']['min']
        
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
                    ecoembed.description=f"You won {coin(ctx.guild.id)} {3*amount}\n\n{outupt}" 
                    await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , 2*amount , ctx.author.id , ctx.guild.id) 
                    ecoembed.color =  discord.Color.brand_green()
                    await ctx.send(embed=ecoembed)
                elif first == second or second  == third:
                    ecoembed.description=f"You won {coin(ctx.guild.id)} {int(1.5*amount)} \n\n{outupt}"
                    await self.client.db.execute('UPDATE users SET cash = cash + $1 WHERE id = $2 AND guild_id = $3' , (int(0.5*amount)) , ctx.author.id , ctx.guild.id) 
                    ecoembed.color =  discord.Color.brand_green()
                    await ctx.send(embed=ecoembed)
                else:
                    ecoembed.description=f"You lost {coin(ctx.guild.id)} {amount}\n\n{outupt}" 
                    await self.client.db.execute('UPDATE users SET cash = cash - $1 WHERE id = $2 AND guild_id = $3' , amount , ctx.author.id , ctx.guild.id) 
                    ecoembed.color =  discord.Color.brand_red()
                    await ctx.send(embed=ecoembed)
    
    @slot.error
    @commands.guild_only()
    @commands.check(check_channel)
    async def slot_error(self,ctx , error):
        ecoembed = discord.Embed(color= 0xF90651)
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar.url)
        if isinstance(error, commands.CommandOnCooldown):
            sec = int(error.retry_after)
            ecoembed.description = f"⌚ | You are on cooldown try again in {sec}seconds."
            await ctx.send (embed = ecoembed)
            return


#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               roll

    @commands.command()
    @commands.guild_only()
    @commands.check(check_channel)
    @cooldown(2, 5, BucketType.user)
    async def rps(self , ctx ,amount : amountconverter ,  rang:typing.Literal['rock' , 'paper' , 'scissor' , 'r' , 'p' , 'c'] = None):
        if rang == "r" or rang == "rock":
            rang = "🪨"
        elif rang == "p" or rang == "paper":
            rang = "📃"
        elif rang == "c" or rang == "scissor":
            rang = "✂️"
        else :
            rang =  random.choice(["🪨" , "📃" , "✂️"])

        ecoembed = discord.Embed(color= discord.Color.green())
        ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)
        
        _max = client.data[ctx.guild.id]['games']['roll']['max'] if client.data[ctx.guild.id]['games'] else default_games['roll']['max']
        _min = client.data[ctx.guild.id]['games']['roll']['min'] if client.data[ctx.guild.id]['games'] else default_games['roll']['min']
        
        user = ctx.author
        bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
        # bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
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
                await ctx.send('You do not have enough money')
        elif amount <= _min or amount > _max:
                await ctx.send(f'You cannot bet {_min} , less or more then {_max}') 
        else:
            # x = random.randint(1, 6)
            #  select a random from 🪨 , 📃 and ✂️
            x = random.choice(["🪨" , "📃" , "✂️"])
            if x == rang:
                # await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f'It\'s a tie! You both chose {x} \nYou get your money back'
                await ctx.send(embed = ecoembed)
            elif (x == "🪨" and rang == "📃") or (x == "📃" and rang == "✂️") or (x == "✂️" and rang == "🪨"): 
                await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You win {coin(ctx.guild.id)} {2 * amount :,}\nYou chose **{rang}** and I chose **{x}**"
                await ctx.send(embed = ecoembed)
            else:
                await self.client.db.execute('UPDATE users SET cash = cash - $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
                ecoembed.description= f"You lose {coin(ctx.guild.id)}{amount: ,}\nYou chose **{rang}** and I chose **{x}**"
                ecoembed.color = discord.Color.red()
                await ctx.send(embed = ecoembed)

    # @commands.command()
    # @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(2, 5, BucketType.user)
    # async def roll(self , ctx ,amount : amountconverter ,  rang:typing.Literal["odd" , "even" , 1 , 2 , 3 ,4, 5, 6] = "even"):
    #     ecoembed = discord.Embed(color= discord.Color.green())
    #     ecoembed.set_author(name = ctx.author , icon_url= ctx.author.display_avatar)
        
    #     _max = client.data[ctx.guild.id]['games']['roll']['max'] if client.data[ctx.guild.id]['games'] else default_games['roll']['max']
    #     _min = client.data[ctx.guild.id]['games']['roll']['min'] if client.data[ctx.guild.id]['games'] else default_games['roll']['min']
        
    #     user = ctx.author
    #     bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
    #     bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
    #     try:
    #         amount = int(amount)
    #     except ValueError:
    #         if amount == "all":
    #             amount = bal["cash"]
    #             if amount > _max:
    #                 amount=_max  
    #         elif amount == "half":
    #             amount = int(0.5 * bal["cash"])
    #             if amount > _max:
    #                 amount=_max     
    #     if bal is None:
    #             await open_account( ctx.guild.id , user.id)
    #             bal = await self.client.db.fetchrow('SELECT * FROM users WHERE id = $1 AND guild_id = $2 ' , user.id , ctx.guild.id)
    #     if amount > bal['cash']:
    #             await ctx.send('You do not have enough money to roll that much')
    #     elif amount <= _min or amount > _max:
    #             await ctx.send(f'You cannot roll {_min} , less or more then {_max}') 
    #     else:
    #         x = random.randint(1, 6)
    #         if rang == "even" and x in [2,4,6]:
    #             await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
    #             ecoembed.description= f"You win {coin(ctx.guild.id)} {2 * amount :,}\n:game_die: You rolled **{x}**"
    #             await ctx.send(embed = ecoembed)
    #         elif rang == "odd" and x in [1,3,5]:    
    #             await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
    #             ecoembed.description= f"You win {coin(ctx.guild.id)} {2 * amount :,}\n:game_die: You rolled **{x}**"
    #             await ctx.send(embed = ecoembed)
    #         elif rang in [1,2,3,4,5,6] and x == rang :
    #             await self.client.db.execute('UPDATE users SET cash = cash + $1  WHERE id = $2 AND guild_id = $3'  , 4*amount ,  ctx.author.id , ctx.guild.id) 
    #             ecoembed.description= f"You win {coin(ctx.guild.id)} {5 * amount :,}\n:game_die: You rolled **{x}**"
    #             await ctx.send(embed = ecoembed)
    #         else:
    #             await self.client.db.execute('UPDATE users SET cash = cash - $1  WHERE id = $2 AND guild_id = $3'  , amount ,  ctx.author.id , ctx.guild.id) 
    #             ecoembed.description= f"You lose {coin(ctx.guild.id)}{amount: ,}\n:game_die: You rolled **{x}**"
    #             ecoembed.color = discord.Color.red()
    #             await ctx.send(embed = ecoembed)
    
    @commands.hybrid_command(aliases=["gtn"])
    @commands.guild_only()
    # @commands.check(check_channel)
    # @cooldown(2, 5, BucketType.user)
    @commands.has_permissions(manage_guild = True)
    async def guessthenumber(self , ctx , number : int  , * , message : str = "Start guessing!"):
        '''
        
        '''

        if ctx.interaction:
            await ctx.defer(ephermal = True)
            await ctx.send("The game started")
        else:
            await ctx.message.delete()

        await ctx.channel.set_permissions(ctx.guild.default_role , send_messages = True)
        embed = discord.Embed(description = message , color= 0x2b2c31)
        msg0  = await ctx.send(embed = embed)
        await msg0.pin()

        def check(m):
            return m.content == str(number) and m.channel == ctx.channel

        msg = await self.client.wait_for('message', check=check)

        embed = discord.Embed(description = f"Congratulation {msg.author.mention}! You guessed the number **{number}**" , color= 0x2b2c31)
        await msg.reply(embed = embed)
        await msg.pin()

        # remove send message perms from everyone 
        await ctx.channel.set_permissions(ctx.guild.default_role , send_messages = False)

    @guessthenumber.error
    async def guessthenumber_error(self , ctx , error):
        print(error)


async def setup(client):
   await client.add_cog(Games(client))                       