import os
import random
import discord
import time
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

client = discord.Client()


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name == GUILD:
            break

    print(f'{client.user} has connected to Discord !',
          f'{guild.name} (id: {guild.id})')

message_log = []

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    log = f"User {message.author} said: '{message.content}'"
    print(log)
    message_log.append(log)
    hello_message = [
        'Bonjour !',
        'Hello !',
        'Salut Salut !',
        'Salutations !'
    ]
    bot_name = str(client.user).split("#")[0]
    if bot_name in message.content:
        time.sleep(1)
        response = random.choice(hello_message)
        await message.channel.send(response)
    elif message.content == 'raise-exception':
        raise discord.DiscordException

    print(message_log)

client.run(TOKEN)