import discord
from discord.ext import commands, tasks
from pytz import timezone
from discord.ext.commands import BucketType, cooldown
import math
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
import io
from database import client
from utils import bembed, open_account, coin, check_channel, check_perms

class MarketInfo(discord.ui.View) :

    def __init__(self):
      super().__init__(timeout=None)
    
    @discord.ui.button(label='Info', emoji='📈' , custom_id="market:info")
    async def info(self, interaction: discord.Interaction , button: discord.ui.Button):
      embed = bembed()
      embed.title = "Market Info"
      embed.description = "# What's Market?\nThe Market is like a virtual store for trading. It adds a fun strategy to the game, letting players make smart choices based on how the in-game money changes.\n# How it Works?\nThe Market is connected to how much total economy there is in the game and how many stocks are available. When there's less economy in the game, stock prices drop, so it's a good time to buy. When players win at the casino games, the total economy goes up, and it's a good time to sell stocks to make a profit. Players can trade stocks by deciding when to buy low and sell high. It's like a cool store where players use their smarts to make more in-game money, going beyond the usual casino games."
      
      await interaction.response.send_message( embed=embed, ephemeral=True)
    

async def amountConverterMarket(user_id: int, guild_id: int, argument: str, type: str, total_shares=0):

  docs = await client.db.fetchrow("SELECT SUM(cash + bank) as economy , SUM(stocks) as stocks FROM users WHERE guild_id = $1;",guild_id)
  total_economy = docs['economy']
  sold_stocks = docs['stocks']

  bal = await client.db.fetchrow(f'SELECT bank, cash, pvc, stocks FROM users WHERE id = $1 AND guild_id = $2 ', user_id, guild_id)
  argument = argument.lower()
  if bal is None:
    await open_account(guild_id, user_id)
    bal = await client.db.fetchrow(
        f'SELECT bank, cash, pvc, stocks FROM users WHERE id = $1 AND guild_id = $2 ',
        user_id, guild_id)

  if type == "sell":
    if len(argument) >= 2:
      if argument[-2] == "e":
        amount = str(int(argument[:-2]) * (10**int(argument[-1])))
      elif argument[-1] == "%" and int(argument[:-1]) in range(1, 101):
        amount = (int(argument[:-1]) / 100) * bal['stocks']
      elif argument == "all":
        amount = int(bal['stocks'])
      elif argument == "half":
        amount = int(0.5 * bal['stocks'])
      else:
        amount = argument
    else:
      amount = argument
      
  elif type == "buy":
    shares = total_shares - sold_stocks
    if len(argument) >= 2:
      if argument[-2] == "e":
        amount = str(int(argument[:-2]) * (10**int(argument[-1])))
      elif argument[-1] == "%" and int(argument[:-1]) in range(1, 101):
        amount = (int(argument[:-1]) / 100) * shares
      elif argument == "all":
        amount = int(shares)
      elif argument == "half":
        amount = int(0.5 * shares)
      else:
        amount = argument
    else:
      amount = argument
  else:
    amount = argument
  return int(amount), total_economy, sold_stocks, bal

def buy_stocks(amount, current_stocks, total_economy):
  total_cost = 0
  current_rate = math.ceil((total_economy / max(1, current_stocks)) * 1 / 2)
  for x in range(1, amount + 1):
    total_cost += current_rate
    current_stocks -= 1
    total_economy = total_economy - current_rate
    current_rate = math.ceil((total_economy / max(1, current_stocks)) * 1 / 2)
  return total_cost

def sell_stocks(amount, current_stocks, total_economy):
  total_value = 0
  current_rate = math.ceil((total_economy / max(1, current_stocks)) * 1 / 2)
  starting_rate = current_rate
  for x in range(1, int(amount) + 1):
    total_value += current_rate
    total_economy = total_economy + current_rate
    current_stocks += 1
    current_rate = math.ceil((total_economy / max(1, current_stocks)) * 1 / 2)
  return total_value - (starting_rate - current_rate)


