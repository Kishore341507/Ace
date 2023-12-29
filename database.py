import discord
from discord.ext import commands
import asyncpg
from dotenv import load_dotenv
import os
import json

load_dotenv()

class MyBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def setup_hook(self):
        
        async def _setup_connection(con):
                    await con.set_type_codec('jsonb', schema='pg_catalog',
                                            encoder= json.dumps , decoder=json.loads)
        
        self.db = await asyncpg.create_pool(dsn= os.environ.get(f"DB") , init=_setup_connection )
        print("Connection to db DONE!")
 
        guilds = await self.db.fetch("SELECT * FROM guilds")
        self.data = { guild['id'] : dict(guild) for guild in guilds }

defult_prefix = ","


async def get_prefix(client , message):  
    try :
        prefix = client.data[message.guild.id]['prefix']
        if not prefix :
            raise Exception
    except Exception:
        prefix = defult_prefix
    finally :
        return commands.when_mentioned_or(prefix)(client , message)


intents = discord.Intents.default()
intents.members = True
intents.message_content = True
client = MyBot(command_prefix= get_prefix , strip_after_prefix =True, case_insensitive=True, intents=intents , help_command= None)

defult_economy = { 
                "work" : {
                    "max" : 5000 ,"min" : 1000,"cooldown" : 600},
                "crime" : {
                    "max" : 5000 ,"cooldown" : 600 ,},
                "rob" : {
                    "cooldown" : 600 ,"percent" : 0.8,}    }

defult_games = { 
            "bj" : {
                "max" : 50000 ,"min" : 1000},
            "slots" : {
                "max" : 50000 ,"min" : 1000,"2" : 1.5,"3" : 2},
            "roulette" : {
                "max" : 50000 ,"min" : 1000,},
            "coinflip" : {
                "max" : 50000 ,"min" : 1000,},
            "russian-roulette" : {
                "max" : 50000 ,"min" : 1000,},
            "roll" : {
                "max" : 50000 ,"min" : 1000,}   }


def check_perms(ctx) -> bool:
    return client.data[ctx.guild.id]['manager'] in [role.id for role in ctx.author.roles] or ctx.author.guild_permissions.manage_guild

def check_channel(ctx) ->bool : 
    return client.data[ctx.guild.id]['channels'] is None or len(client.data[ctx.guild.id]['channels']) == 0  or ctx.channel.id in client.data[ctx.guild.id]['channels'] 

async def open_account( guild_id : int , id : int):
        await client.db.execute('INSERT INTO users(id , guild_id , bank) VALUES ($1 , $2 ,$3)' , id , guild_id , client.data[guild_id].get( "opening_amount" , None) or 1000)

class amountconverter(commands.Converter):
    async def convert(self , ctx , argument):
        if argument[-2] == "e":
            return str(int(argument[:-2]) * (10** int(argument[-1])))
        else:
            return str(argument)

class Confirm(discord.ui.View):
    def __init__(self , user = None , role = None):
        super().__init__()
        self.value = None
        self.user = user
        self.role = role

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user and self.user != interaction.user :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        if self.role and self.role not in interaction.user.roles :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        await interaction.response.send_message('Confirming', ephemeral=True)
        self.value = True
        self.stop()

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.user and self.user != interaction.user :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        if self.role and self.role not in interaction.user.roles :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        await interaction.response.send_message('Cancelling', ephemeral=True)
        self.value = False
        self.stop()


class SelectUsers(discord.ui.View):
    def __init__(self , user = None , role = None):
        super().__init__()
        self.value = None
        self.user = user
        self.role = role
    
    @discord.ui.select( cls = discord.ui.UserSelect , placeholder = "Select A User" )
    async def selectuser(self, interaction , select) :
        if self.user and self.user != interaction.user :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        if self.role and self.role not in interaction.user.roles :
            await interaction.response.send_message('Not your interaction', ephemeral=True)
            return
        await interaction.response.send_message(f'{select.values[0]} Selected', ephemeral=True)
        self.value = select.values[0]
        self.stop()

def coin( guild_id : int ) :
    try :
        icon = client.data[guild_id]['coin']
        if not icon :
            raise Exception
    except Exception:
        icon = "🪙"
    finally :
        return icon

def pvc_coin( guild_id : int ) :
    icon = client.data.get(guild_id , {}).get('pvc_coin' , None )
    if not icon :
        icon = "🪙"
    name = client.data.get(guild_id , {}).get('pvc_name' , None )
    if not name :
        name= 'Pvc'
    return icon , name
    
def bembed(message=None) :
    return discord.Embed( description= message , color= 0x2b2d31 )
