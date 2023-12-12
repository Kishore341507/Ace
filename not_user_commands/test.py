import discord
from discord.ext import commands
from discord.ext.commands import BucketType, cooldown

class Event(commands.Cog):

    def __init__(self , client):
        self.client = client
        self.topic = "event"
        self.body = "empty"
        self.image = "https://media.discordapp.net/attachments/966022737367814156/966412820898000936/PAOD_logo-03.jpg?width=662&height=663"

#------------------------------------------------xxx--------------------------------------------------------------------------------
#                                               event   

    message_cooldown = commands.CooldownMapping.from_cooldown(1.0, 600.0, commands.BucketType.guild)    
    @commands.Cog.listener()
    async def on_message(self , message):

      if message.content.lower() == "hghghggh" :
        bucket = self.message_cooldown.get_bucket(message)
        retry_after = bucket.update_rate_limit()
        if not retry_after:
            embed = discord.Embed(color= discord.Color.blue() , title = self.topic , description = self.body)
            embed.set_image(url = self.image)
            embed.set_author(name = "PLAYGROUND" , icon_url= message.guild.icon)
            await message.channel.send(embed = embed) 
    

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_role(1018965791045075035)
    @cooldown(1, 5, BucketType.user)
    async def eventembed(self, ctx, topic :str , body : str , image : str ):
      self.topic = topic
      self.body = body
      self.image = image
      embed = discord.Embed(color= discord.Color.blue() , title = self.topic , description = self.body)
      embed.set_image(url = self.image)
      embed.set_author(name = "PLAYGROUND" , icon_url= ctx.guild.icon)
      await ctx.send(embed = embed)

    @commands.hybrid_command()
    @commands.guild_only()
    @commands.has_role(1018965791045075035)
    @cooldown(1, 5, BucketType.user)
    async def showembed(self, ctx):
      embed = discord.Embed(color= discord.Color.blue() , title = self.topic , description = self.body)
      embed.set_image(url = self.image)
      embed.set_author(name = "PLAYGROUND" , icon_url= ctx.guild.icon)
      await ctx.send(embed = embed)

      


async def setup(client):
   await client.add_cog(Event(client)) 