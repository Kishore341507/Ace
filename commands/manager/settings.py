import discord
from discord.ext import commands
import math
from database import client
from utils import bembed, coin, pvc_coin, check_perms, default_economy, default_games, default_prefix

class singleInputModal(discord.ui.Modal, title='...'):

  def __init__(self, question, placeholder,min=None, max=None , default = None , required = True ):
    super().__init__()
    self.question = question
    self.placeholder = placeholder
    self.min = min
    self.max = max
    self.value = None
    self.default = default
    self.required = required
    self.input = discord.ui.TextInput(label=self.question,
                                      placeholder=self.placeholder,
                                      min_length=self.min,
                                      max_length=self.max,
                                      default= self.default ,
                                      required=self.required)
                                      
    self.add_item(self.input)

  async def on_submit(self, interaction: discord.Interaction):
    self.value = self.input.value
    await interaction.response.defer()


class singleInputLongModal(discord.ui.Modal):

  def __init__(self, question, placeholder):
    super().__init__()
    self.question = question
    self.placeholder = placeholder
    self.value = None
    self.input = discord.ui.TextInput(label=self.question,
                                      placeholder=self.placeholder,
                                      style=discord.TextStyle.long)
    self.add_item(self.input)

  async def on_submit(self, interaction: discord.Interaction):
    self.value = self.input.value
    await interaction.response.defer()


class multiInputModal(discord.ui.Modal, title='...'):

  def __init__(self, questions: list, placeholders: list, min: list,
               max: list , defaults : list = None):
    super().__init__()
    self.questions = questions
    self.placeholders = placeholders
    self.defaults = defaults
    if not defaults :
      self.defaults = [None] * len(questions)
    self.values = []

    for i in range(len(questions)):
      self.input = discord.ui.TextInput(
          label=self.questions[i],
          placeholder=self.placeholders[i],
          default= self.defaults[i],
          min_length=min[i],
          max_length=max[i]
      )
      self.add_item(self.input)

  async def on_submit(self, interaction: discord.Interaction):
    for item in self.children:
      self.values.append(item.value)
    await interaction.response.defer()


class Settings(commands.Cog):

  def __init__(self, client):
    self.client = client

# ----------------------------------------Main Setup Message----------------------------------------------

  async def setupMessage(self=None):
    # Number emoji's
    numbers = [
        "0️⃣", "<:Number_1:1186881792800735233>",
        "<:Number_2:1186881912342577192>", "<:Number_3:1186882312001044661>",
        "<:Number_4:1186882349691052163>", "<:Number_5:1186882396482707517>",
        "<:Number_6:1186882443530211428>", "<:Number_7:1186882490393174089>",
        "<:Number_8:1186882529362464779>", "<:Number_9:1186882699760238642>",
        "<:Number_10:1186882749127204864>"
    ]
    modules = {
        "Bot Settings": {
            "index": 1,
            "emoji": "🤖",
            "description": "Basic bot setup like prefix, casino manager, etc."
        },
        "Economy Settings": {
            "index":
            2,
            "emoji":
            "💰",
            "description":
            "Economy setup for your server including currency, work/crime limit etc."
        },
        "Game Settings": {
            "index": 3,
            "emoji": "🎲",
            "description": "Manage your game settings i.e gambling limits"
        },
        "PVC Settings": {
            "index": 4,
            "emoji": "🔉",
            "description": "Setup Private VC for your server."
        },
        "Market Setup": {
          "index" : 5,
          "emoji" : "📈",
          "description" : "Setup stock market and view market or server economy stats."
        }
    }
    embed = discord.Embed(title="Setup options", color=discord.Color.green())

    for module_name, module_data in modules.items():
      embed.add_field(
          name=
          f"{numbers[module_data['index']]} {module_data['emoji']} **{module_name}**",
          value=module_data['description'],
          inline=False)

    class mainSetupView(discord.ui.View):

      def __init__(self, modules):
        super().__init__(timeout=180)
        self.modules = modules
        self.user_id = None
        self.message = None

      async def interaction_check(self, interaction: discord.Interaction):

        if interaction.user.id == self.user_id:
          return True
        else:
          await interaction.response.send_message(embed=discord.Embed(
              description=
              "<:pixel_error:1187995377891278919> Interaction failed: Not your panel.",
              color=0x2b2c31),
                                                  ephemeral=True)
          return False

      async def on_timeout(self):
        for item in self.children:
          item.disabled = True
        content = self.message.content[:-18] + "**[** Inactive **]**"
        await self.message.edit(content=content, view=self)

      @discord.ui.select(placeholder="Select a function to setup.",
                         options=[
                             discord.SelectOption(
                                 label=module_name,
                                 value=module_data["index"],
                                 emoji=module_data['emoji'],
                                 description=module_data['description'])
                             for module_name, module_data in modules.items()
                         ],
                         custom_id="main_setup_select")
      async def main_setup_select(self, interaction: discord.Interaction,
                                  select):
        main_selection = int(select.values[0])

        if main_selection == 1:
          embed, view = await Settings.botSettingsMessage(interaction.guild)
        elif main_selection == 2:
          embed, view = await Settings.economySettingsMessage(interaction.guild)
        elif main_selection == 3:
          embed, view = await Settings.gameSettingsMessage(interaction.guild)
        elif main_selection == 4:
          embed, view = await Settings.pvcSettingsMessage(interaction.guild)
        elif main_selection == 5:
          embed, view = await Settings.marketSettingsMessage(interaction.guild)
        else:
          await interaction.response.send_message(embed=bembed(
              f"<:pixel_error:1187995377891278919> Interaction Failed: Unknown error"
          ),
                                                  ephemeral=True)
          return
        view.user_id = self.user_id
        view.message = self.message
        await interaction.response.edit_message(embed=embed, view=view)

    return embed, mainSetupView(modules)

