import discord

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