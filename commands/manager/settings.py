import discord
from discord.ext import commands
from database import *


class singleInputModal(discord.ui.Modal, title='...'):

  def __init__(self, question, placeholder,min=None, max=None , defult = None):
    super().__init__()
    self.question = question
    self.placeholder = placeholder
    self.min = min
    self.max = max
    self.value = None
    self.defult = defult
    self.input = discord.ui.TextInput(label=self.question,
                                      placeholder=self.placeholder,
                                      min_length=self.min,
                                      max_length=self.max,
                                      default= self.defult
                                      )
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
               max: list , defults : list = None):
    super().__init__()
    self.questions = questions
    self.placeholders = placeholders
    self.defults = defults
    if not defults :
      self.defults = [None] * len(questions)
    self.values = []

    for i in range(len(questions)):
      self.input = discord.ui.TextInput(
          label=self.questions[i],
          placeholder=self.placeholders[i],
          default= self.defults[i],
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
          await interaction.response.send_message(
              f"This feature is not ready yet", ephemeral=True)
          return
        elif main_selection == 4:
          embed, view = await Settings.pvcSettingsMessage(interaction.guild)
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
    bot_prefix = client.data[guild.id]['prefix'] or defult_prefix

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
                                   "The length of input should be 1", 0, 1 , client.data[interaction.guild.id]["prefix"] or defult_prefix)
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
    embed.description = f"Economy Coin - `{economy_coin}`"
    embed.add_field(name="Automoney Channel(s)",
                    value=automoney_channels,
                    inline=False)
    embed.add_field(
        name="Automoney Settings",
        value=
        f"Auto Money(AM) Cash/min : **0-{automoney_amount_cash}**\nAuto Money(AM) pvc/min : **0-{automoney_amount_pvc}**",
        inline=False)

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
                  value="3")
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
                                   "Paste your coin.", 1, None , coin(interaction.guild.id) )
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
            await interaction.followup.send("No input", ephemeral=True)

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
        else:
          await interaction.response.send_message(embed=bembed(
              f"<:pixel_error:1187995377891278919> Interaction Failed: Unknown error"
          ),
                                                  ephemeral=True)
          return

    return embed, economySettingsView(guild)


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
    embed.description = f"PVC Status - {pvc_status}\nCoin - `{pvc_coin_symbol}`\nCoin Name - `{pvc_coin_name}`\n\nRate/hr :  - **{pvc_coin_rate}**\n\nMin Time Limit - **{pvc_min_time}** Hrs\nMax Time Limit - **{pvc_max_time}** Hrs\n(0 means no limit)"
    embed.add_field(name="PVC Commands Channel",
                    value=pvc_commands_channels,
                    inline=False)
    embed.add_field(name="Join To Create PVC Channel",
                    value=join_to_create_pvc_channel,
                    inline=False)
    embed.add_field(name="PVC Category", value=pvc_category, inline=False)

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
                                   value="7")
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

        else:
          await interaction.response.send_message(embed=bembed(
              f"<:pixel_error:1187995377891278919> Interaction Failed: Unknown error"
          ),
                                                  ephemeral=True)
          return

    return embed, pvcSettingsView(guild)

  @commands.hybrid_command(name="setup",
                           description="Setup the bot for your server",
                           aliases=["prefix" , "config" , "start"])
  @commands.guild_only()
  @commands.guild_only()
  @commands.check(check_perms)
  @commands.cooldown(1, 5, commands.BucketType.member)
  async def setup(self, ctx):

    await ctx.defer()
    embed, view = await self.setupMessage()
    view.user_id = ctx.author.id
    view.message = await ctx.send(
        content=
        f"> **Setting up {self.client.user.display_name}** •  **[** {ctx.author.name} **]** •  **[** Active **]**",
        embed=embed,
        view=view)


async def setup(client):
  await client.add_cog(Settings(client))
