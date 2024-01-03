from typing import Any, List, Mapping, Optional
import discord
from discord.ext import commands
from discord.ui import Button, View
from database import *

class MyHelp(commands.HelpCommand):
    
    async def send_bot_help(self, mapping) -> None:
        
        embed = discord.Embed(title="Help Commands" , color=discord.Color.blurple() )
        data = {"Economy " : [ "Economy" ] , "Games" : ["Bj" , "Games" , "Roulette" , "russian_roulette" ] , "Manager" : ["EcoManager" , "Settings" ] , "Store & Income" : ["store" , "income" ] ,  "PVC" : [ "PVC" , "PVC_COMMANDS"] }
        modules = { "Economy" : [] , "Games" : [] , "Manager" : [], "Store & Income" : [] , "PVC" : [] , "Other" : [] }
        
        for cog , commands  in mapping.items() :
            filter_commands = await self.filter_commands(commands , sort=True)
            
            if not cog :
                modules["Other"].extend(filter_commands)    
            elif cog.qualified_name in data["Economy "]:
                modules["Economy"].extend(filter_commands)
            elif cog.qualified_name in data["Games"]:
                modules["Games"].extend(filter_commands)
            elif cog.qualified_name in data["Manager"]:
                modules["Manager"].extend(filter_commands)
            elif cog.qualified_name in data["Store & Income"]:
                modules["Store & Income"].extend(filter_commands)
            elif cog.qualified_name in data["PVC"]:
                modules["PVC"].extend(filter_commands)
            elif cog.qualified_name is "Help":
                pass
            else:
                modules["Other"].extend(filter_commands)
          
        for module , commands in modules.items():
            if len(commands) != 0:
                embed.add_field(name=module , value=f"`{'` `'.join([command.name for command in commands])}`" , inline=False)      
        embed.set_footer(text=f"Use {self.context.clean_prefix}help <command> for more info on a command.")
        await self.context.send(embed=embed , view= helpCommandView())
    
    async def send_command_help(self, command) -> None:
        filter_commands = await self.filter_commands([command] , sort=True)
        if len(filter_commands) == 0 :
            return await self.context.send( embed= discord.Embed(description="Hidden command , add in your to know more about it" , color=discord.Color.red()) , view= helpCommandView())
        embed = discord.Embed(title=f"{command.name}" , description= f"`{self.get_command_signature(command)}`"   , color=discord.Color.blurple())
        await self.context.send(embed=embed , view= helpCommandView())
            
    async def send_error_message(self, error: str) -> None:
        return await self.context.send( embed= discord.Embed(description=f"Command not found" , color=discord.Color.red()) , view= helpCommandView() , delete_after=5)
    
class helpCommandView(View):
    def __init__(self):
        super().__init__(timeout=180)
        
        bot_inv_button = Button(label="Invite me",
                                style=discord.ButtonStyle.url,
                                url="https://tickap.com/bots")
        server_inv_button = Button(label="Support server",
                                    style=discord.ButtonStyle.url,
                                    url="https://discord.gg/WevmU9Wsba")
        self.add_item(bot_inv_button)
        self.add_item(server_inv_button)

class Help(commands.Cog):

    def __init__(self, client):
        self.client = client
        help_command = MyHelp()
        help_command.cog = self 
        self.client.help_command = help_command
        
async def setup(client):
  await client.add_cog(Help(client))
