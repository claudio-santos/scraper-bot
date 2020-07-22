import os
from dotenv import load_dotenv
import discord
import wallhaven

load_dotenv()

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!help'):
        await message.channel.send('!help = command list\n'
                                   '!wp = wallhaven featured')

    if message.content.startswith('!wp'):
        for img in wallhaven.featured():
            await message.channel.send(embed=discord.Embed(
                title=img,
                url=img
            ).set_image(url=img))

client.run(os.getenv('DISCORD_TOKEN'))