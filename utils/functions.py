import discord
from database import client

async def open_account( guild_id : int , id : int):
        await client.db.execute('INSERT INTO users(id , guild_id , bank) VALUES ($1 , $2 ,$3)' , id , guild_id , client.data[guild_id].get( "opening_amount" , None) or 1000)

def coin( guild_id : int ) :
    try :
        icon = client.data[guild_id]['coin']
        if not icon :
            raise Exception
    except Exception:
        icon = "🪙"
    finally:
        return icon

def pvc_coin( guild_id : int ) :
    icon = client.data.get(guild_id , {}).get('pvc_coin' , None )
    if not icon :
        icon = "<:tickapCoin:1191976654042570792>"
    name = client.data.get(guild_id , {}).get('pvc_name' , None )
    if not name :
        name= 'Pvc'
    return icon , name
    
def bembed(message=None, color = 0x2b2d31) :
    return discord.Embed( description= message , color= color )