# ----------------------------------------Bot Settings Message----------------------------------------------

  async def botSettingsMessage(guild: discord.Guild):
    # Fetching bot prefix
    bot_prefix = client.data[guild.id]['prefix'] or default_prefix

    # Fetching casino manager role
    if client.data[guild.id]["manager"] and guild.get_role(
        client.data[guild.id]["manager"]):
      manager_role = guild.get_role(client.data[guild.id]["manager"]).mention
    else:
      client.data[guild.id]["manager"] = None
      manager_role = "No manager role set."

    # Fetching Active channels for casino commands
    active_channels = ''  # Initiatialising as empty
    if client.data[guild.id]["channels"] and len(
        client.data[guild.id]["channels"]) > 0:
      for channel in list(client.data[guild.id]["channels"]):
        if guild.get_channel(channel):
          active_channels += f"{guild.get_channel(channel).mention}\n"
        else:
          client.data[guild.id]["channels"].remove(channel)
    else:
      client.data[guild.id]["channels"] = None
      active_channels = "Active In all channels"

    # Creating the embeded message
    embed = discord.Embed(title="Bot Settings")
    embed.description = f"Prefix - ` {bot_prefix} `"
    embed.add_field(name="Casino Manager", value=manager_role, inline=False)
    embed.add_field(name="Active Channel(s)",
                    value=active_channels,
                    inline=False)

    # Creating the view
    class botSettingsView(discord.ui.View):

      def __init__(self, guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.user_id = None
        self.message = None

      async def interaction_check(self, interaction: discord.Interaction):

        if interaction.user.id == self.user_id:
          return True
        else:
          await interaction.response.send_message(embed=discord.Embed(
              description=
              "<:pixel_error:1187995377891278919> Interaction failed: Not your panel.",
              color=0x2b2c31),
                                                  ephemeral=True)
          return False

      async def on_timeout(self):
        for item in self.children:
          item.disabled = True
        content = self.message.content[:-18] + "**[** Inactive **]**"
        await self.message.edit(content=content, view=self)

      @discord.ui.select(
          placeholder="Select a setting to change.",
          options=[
              discord.SelectOption(label="Main menu",
                                   emoji="<:Backtomenu:1187504974226268211>",
                                   description="Go back to main menu page.",
                                   value="0"),
              discord.SelectOption(label="Prefix",
                                   emoji="<:settings:1187254549828882562>",
                                   description="Change the bot prefix.",
                                   value="1"),
              discord.SelectOption(
                  label="Casino Manager",
                  emoji="<:settings:1187254549828882562>",
                  description="Change the casino manager role.",
                  value="2"),
              discord.SelectOption(
                  label="Active Channel(s)",
                  emoji="<:settings:1187254549828882562>",
                  description="Change the active channels for casino commands.",
                  value="3")
          ],
          custom_id="bot_setings_select")
      async def bot_setings_select(self, interaction: discord.Interaction,
                                   select):

        selection = int(select.values[0])

        if selection == 0:
          embed, view = await Settings.setupMessage()
          view.user_id = self.user_id
          view.message = self.message
          await interaction.response.edit_message(embed=embed, view=view)
          return

        elif selection == 1:
          # Creating and sending the modal to update the bot prefix
          modal = singleInputModal("Enter new prefix.",
                                   "The length of input should be 1", 0, 1 , client.data[interaction.guild.id]["prefix"] or default_prefix)
          modal.title = "Change the prefix for the bot."
          await interaction.response.send_modal(modal)
          await modal.wait()

          # Updating the value of the prefix in the database
          if modal.value and len(modal.value) == 1:
            client.data[self.guild.id]["prefix"] = modal.value
            await client.db.execute(
                'UPDATE guilds SET prefix = $1 WHERE id = $2', modal.value,
                self.guild.id)

            # Updating the original message
            embed, view = await Settings.botSettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
          else:
            await interaction.followup.send("Incorrect input", ephemeral=True)

        elif selection == 2:
          # Ephemeral message view's logic (Casino Manager)
          async def update_manager(interaction):
            data = manager_select.values
            if len(data) == 0:
              await client.db.execute(
                  'UPDATE guilds SET manager = $1 WHERE id = $2', None,
                  interaction.guild_id)
              client.data[interaction.guild_id]["manager"] = None
            else:
              await client.db.execute(
                  'UPDATE guilds SET manager = $1 WHERE id = $2', data[0].id,
                  interaction.guild_id)
              client.data[interaction.guild_id]["manager"] = data[0].id
            await interaction.response.edit_message(
                embed=bembed("Casino Manager role updated."), view=None)
            view1.stop()

          # Ephemeral message's view (Casino Manager)
          manager_select = discord.ui.RoleSelect(
              placeholder="Select a role to set as casino manager." , default_values=[interaction.guild.get_role(client.data[guild.id]["manager"])] if client.data[guild.id]["manager"] else None)
          manager_select.callback = update_manager
          view1 = discord.ui.View().add_item(manager_select)

          # Sending the ephemeral message (Casino Manager)
          await interaction.response.send_message(
              embed=bembed("Use the dropdown menu below."),
              view=view1,
              ephemeral=True)
          await view1.wait()

          # Updating the original message
          embed, view = await Settings.botSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return

        elif selection == 3:
          # Ephemeral message view's logic (Casino active channels)
          async def update_channels(interaction):
            data = channels_select.values
            if len(data) == 0:
              await client.db.execute(
                  'UPDATE guilds SET channels = $1 WHERE id = $2', None,
                  interaction.guild.id)
              client.data[interaction.guild.id]["channels"] = None
            else:
              await client.db.execute(
                  'UPDATE guilds SET channels = $1 WHERE id = $2',
                  [item.id for item in data], interaction.guild.id)
              client.data[interaction.guild.id]["channels"] = [
                  item.id for item in data
              ]
            await interaction.response.edit_message(
                embed=bembed("Active channels updated."), view=None)
            view1.stop()

          # Ephemeral message's view (Casino active channels)
          channels_select = discord.ui.ChannelSelect(
              channel_types=[discord.ChannelType.text],
              placeholder="Casino command channels",
              min_values=0,
              max_values=10,
              default_values= [ interaction.guild.get_channel(channel) for channel in client.data[guild.id]["channels"] ] if client.data[guild.id]["channels"] else None)
          channels_select.callback = update_channels
          view1 = discord.ui.View().add_item(channels_select)

          # Sending the ephemeral message (Casino active channels)
          await interaction.response.send_message(
              embed=bembed("Use the dropdown menu below."),
              view=view1,
              ephemeral=True)
          await view1.wait()

          # Updating the original message
          embed, view = await Settings.botSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return

        else:
          await interaction.response.send_message(embed=bembed(
              f"<:pixel_error:1187995377891278919> Interaction Failed: Unknown error"
          ),
                                                  ephemeral=True)
          return

    return embed, botSettingsView(guild)

  #----------------------------------------Economy Settings Message------------------------------------------
  
  async def economySettingsMessage(guild: discord.Guild):
    
    client.data[guild.id]['economy'] = { **default_economy ,  **(client.data[guild.id]['economy'] if client.data[guild.id]['economy'] else {})}

    # Fetching the economy coin
    economy_coin = coin(guild.id)

    # Fetching channels for Automoney
    automoney_channels = ''  # Initiatialising as empty
    if client.data[guild.id]["am_channels"] and len(
        client.data[guild.id]["am_channels"]) > 0:
      for channel in list(client.data[guild.id]["am_channels"]):
        if guild.get_channel(channel):
          automoney_channels += f"{guild.get_channel(channel).mention}\n"
        else:
          client.data[guild.id]["am_channels"].remove(channel)
    else:
      client.data[guild.id]["am_channels"] = None
      automoney_channels = "None"

    # Fetching amount of cash given as automoney when chatting in automoney channels
    automoney_amount_cash = client.data[guild.id]['am_cash']
    automoney_amount_pvc = client.data[guild.id]['am_pvc']

    # Creating the embed for Economy settings message
    embed = discord.Embed(title="Economy Settings")
    embed.description = f"Economy Coin - {economy_coin}"
    embed.add_field(name="Automoney Channel(s)",
                    value=automoney_channels,
                    inline=False)
    embed.add_field(
        name="Automoney Settings",
        value=
        f"Auto Money(AM) Cash/min : **0-{automoney_amount_cash}**\nAuto Money(AM) pvc/min : **0-{automoney_amount_pvc}**",
        inline=False)
    embed.add_field(name="Rob Settings",
                    value= f"Percent : **{int((client.data[guild.id]['economy']['rob']['percent'])* 100)}%**\n`⌚` : **{int((client.data[guild.id]['economy']['rob']['cooldown'])/60)}mins**",
                    )
    embed.add_field(name="Crime Settings",
                    value= f"Amount : **{client.data[guild.id]['economy']['crime']['max']}**\n`⌚` : **{int((client.data[guild.id]['economy']['crime']['cooldown'])/60)}mins**",
                    )
    embed.add_field(name="Work Settings",
                    value= f"Amount : **{client.data[guild.id]['economy']['work']['min']}** - **{client.data[guild.id]['economy']['work']['max']}**\n `⌚` : **{int((client.data[guild.id]['economy']['work']['cooldown'])/60)}mins**",
                    )

    # Creating the Economy settings view
    class economySettingsView(discord.ui.View):

      def __init__(self, guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.user_id = None
        self.message = None

      async def interaction_check(self, interaction: discord.Interaction):

        if interaction.user.id == self.user_id:
          return True
        else:
          await interaction.response.send_message(embed=discord.Embed(
              description=
              "<:pixel_error:1187995377891278919> Interaction failed: Not your panel.",
              color=0x2b2c31),
                                                  ephemeral=True)
          return False

      async def on_timeout(self):
        for item in self.children:
          item.disabled = True
        content = self.message.content[:-18] + "**[** Inactive **]**"
        await self.message.edit(content=content, view=self)

      @discord.ui.select(
          placeholder="Select a setting to change.",
          options=[
              discord.SelectOption(label="Main menu",
                                   emoji="<:Backtomenu:1187504974226268211>",
                                   description="Go back to main menu page.",
                                   value="0"),
              discord.SelectOption(
                  label="Coin",
                  emoji="<:settings:1187254549828882562>",
                  description="Change the currency symbol of your economy.",
                  value="1"),
              discord.SelectOption(
                  label="Automoney Channel(s)",
                  emoji="<:settings:1187254549828882562>",
                  description="Change the automoney channels.",
                  value="2"),
              discord.SelectOption(
                  label="Automoney Amount",
                  emoji="<:settings:1187254549828882562>",
                  description=
                  f"Change the amount of cash given as automoney when texting in automoney channels.",
                  value="3"),
              discord.SelectOption(
                  label="Work Settings",
                  emoji="<:settings:1187254549828882562>",
                  description=
                  f"Change the Work Command Settings.",
                  value="4"),
              discord.SelectOption(
                  label="Crime Settings",
                  emoji="<:settings:1187254549828882562>",
                  description=
                  f"Change the Crime Command Settings.",
                  value="5"),
              discord.SelectOption(
                  label="Rob Settings",
                  emoji="<:settings:1187254549828882562>",
                  description=
                  f"Change the Rob Command Settings.",
                  value="6"),
          ],
          custom_id="economy_setings_select")
      async def economy_setings_select(self, interaction: discord.Interaction,
                                       select):
        selection = int(select.values[0])

        # Main Menu
        if selection == 0:
          embed, view = await Settings.setupMessage()
          view.user_id = self.user_id
          view.message = self.message
          await interaction.response.edit_message(embed=embed, view=view)
          return

        # Economy Coin
        elif selection == 1:

          # Modal to update the economy coin
          modal = singleInputModal("Enter a coin to use as your Economy coin.",
                                   "Paste your coin.", 0, None , coin(interaction.guild.id) , False )
          modal.title = "Change the economy coin."
          await interaction.response.send_modal(modal)
          await modal.wait()

          # Checking if the input is valid and updating the economy coin
          if modal.value:
            client.data[interaction.guild.id]["coin"] = modal.value
            await client.db.execute(
                'UPDATE guilds SET coin = $1 WHERE id = $2', modal.value,
                interaction.guild.id)
          else:
            client.data[interaction.guild.id]["coin"] = modal.value
            await client.db.execute(
                'UPDATE guilds SET coin = $1 WHERE id = $2', modal.value,
                interaction.guild.id)
            
          # Updating the original message
          embed, view = await Settings.economySettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return

        # Automoney Channels
        elif selection == 2:

          # Ephemeral message view's logic (Automoney Channels)
          async def update_am_channels(interaction):
            data = am_channels_select.values
            if len(data) == 0:
              await client.db.execute(
                  'UPDATE guilds SET am_channels = $1 WHERE id = $2', None,
                  interaction.guild.id)
              client.data[interaction.guild.id]["am_channels"] = None
            else:
              await client.db.execute(
                  'UPDATE guilds SET am_channels = $1 WHERE id = $2',
                  [item.id for item in data], interaction.guild.id)
              client.data[interaction.guild.id]["am_channels"] = [
                  item.id for item in data
              ]
            await interaction.response.edit_message(
                embed=bembed("AM channels updated."), view=None)
            view1.stop()

          # Ephemeral message's view (Automoney Channels)
          am_channels_select = discord.ui.ChannelSelect(
              channel_types=[discord.ChannelType.text],
              placeholder="Auto Money channels",
              min_values=0,
              max_values=10, 
              default_values= [ interaction.guild.get_channel(channel) for channel in client.data[interaction.guild.id]["am_channels"] ] if client.data[interaction.guild.id]["am_channels"] else None )
          am_channels_select.callback = update_am_channels
          view1 = discord.ui.View().add_item(am_channels_select)

          # Sending the ephemeral message (Automoney Channels)
          await interaction.response.send_message(
              embed=bembed("Use the dropdown menu below."),
              view=view1,
              ephemeral=True)
          await view1.wait()

          # Updating the original message
          embed, view = await Settings.economySettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return

        # Automoney Amount
        elif selection == 3:

          # Modal to update the amount of cash given as automoney when texting in automoney channels
          modal = multiInputModal([
              "Enter the max amount of cash for automoney.",
              "Enter the max amount of pvc for automoney."
          ], ["Enter Cash amount.", "Enter PVC amount."], [1, 1], [None, None] , [ str(client.data[interaction.guild.id]['am_cash']) , str(client.data[interaction.guild.id]['am_pvc']) ])
          modal.title = "Automoney Amount Settings"
          await interaction.response.send_modal(modal)
          await modal.wait()

          # Checking if the inputs are valid and updating the automoney amoun settings
          has_value_error = False
          for value in modal.values:
            try:
              value = int(value)
            except ValueError:
              has_value_error = True

          if has_value_error:
            await interaction.followup.send("Invalid input detected.",
                                            ephemeral=True)
            return
          else:
            client.data[interaction.guild.id]['am_cash'] = int(modal.values[0])
            client.data[interaction.guild.id]['am_pvc'] = int(modal.values[1])
            await client.db.execute(
                'UPDATE guilds SET am_cash = $1 WHERE id = $2',
                int(modal.values[0]), interaction.guild.id)
            await client.db.execute(
                'UPDATE guilds SET am_pvc = $1 WHERE id = $2',
                int(modal.values[1]), interaction.guild.id)

          # Updating the original message
          embed, view = await Settings.economySettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return
        
        if selection == 4:
          
            # Modal to update the amount of cash given as work
            modal = multiInputModal([
                "Cooldown (in Minutes)",
                "Min Ammount",
                "Max Amount"
            ], ["Enter cooldown amount.","Enter Min Cash amount.", "Enter Max Cash amount."], [1, 1 , 1], [8, 8 , 8] , [ str(int((client.data[interaction.guild.id]['economy']['work']['cooldown'] if client.data[interaction.guild.id]['economy'] else default_economy['work']['cooldown']) / 60 ) ) , str(client.data[interaction.guild.id]['economy']['work']['min'] if client.data[interaction.guild.id]['economy'] else default_economy['work']['min'] ) , str(client.data[interaction.guild.id]['economy']['work']['max'] if client.data[interaction.guild.id]['economy'] else default_economy['work']['max']) ])
            modal.title = "Work Command Settings"
            await interaction.response.send_modal(modal)
            await modal.wait()

            # Checking if the inputs are valid and updating the automoney amoun settings
            has_value_error = False
            for value in modal.values:
              try:
                value = int(value)
              except ValueError:
                has_value_error = True

            if has_value_error:
              await interaction.followup.send("Invalid input detected.",
                                              ephemeral=True)
              return
            else:
              client.data[interaction.guild.id]['economy']['work'] = { "cooldown" : abs(int(modal.values[0])) * 60 , "min" : abs(int(modal.values[1])) , "max" : abs(int(modal.values[2])) }
              await client.db.execute(
                  'UPDATE guilds SET economy = $1 WHERE id = $2',
                  client.data[interaction.guild.id]['economy'], interaction.guild.id)

            # Updating the original message
            embed, view = await Settings.economySettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return
        
        if selection == 5:
            
              
              # Modal to update the amount of cash given as crime 
              modal = multiInputModal([
                  "Cooldown (in Minutes)",
                  "Max Amount"
              ], ["Enter cooldown amount.","Enter Max Cash amount."], [1, 1], [8, 8] , [ str(int((client.data[interaction.guild.id]['economy']['crime']['cooldown'] if client.data[interaction.guild.id]['economy'] else default_economy['crime']['cooldown']) / 60 ) ) , str(client.data[interaction.guild.id]['economy']['crime']['max'] if client.data[interaction.guild.id]['economy'] else default_economy['crime']['max']) ])
              modal.title = "Crime Command Settings"
              await interaction.response.send_modal(modal)
              await modal.wait()
  
              # Checking if the inputs are valid and updating the automoney amoun settings
              
              has_value_error = False
              for value in modal.values:
                try:
                  value = int(value)
                except ValueError:
                  has_value_error = True
  
              if has_value_error:
                await interaction.followup.send("Invalid input detected.",
                                                ephemeral=True)
                return
              else:
                client.data[interaction.guild.id]['economy']['crime'] = { "cooldown" : abs(int(modal.values[0])) * 60 , "max" : abs(int(modal.values[1])) }
                await client.db.execute(
                    'UPDATE guilds SET economy = $1 WHERE id = $2',
                    client.data[interaction.guild.id]['economy'], interaction.guild.id)
  
              # Updating the original message
              embed, view = await Settings.economySettingsMessage(self.guild)
              view.user_id = self.user_id
              view.message = self.message
              await interaction.message.edit(embed=embed, view=view)
              return
        
        if selection == 6:
          
          # Modal to update the amount rob
          modal = multiInputModal([
              "Cooldown (in Minutes)",
              "Percent (%)"
          ], ["Enter cooldown amount.","Enter Percent."], [1, 1], [8, 2] , [ str(int((client.data[interaction.guild.id]['economy']['rob']['cooldown'] if client.data[interaction.guild.id]['economy'] else default_economy['rob']['cooldown']) / 60 ) ) , str(int((client.data[interaction.guild.id]['economy']['rob']['percent'] if client.data[interaction.guild.id]['economy'] else default_economy['rob']['percent']) * 100)) ])
          
          modal.title = "Rob Command Settings"
          await interaction.response.send_modal(modal)
          await modal.wait()
          
          # Checking if the inputs are valid
          has_value_error = False
          for value in modal.values:
            try:
              value = int(value)
            except ValueError:
              has_value_error = True
          
          if has_value_error:
            await interaction.followup.send("Invalid input detected.",
                                            ephemeral=True)
            return
          else :
            client.data[interaction.guild.id]['economy']['rob'] = { "cooldown" : abs(int(modal.values[0])) * 60 , "percent" : abs(int(modal.values[1]) / 100) }
            await client.db.execute(
                'UPDATE guilds SET economy = $1 WHERE id = $2',
                client.data[interaction.guild.id]['economy'], interaction.guild.id)

            embed, view = await Settings.economySettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return
            
        else:
          await interaction.response.send_message(embed=bembed(
              f"<:pixel_error:1187995377891278919> Interaction Failed: Unknown error"
          ),
                                                  ephemeral=True)
          return
        

    return embed, economySettingsView(guild)




  #----------------------------------------Games Settings Message------------------------------------------
  
  async def gameSettingsMessage(guild: discord.Guild):
    
    client.data[guild.id]['games'] = { **default_games ,  **(client.data[guild.id]['games'] if client.data[guild.id]['games'] else {})}

    # Creating the embed for Economy settings message
    embed = discord.Embed(title="Game Settings")
    embed.add_field(name="Blackjack",
                    value= f"min : **{ client.data[guild.id]['games']['blackjack']['min']}**\nmax : **{client.data[guild.id]['games']['blackjack']['max']}**",
    )
    embed.add_field(name="Coinflip",
                    value= f"min : **{ client.data[guild.id]['games']['coinflip']['min']}**\nmax : **{client.data[guild.id]['games']['coinflip']['max']}**",
    )
    embed.add_field(name="Roulette",
                    value= f"min : **{ client.data[guild.id]['games']['roulette']['min']}**\nmax : **{client.data[guild.id]['games']['roulette']['max']}**",
    )
    embed.add_field(name="Russian-roulette",
                    value= f"min : **{ client.data[guild.id]['games']['russian-roulette']['min']}**\nmax : **{client.data[guild.id]['games']['russian-roulette']['max']}**",
    )
    embed.add_field(name="Roll",
                    value= f"min : **{ client.data[guild.id]['games']['roll']['min']}**\nmax : **{client.data[guild.id]['games']['roll']['max']}**",
    )
    embed.add_field(name="Slots",
                    value= f"min : **{ client.data[guild.id]['games']['slots']['min']}**\nmax : **{client.data[guild.id]['games']['slots']['max']}**",
    )
    # Creating the Economy settings view
    class gamesSettingsView(discord.ui.View):

      def __init__(self, guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.user_id = None
        self.message = None
        
      async def interaction_check(self, interaction: discord.Interaction):

        if interaction.user.id == self.user_id:
          return True
        else:
          await interaction.response.send_message(embed=discord.Embed(
              description=
              "<:pixel_error:1187995377891278919> Interaction failed: Not your panel.",
              color=0x2b2c31),
                                                  ephemeral=True)
          return False

      async def on_timeout(self):
        for item in self.children:
          item.disabled = True
        content = self.message.content[:-18] + "**[** Inactive **]**"
        await self.message.edit(content=content, view=self)

      @discord.ui.select(
          placeholder="Select a setting to change.",
          options=[
              discord.SelectOption(label="Main menu",
                                   emoji="<:Backtomenu:1187504974226268211>",
                                   description="Go back to main menu page.",
                                   value="0"),
              discord.SelectOption(
                  label="Blackjack",
                  emoji="<:settings:1187254549828882562>",
                  # description="Change the currency symbol of your economy.",
                  value="1"),
              discord.SelectOption(
                label="Coinflip" ,
                emoji="<:settings:1187254549828882562>",
                # description="Change the currency symbol of your economy.",
                value="2"),
              discord.SelectOption(
                label="Roulette" ,
                emoji="<:settings:1187254549828882562>",
                # description="Change the currency symbol of your economy.",
                value="3"),
              discord.SelectOption(
                label="Russian-roulette" ,
                emoji="<:settings:1187254549828882562>",
                # description="Change the currency symbol of your economy.",
                value="4"),
              discord.SelectOption(
                label="Roll" ,
                emoji="<:settings:1187254549828882562>",
                # description="Change the currency symbol of your economy.",
                value="5"),
              discord.SelectOption(
                label="Slots" ,
                emoji="<:settings:1187254549828882562>",
                # description="Change the currency symbol of your economy.",
                value="6"),       
          ],
          custom_id="game_setings_select")
      async def game_setings_select(self, interaction: discord.Interaction,
                                       select):
        selection = int(select.values[0])

        # Main Menu
        if selection == 0:
          embed, view = await Settings.setupMessage()
          view.user_id = self.user_id
          view.message = self.message
          await interaction.response.edit_message(embed=embed, view=view)
          return

        # BlackJack
        
        elif selection == 1:
            modal = multiInputModal([
                "Min Ammount",
                "Max Amount"], 
                                    ["Enter Min Cash amount.", "Enter Max Cash amount."], [1 , 1], [8, 8 ] , [ str( client.data[interaction.guild.id]['games']['blackjack']['min']) , str( client.data[interaction.guild.id]['games']['blackjack']['max']) ])
            modal.title = "Blackjack Command Settings"
            await interaction.response.send_modal(modal)
            await modal.wait()

            # Checking if the inputs are valid and updating the automoney amoun settings
            has_value_error = False
            for value in modal.values:
              try:
                value = int(value)
              except ValueError:
                has_value_error = True

            if has_value_error:
              await interaction.followup.send("Invalid input detected.",
                                              ephemeral=True)
              return
            else:
              client.data[interaction.guild.id]['games']['blackjack'] = { "min" : abs(int(modal.values[0])) , "max" : abs(int(modal.values[1])) }
              await client.db.execute(
                  'UPDATE guilds SET games = $1 WHERE id = $2',
                  client.data[interaction.guild.id]['games'], interaction.guild.id)

            # Updating the original message
            embed, view = await Settings.gameSettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return
        
        # Coinflip
        elif selection == 2:
            modal = multiInputModal([
                "Min Ammount",
                "Max Amount"], 
                                    ["Enter Min Cash amount.", "Enter Max Cash amount."], [1 , 1], [8, 8 ] , [ str( client.data[interaction.guild.id]['games']['coinflip']['min']) , str( client.data[interaction.guild.id]['games']['coinflip']['max']) ])
            modal.title = "Coinflip Command Settings"
            await interaction.response.send_modal(modal)
            await modal.wait()

            # Checking if the inputs are valid and updating the automoney amoun settings
            has_value_error = False
            for value in modal.values:
              try:
                value = int(value)
              except ValueError:
                has_value_error = True

            if has_value_error:
              await interaction.followup.send("Invalid input detected.",
                                              ephemeral=True)
              return
            else:
              client.data[interaction.guild.id]['games']['coinflip'] = { "min" : abs(int(modal.values[0])) , "max" : abs(int(modal.values[1]))  }
              await client.db.execute(
                  'UPDATE guilds SET games = $1 WHERE id = $2',
                  client.data[interaction.guild.id]['games'], interaction.guild.id)

            # Updating the original message
            embed, view = await Settings.gameSettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return
        
        # Roulette
        elif selection == 3:
            modal = multiInputModal([
                "Min Ammount",
                "Max Amount"], 
                                    ["Enter Min Cash amount.", "Enter Max Cash amount."], [1 , 1], [8, 8 ] , [ str( client.data[interaction.guild.id]['games']['roulette']['min']) , str( client.data[interaction.guild.id]['games']['roulette']['max']) ])
            modal.title = "Roulette Command Settings"
            await interaction.response.send_modal(modal)
            await modal.wait()

            # Checking if the inputs are valid and updating the automoney amoun settings
            has_value_error = False
            for value in modal.values:
              try:
                value = int(value)
              except ValueError:
                has_value_error = True

            if has_value_error:
              await interaction.followup.send("Invalid input detected.",
                                              ephemeral=True)
              return
            else:
              client.data[interaction.guild.id]['games']['roulette'] = { "min" : abs(int(modal.values[0])) , "max" : abs(int(modal.values[1])) }
              await client.db.execute(
                  'UPDATE guilds SET games = $1 WHERE id = $2',
                  client.data[interaction.guild.id]['games'], interaction.guild.id)

            # Updating the original message
            embed, view = await Settings.gameSettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return
        
        # Russian-roulette
        elif selection == 4:
            modal = multiInputModal([
                "Min Ammount",
                "Max Amount"], 
                                    ["Enter Min Cash amount.", "Enter Max Cash amount."], [1 , 1], [8, 8 ] , [ str( client.data[interaction.guild.id]['games']['russian-roulette']['min']) , str( client.data[interaction.guild.id]['games']['russian-roulette']['max']) ])
            modal.title = "Russian-roulette Command Settings"
            await interaction.response.send_modal(modal)
            await modal.wait()

            # Checking if the inputs are valid and updating the automoney amoun settings
            has_value_error = False
            for value in modal.values:
              try:
                value = int(value)
              except ValueError:
                has_value_error = True

            if has_value_error:
              await interaction.followup.send("Invalid input detected.",
                                              ephemeral=True)
              return
            else:
              client.data[interaction.guild.id]['games']['russian-roulette'] = { "min" : abs(int(modal.values[0]))  , "max" : abs(int(modal.values[1])) }
              await client.db.execute(
                  'UPDATE guilds SET games = $1 WHERE id = $2',
                  client.data[interaction.guild.id]['games'], interaction.guild.id)

            # Updating the original message
            embed, view = await Settings.gameSettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return
        
        # Roll
        elif selection == 5:
            modal = multiInputModal([
                "Min Ammount",
                "Max Amount"], 
                                    ["Enter Min Cash amount.", "Enter Max Cash amount."], [1 , 1], [8, 8 ] , [ str( client.data[interaction.guild.id]['games']['roll']['min']) , str( client.data[interaction.guild.id]['games']['roll']['max']) ])
            modal.title = "Roll Command Settings"
            await interaction.response.send_modal(modal)
            await modal.wait()

            # Checking if the inputs are valid and updating the automoney amoun settings
            has_value_error = False
            for value in modal.values:
              try:
                value = int(value)
              except ValueError:
                has_value_error = True

            if has_value_error:
              await interaction.followup.send("Invalid input detected.",
                                              ephemeral=True)
              return
            else:
              client.data[interaction.guild.id]['games']['roll'] = { "min" : abs(int(modal.values[0])) , "max" : abs(int(modal.values[1]))}
              await client.db.execute(
                  'UPDATE guilds SET games = $1 WHERE id = $2',
                  client.data[interaction.guild.id]['games'], interaction.guild.id)

            # Updating the original message
            embed, view = await Settings.gameSettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return
        
        # Slots
        elif selection == 6:
            modal = multiInputModal([
                "Min Ammount",
                "Max Amount"], 
                                    ["Enter Min Cash amount.", "Enter Max Cash amount.", ], [1 , 1 ], [8, 8  ] , [ str( client.data[interaction.guild.id]['games']['slots']['min']) , str( client.data[interaction.guild.id]['games']['slots']['max'])])
            modal.title = "Slots Command Settings"
            await interaction.response.send_modal(modal)
            await modal.wait()

            # Checking if the inputs are valid and updating the automoney amoun settings
            has_value_error = False
            for   value in modal.values:
              try:
                  value = int(value)
              except ValueError :
                has_value_error = True

            if has_value_error:
              await interaction.followup.send("Invalid input detected.",
                                              ephemeral=True)
              return
            else:
              client.data[interaction.guild.id]['games']['slots'] = { "min" : abs(int(modal.values[0])) , "max" : abs(int(modal.values[1])) , "2" : 1.5 , "3" : 3 }
              await client.db.execute(
                  'UPDATE guilds SET games = $1 WHERE id = $2',
                  client.data[interaction.guild.id]['games'], interaction.guild.id)

            # Updating the original message
            embed, view = await Settings.gameSettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return
          
        else:
          await interaction.response.send_message(embed=bembed(
              f"<:pixel_error:1187995377891278919> Interaction Failed: Unknown error"
          ),
                                                  ephemeral=True)
          return

    return embed, gamesSettingsView(guild)


# ----------------------------------------pvc Settings Message--------------------------------------------

  async def pvcSettingsMessage(guild: discord.Guild):

    # Fetching the pvc status for guild (on/off)
    if client.data[guild.id]['pvc']:
      pvc_on = True
    else:
      pvc_on = False
    pvc_status = "`🟢`" if pvc_on else "`🔴`"

    # Fetching the pvc coin name, symbol & rate
    pvc_coin_name = pvc_coin(guild.id)[1]
    pvc_coin_symbol = pvc_coin(guild.id)[0]
    pvc_coin_rate = client.data[guild.id]['rate']

    # Fetching the pvc min & max time limits
    pvc_min_time = client.data[guild.id]['pvc_min']
    pvc_max_time = client.data[guild.id]['pvc_max']

    # Fetching the commands channels for pvc
    if client.data[guild.id]["pvc_channel"] and guild.get_channel(
        client.data[guild.id]["pvc_channel"]):
      pvc_commands_channels = guild.get_channel(
          client.data[guild.id]["pvc_channel"]).mention
    else:
      client.data[guild.id]["pvc_channel"] = None
      pvc_commands_channels = "No seprate commands channel For PVC"

    # Fetching the join to create pvc channel
    if client.data[guild.id]["pvc_vc"] and guild.get_channel(
        client.data[guild.id]["pvc_vc"]):
      join_to_create_pvc_channel = guild.get_channel(
          client.data[guild.id]["pvc_vc"]).mention
    else:
      client.data[guild.id]["pvc_vc"] = None
      join_to_create_pvc_channel = "No channel setup for join to create pvc."

    # Fetching the category where pvc's are created
    if client.data[guild.id]["pvc_category"] and guild.get_channel(
        client.data[guild.id]["pvc_category"]):
      pvc_category = guild.get_channel(
          client.data[guild.id]["pvc_category"]).mention
    else:
      client.data[guild.id]["pvc_category"] = None
      pvc_category = "No Category"

    # Creating the embeded message for PVC settings
    embed = discord.Embed(title="PVC Settings")
    embed.description = f"PVC Status - {pvc_status}\nCoin - {pvc_coin_symbol}\nCoin Name - `{pvc_coin_name}`\n\nRate/hr :  - **{pvc_coin_rate}**\n\nMin Time Limit - **{pvc_min_time}** Hrs\nMax Time Limit - **{pvc_max_time}** Hrs\n(0 means no limit)"
    embed.add_field(name="PVC Commands Channel",
                    value=pvc_commands_channels,
                    inline=False)
    embed.add_field(name="Join To Create PVC Channel",
                    value=join_to_create_pvc_channel,
                    inline=False)
    embed.add_field(name="PVC Category", value=pvc_category, inline=False)
    perms_value = ''
    if client.data[guild.id]["pvc_perms"]:
      for role in client.data[guild.id]["pvc_perms"]:
        if guild.get_role(int(role)):
          perms_value += guild.get_role(int(role)).mention + '\n' + 'Allow :' +' ,'.join([i[0] for i in discord.Permissions(client.data[guild.id]["pvc_perms"][role]['allow']) if i[1] == True]) + '\n' + 'Deny :' +' ,'.join([i[0] for i in discord.Permissions(client.data[guild.id]["pvc_perms"][role]['deny']) if i[1] == True]) + '\n'
    
    if perms_value != '' and len(perms_value) < 999:
      embed.add_field(name="PVC Role Permissions", value=perms_value, inline=False)

    embed.add_field(name="Public PVC", value= f'vc limit : {client.data[guild.id]['pvc_public']}' if client.data[guild.id]['pvc_public']!=0 else 'Off' , inline=False)

    # Creating the view for PVC settings
    class pvcSettingsView(discord.ui.View):

      def __init__(self, guild):
        super().__init__(timeout=180)
        self.guild = guild
        self.user_id = None
        self.message = None

      async def interaction_check(self, interaction: discord.Interaction):

        if interaction.user.id == self.user_id:
          return True
        else:
          await interaction.response.send_message(embed=discord.Embed(
              description=
              "This is not your panel. You need to run the command yourself.",
              color=0x2b2c31),
                                                  ephemeral=True)
          return False

      async def on_timeout(self):
        for item in self.children:
          item.disabled = True
        content = self.message.content[:-18] + "**[** Inactive **]**"
        await self.message.edit(content=content, view=self)

      @discord.ui.select(
          placeholder="Select a setting to change.",
          options=[
              discord.SelectOption(label="Main menu",
                                   emoji="<:Backtomenu:1187504974226268211>",
                                   description="Go back to main menu page.",
                                   value="0"),
              discord.SelectOption(
                  label="PVC Status",
                  emoji="<:settings:1187254549828882562>",
                  description="Turn the PVC's on or off for the server.",
                  value="1"),
              discord.SelectOption(
                  label="PVC Coin/Name",
                  emoji="<:settings:1187254549828882562>",
                  description="Change the name or currency symbol of your pvc.",
                  value="2"),
              discord.SelectOption(
                  label="PVC Rate",
                  emoji="<:settings:1187254549828882562>",
                  description="Edit the cost/rate of pvc(/hr)",
                  value="3"),
              discord.SelectOption(
                  label="PVC limits",
                  emoji="<:settings:1187254549828882562>",
                  description="Edit the min/max time a pvc can be created for.",
                  value="4"),
              discord.SelectOption(
                  label="PVC Commands Channel",
                  emoji="<:settings:1187254549828882562>",
                  description="Change the commands channel for PVC.",
                  value="5"),
              discord.SelectOption(
                  label="Join To Create PVC Channel",
                  emoji="<:settings:1187254549828882562>",
                  description="Change the join to create pvc channel.",
                  value="6"),
              discord.SelectOption(label="PVC Category",
                                   emoji="<:settings:1187254549828882562>",
                                   description="Change the category for pvc.",
                                   value="7"),
              discord.SelectOption(label="PVC Role Permissions",
                                   emoji="<:settings:1187254549828882562>",
                                   description="Set Role Permissions in PVC.",
                                   value="8") ,                   
              discord.SelectOption(label="Public PVC",
                                   emoji="<:settings:1187254549828882562>",
                                   description="Set Public PVC Settings.",
                                   value="9")                     
          ],
          custom_id="pvc_setings_select")
      async def pvc_setings_select(self, interaction: discord.Interaction,
                                   select: discord.ui.Select):
        selection = int(select.values[0])

        # Main Menu
        if selection == 0:
          embed, view = await Settings.setupMessage()
          view.user_id = self.user_id
          view.message = self.message
          await interaction.response.edit_message(embed=embed, view=view)
          return

        # PVC Status
        elif selection == 1:
          # Switching the pvc status
          if client.data[interaction.guild.id]['pvc']:
            await client.db.execute('UPDATE guilds SET pvc = $1 WHERE id = $2',
                                    False, interaction.guild.id)
            client.data[interaction.guild.id]['pvc'] = False

          else:
            await client.db.execute('UPDATE guilds SET pvc = $1 WHERE id = $2',
                                    True, interaction.guild.id)
            client.data[interaction.guild.id]['pvc'] = True

          # Updating the original message
          embed, view = await Settings.pvcSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.response.edit_message(embed=embed, view=view)
          return

        # PVC Coin/Name
        elif selection == 2:
          # Modal to update the pvc coin/name
          modal = multiInputModal(
              ["Enter the pvc coin name.", "Enter the pvc coin symbol."],
              ["Enter coin name.", "Enter coin symbol."], [1, 1], [None, None] , [ pvc_coin(interaction.guild.id)[1] ,  pvc_coin(interaction.guild.id)[0] ])
          modal.title = "PVC Coin/Name Settings"
          await interaction.response.send_modal(modal)
          await modal.wait()
          # Updating the pvc Coin/Name
          client.data[interaction.guild.id]['pvc_name'] = modal.values[0]
          client.data[interaction.guild.id]['pvc_coin'] = modal.values[1]
          await client.db.execute(
              'UPDATE guilds SET pvc_name = $1 WHERE id = $2', modal.values[0],
              interaction.guild.id)
          await client.db.execute(
              'UPDATE guilds SET pvc_coin = $1 WHERE id = $2', modal.values[1],
              interaction.guild.id)

          # Updating the original message
          embed, view = await Settings.pvcSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return

        # PVC Rate
        elif selection == 3:
          modal = singleInputModal("Rate/hr for Pvc",
                                   "Input should be in Numbers", 1, None , str(client.data[interaction.guild.id]['rate']) )
          modal.title = "PVC Rate Settings"
          await interaction.response.send_modal(modal)
          await modal.wait()
          # Checking if the input is a number and updating the rate in database
          if modal.value:
            has_value_error = False
            try:
              value = int(modal.value)
            except Exception:
              has_value_error = True
            if has_value_error:
              await interaction.followup.send("Rate/hr should be in numbers.")
              return
            else:
              client.data[interaction.guild.id]['rate'] = value
              await client.db.execute(
                  'UPDATE guilds SET rate = $1 WHERE id = $2', value,
                  interaction.guild.id)

            # Updating the original message
            embed, view = await Settings.pvcSettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return

        # PVC Limits
        elif selection == 4:
          # Modal to update the limits for PVC creation
          modal = multiInputModal([
              "Enter the min time limit for pvc(in hrs)",
              "Enter the max time limit for pvc(in hrs)"
          ], [
              "Min input should be in whole numbers",
              "Max input should be in whole numbers"
          ], [1, 1], [None, None] , [ str(client.data[interaction.guild.id]['pvc_min']) , str(client.data[interaction.guild.id]['pvc_max']) ])
          modal.title = "PVC Limits Settings"
          await interaction.response.send_modal(modal)
          await modal.wait()

          # Checking if the inputs are valid and updating the PVC limits in database
          has_value_error = False
          for value in modal.values:
            try:
              value = int(value)
            except Exception:
              has_value_error = True

          if has_value_error:
            await interaction.followup.send("Invalid input detected.",
                                            ephemeral=True)
            return
          else:
            client.data[interaction.guild.id]['pvc_min'] = int(modal.values[0])
            client.data[interaction.guild.id]['pvc_max'] = int(modal.values[1])
            await client.db.execute(
                'UPDATE guilds SET pvc_min = $1 WHERE id = $2',
                int(modal.values[0]), interaction.guild.id)
            await client.db.execute(
                'UPDATE guilds SET pvc_max = $1 WHERE id = $2',
                int(modal.values[1]), interaction.guild.id)

          # Updating the original message
          embed, view = await Settings.pvcSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return

        # PVC Commands Channel
        elif selection == 5:

          async def update_pvc_channel(interaction):
            data = pvc_channel_select.values
            if len(data) == 0:
              await client.db.execute(
                  'UPDATE guilds SET pvc_channel = $1 WHERE id = $2', None,
                  interaction.guild.id)
              client.data[interaction.guild.id]["pvc_channel"] = None
            else:
              await client.db.execute(
                  'UPDATE guilds SET pvc_channel = $1 WHERE id = $2',
                  data[0].id, interaction.guild.id)
              client.data[interaction.guild.id]["pvc_channel"] = data[0].id
            await interaction.response.edit_message(
                embed=bembed("PVC Commands Channel updated."), view=None)
            view1.stop()

          pvc_channel_select = discord.ui.ChannelSelect(
              channel_types=[discord.ChannelType.text],
              placeholder="Select a PVC command channel.",
              min_values=0,
              max_values=1,
              default_values= [ interaction.guild.get_channel(client.data[interaction.guild.id]["pvc_channel"])] if client.data[interaction.guild.id]["pvc_channel"] else None )
          pvc_channel_select.callback = update_pvc_channel

          view1 = discord.ui.View().add_item(pvc_channel_select)
          await interaction.response.send_message(
              embed=bembed("Use the dropdown below."),
              view=view1,
              ephemeral=True)
          await view1.wait()

          # Updating the original message
          embed, view = await Settings.pvcSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return

        # Join To Create PVC Channel
        elif selection == 6:

          # Logic to update the join to create pvc channel
          async def update_pvc_channel(interaction):
            data = pvc_voice_channel_select.values
            if len(data) == 0:
              await client.db.execute(
                  'UPDATE guilds SET pvc_vc = $1 WHERE id = $2', None,
                  interaction.guild.id)
              client.data[interaction.guild.id]["pvc_vc"] = None
            else:
              await client.db.execute(
                  'UPDATE guilds SET pvc_vc = $1 WHERE id = $2', data[0].id,
                  interaction.guild.id)
              client.data[interaction.guild.id]["pvc_vc"] = data[0].id
            await interaction.response.edit_message(
                embed=bembed("Join to create PVC Channel updated."), view=None)
            view1.stop()

          # Ephemeral view to select the join to create pvc channel
          pvc_voice_channel_select = discord.ui.ChannelSelect(
              channel_types=[discord.ChannelType.voice],
              placeholder="Select a join to create PVC Channel.",
              min_values=0,
              max_values=1,
              default_values= [ interaction.guild.get_channel(client.data[interaction.guild.id]["pvc_vc"])] if client.data[interaction.guild.id]["pvc_vc"] else None
              )
          pvc_voice_channel_select.callback = update_pvc_channel
          view1 = discord.ui.View().add_item(pvc_voice_channel_select)

          # Sending the ephermeral message
          await interaction.response.send_message(
              embed=bembed("Use the dropdown below."),
              view=view1,
              ephemeral=True)
          await view1.wait()

          # Updating the original message
          embed, view = await Settings.pvcSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return

        # PVC Category
        elif selection == 7:
          # Logic to update the pvc category
          async def update_pvc_category(interaction):
            data = pvc_category_select.values
            if len(data) == 0:
              await client.db.execute(
                  'UPDATE guilds SET pvc_category = $1 WHERE id = $2', None,
                  interaction.guild.id)
              client.data[interaction.guild.id]["pvc_category"] = None
            else:
              await client.db.execute(
                  'UPDATE guilds SET pvc_category = $1 WHERE id = $2',
                  data[0].id, interaction.guild.id)
              client.data[interaction.guild.id]["pvc_category"] = data[0].id
            await interaction.response.edit_message(
                embed=bembed("PVC Category updated."), view=None)
            view1.stop()

          pvc_category_select = discord.ui.ChannelSelect(
              channel_types=[discord.ChannelType.category],
              placeholder="Select a PVC's Category",
              min_values=0,
              max_values=1,
              default_values= [ interaction.guild.get_channel(client.data[interaction.guild.id]["pvc_category"])] if client.data[interaction.guild.id]["pvc_category"] else None )
          pvc_category_select.callback = update_pvc_category
          view1 = discord.ui.View().add_item(pvc_category_select)
          await interaction.response.send_message(
              embed=bembed("Use the dropdown below."),
              view=view1,
              ephemeral=True)
          await view1.wait()


          # Updating the original message
          embed, view = await Settings.pvcSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return
        
        # PVC Role Permissions
        elif selection == 8:

          async def button_callback(interaction):
            role = pvc_permission_role_select.values
            allowed_perms = pvc_allowed_permissions_select.values
            denied_perms = pvc_denied_permissions_select.values

            if not client.data[interaction.guild.id]["pvc_perms"]  :
              client.data[interaction.guild.id]["pvc_perms"] = {}

            if len(role) == 0:
              await interaction.response.send_message(
                  embed=bembed("No role selected."),
                  ephemeral=True)
              return
            elif len(allowed_perms) == 0 and len(denied_perms) == 0:
              client.data[interaction.guild.id]["pvc_perms"].pop(
                  str(role[0].id), None)
              await client.db.execute(
                  'UPDATE guilds SET pvc_perms = $1 WHERE id = $2',
                  client.data[interaction.guild.id]["pvc_perms"],
                  interaction.guild.id)
              await interaction.response.edit_message(
                  embed=bembed("Role permissions reset."), view=None)
              view1.stop()
              return
            elif list(set(allowed_perms).intersection(denied_perms)):
              await interaction.response.send_message(
                  embed=bembed(
                      "You can't allow and deny the same permission. remove the common permissions from one of the options."),
                  ephemeral=True
              )
              return
            else :
              client.data[interaction.guild.id]["pvc_perms"][str(role[0].id)] = {
                  "allow": discord.Permissions(**{ i : True for i in allowed_perms}).value,
                  "deny": discord.Permissions(**{ i : True for i in denied_perms}).value
              }
              await client.db.execute(
                  'UPDATE guilds SET pvc_perms = $1 WHERE id = $2',
                  client.data[interaction.guild.id]["pvc_perms"],
                  interaction.guild.id)
              
              await interaction.response.edit_message(
                  embed=bembed("Role permissions updated."), view=None)
              view1.stop()
              return
             
          async def pvc_allowed_permissions_select_callback(interaction) :
            await interaction.response.defer()
          
          async def pvc_denied_permissions_select_callback(interaction) :
            await interaction.response.defer()
          
          async def pvc_permission_role_select_callback(interaction) :
            await interaction.response.defer()
          
          
          pvc_permission_role_select = discord.ui.RoleSelect(
              placeholder="Select a role to set permissions for PVC.")
          pvc_permission_role_select.callback = pvc_permission_role_select_callback

          all_perms = discord.Permissions.voice()
          # all_perms.view_channel = True
          options = [discord.SelectOption(label=perm[0].replace('_', ' ').title() , value=perm[0]) for perm in all_perms if perm[1] == True]
          options.insert(0,discord.SelectOption(label="View Channel", value="read_messages"))

          pvc_allowed_permissions_select = discord.ui.Select(
              placeholder="Select the permissions to allow for the role.",
              options= options ,
              min_values=1,
              max_values= min(25,len(options)),
              custom_id="pvc_allowed_permissions_select")
          pvc_allowed_permissions_select.callback = pvc_allowed_permissions_select_callback

          pvc_denied_permissions_select = discord.ui.Select(
              placeholder="Select the permissions to deny for the role.",
              options= options,
              min_values=1,
              max_values=min(25,len(options)),
              custom_id="pvc_denied_permissions_select")
          pvc_denied_permissions_select.callback = pvc_denied_permissions_select_callback
          
          view1 = discord.ui.View().add_item(pvc_permission_role_select).add_item(pvc_allowed_permissions_select).add_item(pvc_denied_permissions_select)
          button = discord.ui.Button(style=discord.ButtonStyle.green, label="Done")
          button.callback = button_callback
          view1.add_item(button)
          await interaction.response.send_message(
              embed=bembed("Use the dropdown below.").set_footer(text="Select the role and remove all Allow/Deny permissions to reset the role permissions."),
              view=view1,
              ephemeral=True)
          await view1.wait()
          
          # Updating the original message
          embed, view = await Settings.pvcSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return
        
        # Public PVC
        elif selection == 9:
          modal = multiInputModal([
              "Vc limit (100 mean unlimited , 0 mean Off)",
          ], [
              "Vc limit input should be in numbers",
          ], [1], [None] , [ str(client.data[interaction.guild.id]['pvc_public']) ])
          modal.title = "Public Limits Settings"
          await interaction.response.send_modal(modal)
          await modal.wait()

          # Checking if the inputs are valid and updating the PVC limits in database
          has_value_error = False
          for value in modal.values:
            try:
              value = int(value)
              if value < 0:
                has_value_error = True
            except Exception:
              has_value_error = True

          if has_value_error:
            await interaction.followup.send("Invalid input detected.",
                                            ephemeral=True)
            return
          else:
            client.data[interaction.guild.id]['pvc_public'] = int(modal.values[0])
            await client.db.execute(
                'UPDATE guilds SET pvc_public = $1 WHERE id = $2',
                int(modal.values[0]), interaction.guild.id)
            
          # Updating the original message
          embed, view = await Settings.pvcSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return
          
        else:
          await interaction.response.send_message(embed=bembed(
              f"<:pixel_error:1187995377891278919> Interaction Failed: Unknown error"
          ),
                                                  ephemeral=True)
          return

    return embed, pvcSettingsView(guild)
 
  ################################################################################### Market Settings Message ########################################################################
  async def marketSettingsMessage(guild):
    # Fetching the pvc status for guild (on/off)
    if client.data[guild.id]['market'] and client.data[guild.id]['market']['status'] is True:
      market_enabled = True
    else:
      market_enabled = False
    market_status = "`🟢`" if market_enabled else "`🔴`"

    stocks = client.data[guild.id]['market']['stocks'] if client.data[guild.id]['market'] else 0

    # Creating the embeded message for Merket settings
    embed = discord.Embed(title="Market Settings")
    embed.description = f"Market Status - {market_status}\nTotal Stocks - 📈 {stocks:,}" # + "Symbol - 📈\nName - **Feature yet unavailable**"
    # 

    # Creating the view for PVC settings
    class marketSettingsView(discord.ui.View):

      def __init__(self, guild):
        super().__init__(timeout=None)
        self.client = client
        self.guild = guild
        self.user_id = None
        self.message = None

      async def interaction_check(self, interaction: discord.Interaction):

        if interaction.user.id == self.user_id:
          return True
        else:
          await interaction.response.send_message(embed=discord.Embed(
              description=
              "This is not your panel. You need to run the command yourself.",
              color=0x2b2c31),
                                                  ephemeral=True)
          return False

      async def on_timeout(self):
        for item in self.children:
          item.disabled = True
        content = self.message.content[:-18] + "**[** Inactive **]**"
        await self.message.edit(content=content, view=self)

        """
              discord.SelectOption(
                  label="Market Symbol/Name",
                  emoji="<:settings:1187254549828882562>",
                  description="Change the name or symbol of your stock.",
                  value="3")
        """
      @discord.ui.select(
          placeholder="Select a setting to change.",
          options=[
              discord.SelectOption(label="Main menu",
                                   emoji="<:Backtomenu:1187504974226268211>",
                                   description="Go back to main menu page.",
                                   value="0"),
              discord.SelectOption(
                  label="View Market Stats",
                  emoji="<:settings:1187254549828882562>",
                  description="View the current status of server economy and the market.",
                  value="1"
              ),
              discord.SelectOption(
                  label="Market Status",
                  emoji="<:settings:1187254549828882562>",
                  description="Enable or disable the market for the server.",
                  value="2"),
              discord.SelectOption(
                  label="Total Stocks",
                  emoji="<:settings:1187254549828882562>",
                  description="Change the number of stocks the market is open at.",
                  value="3")
          ],
              custom_id="market_setings_select")
      async def market_setings_select(self, interaction: discord.Interaction,
                                   select: discord.ui.Select):
        selection = int(select.values[0])

        # Main Menu
        if selection == 0:
          embed, view = await Settings.setupMessage()
          view.user_id = self.user_id
          view.message = self.message
          await interaction.response.edit_message(embed=embed, view=view)
          return
        
        # Economy stats
        if selection == 1:
          docs = await client.db.fetchrow("SELECT SUM(cash + bank) as economy , SUM(pvc) as pvc, SUM(stocks) as stocks FROM users WHERE guild_id = $1;", interaction.guild.id)
          total_economy = docs['economy']
          sold_stocks = docs['stocks']
          stocks_left = client.data[interaction.guild.id]['market']['stocks'] - sold_stocks
          message = f"The server stats of **{interaction.guild.name}** are as follows:\n- The total amount of economy in  the server is {coin(interaction.guild.id)} {total_economy:,}.\n- The total amount of {pvc_coin(interaction.guild.id)[1]} in the server is {pvc_coin(interaction.guild.id)[0]} {docs['pvc']:,}.\n"
          if client.data[interaction.guild.id]['market'] and client.data[interaction.guild.id]['market']['status'] is True: 
            current_price = math.ceil((total_economy/max(1, stocks_left)) / 2)
            message = message + f"- The total amount of shares sold in this server is 📈 {sold_stocks:,} and the current stock price is {coin(interaction.guild.id)} {current_price:,}" + f" with a total of 📈 {stocks_left:,} in the market." if stocks_left >= 0 else "."
          await interaction.response.send_message(message, ephemeral=True)

        # Market Status
        elif selection == 2:
          # Switching the Market status
          if client.data[interaction.guild.id]['market'] and client.data[interaction.guild.id]['market']['status'] is True:
            stocks = self.client.data[interaction.guild.id]['market']['stocks']
            await self.client.db.execute('UPDATE guilds SET market = $1 WHERE id = $2', {"status": False,"stocks": stocks}, interaction.guild.id )
            self.client.data[interaction.guild.id]['market'] = { 'status' : False , 'stocks' : stocks}
          else:
            stocks = self.client.data[interaction.guild.id]['market']['stocks'] if self.client.data[interaction.guild.id]['market'] else 100000
            await self.client.db.execute('UPDATE guilds SET market = $1 WHERE id = $2', {"status": True,"stocks": stocks}, interaction.guild.id )
            self.client.data[interaction.guild.id]['market'] = { 'status' : True , 'stocks' : stocks}
          """
        # Market symblol/stock's name
        elif selection == 3:
          return await interaction.followup.send("This is underdevelopment as of now.", ephemeral=True)
          # Modal to update the pvc coin/name
          modal = multiInputModal(
              ["Enter the stock's name.", "Enter the stock's symbol."],
              ["Enter stock name.", "Enter stock symbol."], [1, 1], [15, 25] , [ None ,  "📈"])
          modal.title = "Market symbol/stock's name settings"
          await interaction.response.send_modal(modal)
          await modal.wait()
          # Updating the pvc Coin/Name
          client.data[interaction.guild.id]['stock_name'] = modal.values[0]
          client.data[interaction.guild.id]['stock_symbol'] = modal.values[1]
          await client.db.execute(
              'UPDATE guilds SET stock_name = $1 WHERE id = $2', modal.values[0],
              interaction.guild.id)
          await client.db.execute(
              'UPDATE guilds SET stock_symbols = $1 WHERE id = $2', modal.values[1],
              interaction.guild.id)

          # Updating the original message
          embed, view = await Settings.marketSettingsMessage(self.guild)
          view.user_id = self.user_id
          view.message = self.message
          await interaction.message.edit(embed=embed, view=view)
          return
          """
        elif selection == 3:
          modal = singleInputModal("Total Number of Stocks for Market.",
                                   "Input should be in Numbers", 1, None , str(client.data[interaction.guild.id]['market']['stocks']) if  client.data[interaction.guild.id]['market'] else "0")
          modal.title = "Total Stocks Settings"
          await interaction.response.send_modal(modal)
          await modal.wait()
          # Checking if the input is a number and updating the rate in database
          if modal.value:
            has_value_error = False
            try:
              value = int(modal.value)
            except Exception:
              has_value_error = True
            if has_value_error:
              await interaction.followup.send("Stock amount should be in numbers.")
              return
            else:
              status = self.client.data[interaction.guild.id]['market']['status']
              await self.client.db.execute('UPDATE guilds SET market = $1 WHERE id = $2', {"status": status,"stocks": value}, interaction.guild.id )
              self.client.data[interaction.guild.id]['market'] = { 'status' : status , 'stocks' : value}

            # Updating the original message
            embed, view = await Settings.marketSettingsMessage(self.guild)
            view.user_id = self.user_id
            view.message = self.message
            await interaction.message.edit(embed=embed, view=view)
            return
        else:
          await interaction.response.send_message(embed=bembed(
              f"<:pixel_error:1187995377891278919> Interaction Failed: Unknown error"
          ),
                                                  ephemeral=True)
          return
        
        # Updating the original message
        embed, view = await Settings.marketSettingsMessage(self.guild)
        view.user_id = self.user_id
        view.message = self.message
        await interaction.response.edit_message(embed=embed, view=view)
        return
      
    return embed, marketSettingsView(guild)

  @commands.hybrid_command(name="setup",
                           description="Setup the bot for your server",
                           aliases=[ "config" , "start", 'setting'])
  @commands.guild_only()
  @commands.guild_only()
  @commands.check(check_perms)
  @commands.cooldown(1, 5, commands.BucketType.member)
  async def setup(self, ctx , page : int = 0):

    await ctx.defer()

    if page == 1 :
      embed , view = await Settings.botSettingsMessage(ctx.guild)
    elif page == 2 :
      embed , view = await Settings.economySettingsMessage(ctx.guild)
    elif page == 3 :
      embed , view = await Settings.gameSettingsMessage(ctx.guild)
    elif page == 4 :
      embed , view = await Settings.pvcSettingsMessage(ctx.guild)
    elif page == 5:
      embed, view = await Settings.marketSettingsMessage(ctx.guild)
    else :
      embed, view = await self.setupMessage()
      

    view.user_id = ctx.author.id
    view.message = await ctx.send(
        content=
        f"> **Setting up {client.user.display_name}** •  **[** {ctx.author.name} **]** •  **[** Active **]**",
        embed=embed,
        view=view)
    
  @commands.hybrid_command(name="prefix", description="Change the bot prefix")
  @commands.guild_only()
  @commands.check(check_perms)
  @commands.cooldown(1, 5, commands.BucketType.member)
  async def prefix(self, ctx, prefix: str = None):

    if not prefix:
      await ctx.send(embed=bembed(
          f"Current prefix for this server is `{ctx.clean_prefix}`"
      ))
      return

    if len(prefix) > 1:
      await ctx.send(embed=bembed("Prefix can't be more than 1 characters."))
      return

    client.data[ctx.guild.id]['prefix'] = prefix
    await client.db.execute('UPDATE guilds SET prefix = $1 WHERE id = $2',
                            prefix, ctx.guild.id)
    await ctx.send(embed=bembed(f"Prefix updated to `{prefix}`"))
      


async def setup(client):
  await client.add_cog(Settings(client))