class Market(commands.Cog):

  def __init__(self, client):
    self.client = client
    self.client.add_view(MarketInfo())
    self.stock_data = { } # guild_id : { 'data' : [] , 'time' : [] }
    self.ist_timezone = timezone('Asia/Kolkata')
    self.stock_data_update.start()

  async def cog_unload(self):
    self.stock_data_update.cancel()
    
  def check_market(ctx):
      return client.data[ctx.guild.id]['market'] and client.data[ctx.guild.id]['market']['status']
  

  @tasks.loop( minutes= 30  , reconnect = True )
  async def stock_data_update(self):
      for guild_id in self.client.data:
        if self.client.data[guild_id]['market'] and self.client.data[guild_id]['market']['status'] is True:
            docs = await client.db.fetchrow("SELECT SUM(cash + bank) as economy , SUM(stocks) as stocks FROM users WHERE guild_id = $1;",guild_id)
            total_economy = docs['economy']
            sold_stocks = docs['stocks']
            
            current_stocks =  self.client.data[guild_id]['market']['stocks'] - sold_stocks
            current_rate = math.ceil((total_economy / max(1, current_stocks)) * 1 / 2)
            
            if guild_id not in self.stock_data:
                self.stock_data[guild_id] = { 'data' : [current_rate] , 'time' : [datetime.now().timestamp()] }
            elif len(self.stock_data[guild_id]['data']) > 48  :
              
                self.stock_data[guild_id]['data'].pop(0)
                self.stock_data[guild_id]['data'].append(current_rate)
                self.stock_data[guild_id]['time'].pop(0)
                self.stock_data[guild_id]['time'].append(datetime.now().timestamp())
            else:
                self.stock_data[guild_id]['data'].append(current_rate)
                self.stock_data[guild_id]['time'].append(datetime.now().timestamp())

  
  @stock_data_update.before_loop
  async def before_stock_data_update(self):
      await self.client.wait_until_ready()
  
  @commands.hybrid_command()
  @commands.guild_only()
  @commands.check(check_perms)
  @cooldown(1, 5, BucketType.member)
  async def marketsetup(self , ctx , status: bool = None , stocks: int = 100000) :

      if status:
          await self.client.db.execute('UPDATE guilds SET market = $1 WHERE id = $2', {"status": status,"stocks": stocks}, ctx.guild.id )
          self.client.data[ctx.guild.id]['market'] = { 'status' : status , 'stocks' : stocks }
          self.stock_data[ctx.guild.id] = { 'data' : [] , 'time' : [] }
          await ctx.send(embed=bembed(f"Market is now open with {stocks} shares."))
      elif status is False:
          await self.client.db.execute('UPDATE guilds SET market = $1 WHERE id = $2', {"status": status,"stocks": stocks}, ctx.guild.id )
          self.client.data[ctx.guild.id]['market'] = { 'status' : status , 'stocks' : stocks }
          await ctx.send(embed=bembed(f"Market is now closed."))
      else:
          await ctx.send(embed=bembed(f"Status : { self.client.data[ctx.guild.id]['market']['status'] if self.client.data[ctx.guild.id]['market'] else False} \nStocks : {self.client.data[ctx.guild.id]['market']['stocks'] if self.client.data[ctx.guild.id]['market'] else 0}"))
 
  @commands.hybrid_command()
  @commands.guild_only()
  @commands.check(check_channel)
  @commands.check(check_market)
  @cooldown(1, 5, BucketType.member)
  async def market(self, ctx):
    total_stocks = self.client.data[ctx.guild.id]['market']['stocks']
    docs = await client.db.fetchrow("SELECT SUM(cash + bank) as economy , SUM(stocks) as stocks FROM users WHERE guild_id = $1;", ctx.guild.id)
    
    total_economy = docs['economy']
    sold_stocks = docs['stocks']
    
    current_stocks = total_stocks - sold_stocks
    current_rate = math.ceil((total_economy / max(1, current_stocks)) * 1 / 2)
    embed = discord.Embed(description=f"**__Market Details__**\n\nCurrent Value  : {coin(ctx.guild.id)} {current_rate}\n\n**__Market Stats__**")

    if ctx.guild.id not in self.stock_data:
      self.stock_data[ctx.guild.id] = { 'data' : [current_rate] , 'time' : [datetime.now().timestamp()] }
    self.stock_data[ctx.guild.id]['data'].append(round((total_economy / max(1, current_stocks) * 1 / 2) , 2))
    self.stock_data[ctx.guild.id]['time'].append(datetime.now().timestamp())

    plt.style.use('dark_background')
      
    plt.plot([
        datetime.fromtimestamp(i)
        for i in self.stock_data[ctx.guild.id]['time']
    ], self.stock_data[ctx.guild.id]['data'] , color='cyan', label='Stock Data' ,  linestyle='-', marker='o', markersize=5, alpha=0.7, markerfacecolor='lightblue', markeredgecolor='white')
    plt.ylim(
        int(min(self.stock_data[ctx.guild.id]['data'])) - 1,
        int(max(self.stock_data[ctx.guild.id]['data'])) + 2)
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.gca().xaxis.set_major_formatter(
        DateFormatter('%H:%M', tz=self.ist_timezone))
    plt.gcf().autofmt_xdate()
    plt.title('Stock Data')
    # Customize grid and legend
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.legend(loc='upper left')
    
    # Set background color and borders for the plot
    plt.gca().set_facecolor('#2C2F33')
    plt.gca().spines['bottom'].set_color('white')
    plt.gca().spines['top'].set_color('white')
    plt.gca().spines['right'].set_color('white')
    plt.gca().spines['left'].set_color('white')

    # Customize ticks color
    plt.tick_params(axis='x', colors='white')
    plt.tick_params(axis='y', colors='white')
    
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    
    file = discord.File( buffer , filename="image.png")
    embed.set_image(url="attachment://image.png")
    plt.clf()
    self.stock_data[ctx.guild.id]['data'].pop()
    self.stock_data[ctx.guild.id]['time'].pop()
    
    view = MarketInfo()
    
    await ctx.send(file=file, embed=embed , view = view)



  @commands.hybrid_command(aliases=["bs"])
  @commands.guild_only()
  @commands.check(check_channel)
  @commands.check(check_market)
  @cooldown(1, 10, BucketType.member)
  @commands.max_concurrency(1, BucketType.guild, wait=True)
  async def buystocks(self, ctx, amount: str):
    
    total_stocks = self.client.data[ctx.guild.id]['market']['stocks']
    amount, total_economy, sold_stocks, bal = await amountConverterMarket(ctx.author.id, ctx.guild.id, amount, "buy", total_stocks)
    current_stocks = total_stocks - sold_stocks
    
    if amount > 100000:
      return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> Failed: You cannot buy more than 100,000 shares at once."))

    if bal['cash'] < 0:
      await ctx.command.reset_cooldown(ctx)
      return await ctx.send(embed=bembed('<:pixel_error:1187995377891278919> Failed: Your Cash should not be in negative.'))
    elif amount > total_stocks:
      return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> Failed: You cannot buy that many shares."))
    if amount > current_stocks:
      return await ctx.send(embed=bembed('<:pixel_error:1187995377891278919> Failed: Not enough shares available in the market.'))
    elif amount <= 0:
      return await ctx.send(embed=bembed('<:pixel_error:1187995377891278919> Failed: Not a valid amount to buy.'))
    
    total_cost = buy_stocks(amount, current_stocks, total_economy)

    if bal['bank'] < total_cost:
      await ctx.send(embed=bembed(f"<:pixel_error:1187995377891278919> Failed: You dont have enough Money, You need {coin(ctx.guild.id)} {total_cost:,}."))
      return
    else:
      await self.client.db.execute('UPDATE users SET bank = bank - $1, stocks = stocks + $2 WHERE id = $3 AND guild_id = $4', total_cost, amount, ctx.author.id, ctx.guild.id)

    user_name = ctx.author.nick if ctx.author.nick else ctx.author.display_name

    embed = discord.Embed(
        title=f"{user_name}",
        url=f"https://tickap.com/user/{ctx.author.id}",
        description=
        f"**__Transaction Details__**\n\n>>> Share(s) bought : 📈 {amount:,}\nTotal money paid : {coin(ctx.guild.id)} {total_cost:,}",
        color=discord.Color.blue())
    embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon)
    await ctx.send(embed=embed)

  @buystocks.error
  @commands.guild_only()
  @commands.check(check_channel)
  async def buystocks_error(self, ctx, error):
    ecoembed = discord.Embed(color=0xF90651)
    ecoembed.set_author(name=ctx.author,
                        icon_url=ctx.author.display_avatar.url)
    if isinstance(error, commands.CommandOnCooldown):
      sec = int(error.retry_after)
      min, sec = divmod(sec, 60)
      ecoembed.description = f"⌚ | try after {min}min {sec}seconds."
      await ctx.send(embed=ecoembed)
      return
    else :
      print(error)

  @commands.hybrid_command(aliases=["ss"])
  @commands.guild_only()
  @commands.check(check_channel)
  @commands.check(check_market)
  @cooldown(1, 10, BucketType.member)
  @commands.max_concurrency(1, BucketType.guild, wait=True)
  async def sellstocks(self, ctx, amount: str):
    total_stocks = self.client.data[ctx.guild.id]['market']['stocks']
    amount, total_economy, sold_stocks, bal = await amountConverterMarket(ctx.author.id, ctx.guild.id, amount, "sell", total_stocks)
    user_shares = bal['stocks']

    if amount > 100000:
      return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> Failed: You cannot sell more than 100,000 shares at once."))

    if not user_shares or user_shares <= 0: 
      return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> Failed: You do not own any shares to sell."))
    if amount > user_shares:
      return await ctx.send(embed=bembed(f"<:pixel_error:1187995377891278919> Failed: You do not own 📈 {amount:,} shares to sell."))
    elif amount <= 0:
      await ctx.send(embed=bembed(f"<:pixel_error:1187995377891278919> Failed: Not a valid amount to sell."))
      return
    elif amount > total_stocks:
      await ctx.send(embed=bembed(
          "<:pixel_error:1187995377891278919> Failed: You cannot sell that many shares."
      ))
      return

    current_stocks = total_stocks - sold_stocks
    total_value = sell_stocks(amount, current_stocks, total_economy)

    await self.client.db.execute(
        'UPDATE users SET bank = bank + $1, stocks = stocks - $2 WHERE id = $3 AND guild_id = $4',
        total_value, amount, ctx.author.id, ctx.guild.id)

    embed = discord.Embed(
        title=f"{ctx.author.display_name}",
        url=f"https://tickap.com/user/{ctx.author.id}",
        # description=
        # f"**__Transaction Details__**\n>>> ```yaml\n• Shares sold      : 📈 {number}\n• Total value      : {coin(ctx.guild.id)} {total_cost}\n• Current rate     : {coin(ctx.guild.id)} {current_rate}\n• Stocks in market : 📈 {current_stocks}```",
        description=
        f"**__Transaction Details__**\n\n>>> Share(s) sold : 📈 {amount:,}\nTotal in value : {coin(ctx.guild.id)} {total_value:,}",
        color=discord.Color.blue())
    embed.set_footer(text=f"{ctx.guild.name}", icon_url=ctx.guild.icon)
    await ctx.send(embed=embed)


  @sellstocks.error
  @commands.guild_only()
  @commands.check(check_channel)
  async def sellstocks_error(self, ctx, error):
    ecoembed = discord.Embed(color=0xF90651)
    ecoembed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
    if isinstance(error, commands.CommandOnCooldown):
      sec = int(error.retry_after)
      min, sec = divmod(sec, 60)
      ecoembed.description = f"⌚ | try after {min}min {sec}seconds."
      await ctx.send(embed=ecoembed)
      return

  @commands.hybrid_command(aliases=["ac"])
  @commands.guild_only()
  @commands.check(check_channel)
  @commands.check(check_market)
  @cooldown(1, 5, BucketType.member)
  async def account(self, ctx, user: discord.Member = None):
    if user is None:
      user = ctx.author
    bal = await client.db.fetchrow(f'SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', user.id, ctx.guild.id)
    if bal is None:
      await open_account(ctx.guild.id, user.id)
      bal = await self.client.db.fetchrow( 'SELECT * FROM users WHERE id = $1 AND guild_id = $2 ', user.id, ctx.guild.id)
    docs = await client.db.fetchrow("SELECT SUM(cash + bank) as economy , SUM(stocks) as stocks FROM users WHERE guild_id = $1;", ctx.guild.id)
    total_stocks = client.data[ctx.guild.id]['market']['stocks']
    total_economy = docs['economy']
    sold_stocks = docs['stocks']
    current_stocks = total_stocks - sold_stocks
    total_value = sell_stocks(bal['stocks'], current_stocks, total_economy)
    net_worth = bal['bank'] + bal['cash'] + total_value

    embed = discord.Embed(
        timestamp=ctx.message.created_at,
        title=f"{user.display_name}",
        url=f"https://tickap.com/user/{user.id}",
        description=
        f"**__Account Details__**",
        color=discord.Color.blue())
    embed.add_field(name="**Net Worth**", value=f"{coin(ctx.guild.id)} {net_worth:,}")
    embed.add_field(name="**Bank balance**", value=f"{coin(ctx.guild.id)} {bal['bank']:,}")
    embed.add_field(name="**Shares held**", value=f"📈 {bal['stocks']:,}")
    if ctx.author != user:
      embed.set_footer(text=f"Requested By: {ctx.author.name} | use /bug to report a bug", icon_url=f"{ctx.author.display_avatar}")
    else:
      embed.set_footer(text=f"Use /bug to report a bug")
    await ctx.send(embed=embed)

  @commands.hybrid_command(name="calculate", aliases=["cal"], description="Calculate the buy/sell value of stocks in the market.")
  @commands.guild_only()
  @commands.check(check_channel)
  @cooldown(1, 5, BucketType.member)
  async def calculate(self, ctx, action: str, shares: str,):
    if shares.lower() in ["all", "half"]:
      return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> Failed: Invalid amount to calculate."))
    
    if action.lower() in ["buy", "bs", "buystocks"]:
      action = "buy"
    elif action.lower() in ["sell", "ss", "sellstocks"]:
      action = "sell"
    else:
      return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> Failed: Invalid Input.", discord.Color.brand_red))
    
    total_stocks = self.client.data[ctx.guild.id]['market']['stocks']
    amount, total_economy, sold_stocks, bal = await amountConverterMarket(ctx.author.id, ctx.guild.id, shares, "buy", total_stocks)
    current_stocks = total_stocks - sold_stocks

    if amount > 100000:
      return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> Failed: You cannot buy/sell more than 100,000 shares at once."))

    if amount > current_stocks:
      return await ctx.send(embed=bembed('<:pixel_error:1187995377891278919> Failed: Not enough shares available in the market.'))
    elif amount == 0:
      return await ctx.send(embed=bembed("<:pixel_error:1187995377891278919> Failed: Can't buy/sell 0 stocks."))
    elif amount < 0:
      return await ctx.send(embed=bembed('<:pixel_error:1187995377891278919> Failed: Not a valid amount to buy/sell.'))

    if action == "buy":
      total_cost = buy_stocks(amount, current_stocks, total_economy)
      return await ctx.send(embed=bembed(f"Buying 📈{amount:,} will cost you {coin(ctx.guild.id)}{total_cost:,}"))
    elif action == "sell":
      total_value = sell_stocks(amount, current_stocks, total_economy)
      return await ctx.send(embed=bembed(f"Selling 📈{amount:,} will give you {coin(ctx.guild.id)} {total_value:,}"))

async def setup(client):
  await client.add_cog(Market(client))
