import random
from typing import List

import re
import discord
from discord.ext import commands
from discord.ext import tasks
from dotenv import load_dotenv
import os
import modrinth

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='?', intents=intents)
souls_awakening_project = modrinth.Projects.ModrinthProject("WzNAv1Om")


@bot.event
async def on_ready():
    await bot.change_presence(status=discord.Status.online, activity=discord.Game('Assisting Beosti'))
    print("-----------------------")
    print("Ready to assist anyone!")
    print("-----------------------")
    periodic_task.start()


@tasks.loop(minutes=10)
async def periodic_task():
    try:
        await background_check_update()
    except Exception as e:
        print(f"Task exception at periodic task: {e}")


async def background_check_update():
    try:
        latest_version = souls_awakening_project.getLatestVersion().version
        cacheversions = get_cache_version()
        if latest_version != cacheversions:
            await new_version_announcement(souls_awakening_project)
        modify_cache_version(souls_awakening_project.getLatestVersion().version)
    except Exception as e:
        print(f"Task exception at the getting of latest update: {e}")


async def new_version_announcement(
        modrinthproject):  # Specific method to handle the announcement of having a new version for a mod
    announcement_update_channel = bot.get_channel(973320177817104394)
    allowed_mentions = discord.AllowedMentions(everyone=True)
    await announcement_update_channel.send(content="@everyone" +
                                                   "\nA mod got an update! Get in here!"
                                                   "\n" + "https://modrinth.com/mod/" + format_string(
        modrinthproject.getLatestVersion().name) +
                                                   "\n" + "Check the link for the changelog!",
                                           allowed_mentions=allowed_mentions)


def format_string(input_str):
    # Split the input string by spaces
    components = input_str.split()

    # Convert each component to lowercase
    components = [component.lower() for component in components]

    # Join the components with "/"
    formatted_str = '-'.join(components[:-1]) + '/version/' + components[-1]

    return formatted_str


def get_cache_version():
    file_path = 'publicids'
    with open(file_path, 'r') as file:
        content = file.read()

    # Retrieve the value of cacheversions using regular expressions
    matches = re.search(r"cacheversions\s*=\s*'([^']+)'", content)

    if matches:
        return matches.group(1)  # Return only the matched content within the quotes
    else:
        return None  # Return None if no match is found


def modify_cache_version(new_version):
    file_path = 'publicids'

    # Change the value of cacheversions to something else
    new_version_value = "new_version_value_here"

    with open(file_path, 'r') as file:
        content = file.read()

    # Replace the value of cacheversions with the new version value
    modified_content = re.sub(r"cacheversions\s*=\s*'([^']+)'", f"cacheversions = '{new_version}'", content)
    with open(file_path, 'w') as file:
        file.write(modified_content)


# Setup command for the role you can get yourself
@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    try:
        # Add custom emoji reactions
        emojis = ["🎬", "🦑", "🎤", "👀", "🎮", "🚨"]

        # Store the main message
        main_message = await ctx.send("Pick up your roles for pings here!:")

        # Store the reaction messages
        reaction_messages = [await ctx.send(f"{emoji}:{role}") for emoji, role in
                             zip(emojis, ["youtube", "manga", "streams", "sneak peek", "mod updates", "discord"])]

        # Add custom emoji reactions to reaction messages
        for reaction_message, emoji in zip(reaction_messages, emojis):
            await reaction_message.add_reaction(emoji)

        # Store message IDs and roles mapping in a database or a data structure
        roles_mapping = {
            "🎬": "videos",
            "🦑": "mangas",
            "🎤": "streams",
            "👀": "sneak peek",
            "🎮": "mod updates",
            "🚨": "discord"
        }
        roles_data[main_message.id] = roles_mapping
        roles_data.update({message.id: {emoji: role} for message, emoji, role in zip(reaction_messages, emojis,
                                                                                     ["videos", "mangas", "streams",
                                                                                      "sneak peek", "mod updates",
                                                                                      "discord"])})
    except commands.MissingPermissions:
        # User doesn't have the required permissions, handle it gracefully
        await print("Someone used a non usable command")


user_reactions = {}


@bot.event
async def on_raw_reaction_add(payload):
    await handle_reaction(payload, add=True)


@bot.event
async def on_raw_reaction_remove(payload):
    await handle_reaction(payload, add=False)


# Handles the reactions in general
async def handle_reaction(payload, add=True):
    # If the person reacting is the bot then exit
    if payload.user_id == bot.user.id:
        return
    channel = bot.get_channel(payload.channel_id)  # gets the channel id of the place reacting
    message = await channel.fetch_message(payload.message_id)  # get the message

    # If the reacted message is from the bot exit
    if message.author != bot.user:
        return
    roles_mapping = roles_data.get(message.id)

    if roles_mapping and payload.emoji.name in roles_mapping:
        role_name = roles_mapping[payload.emoji.name]

        # Get the role or create it if it doesn't exist
        role = discord.utils.get(message.guild.roles, name=role_name)
        if role is None:
            role = await message.guild.create_role(name=role_name)

        member = message.guild.get_member(payload.user_id)

        if role:
            if payload.message_id not in user_reactions:
                user_reactions[payload.message_id] = set()

            if add and payload.user_id not in user_reactions[payload.message_id]:
                # User does not have the role, add it
                await member.add_roles(role)

                # Add the user to the set of users who have reacted to this message
                user_reactions[payload.message_id].add(payload.user_id)
            elif not add and payload.user_id in user_reactions[payload.message_id]:
                # User has already reacted, remove the reaction and the role
                await member.remove_roles(role)
                user_reactions[payload.message_id].remove(payload.user_id)


# Store roles data in a dictionary
roles_data = {}
gif_database: List[str] = [
    'https://media1.tenor.com/m/CBxyvlf0CMoAAAAC/welcome-anime.gif',
    'https://media1.tenor.com/m/wZW05QUURk4AAAAC/welcome-anime.gif',
    'https://media1.tenor.com/m/aSEjob2tK08AAAAC/youre-welcome-you-are-welcome.gif',
    'https://media1.tenor.com/m/HNcG3X-Og7wAAAAC/welcome-anime.gif',
    'https://media1.tenor.com/m/uig4MIIEykoAAAAC/welcome-anime.gif'
]


@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name='seaman')
    channel_message = bot.get_channel(1173654611320651827)
    channel_role = bot.get_channel(1173652899788759162)
    role_channel_mention = channel_role.mention
    welcome_message = f"Welcome to Yuanno Inc. {member.mention} pick up your roles in {role_channel_mention}!"
    selected_gif = random.choice(gif_database)
    message_without_gif = f"{welcome_message}"

    await channel_message.send(message_without_gif)
    await channel_message.send(selected_gif)
    await member.add_roles(role)


@bot.command()
async def hello(ctx):
    await ctx.send("Hello, I am Assistant Blue! Ready to assist anyone!")


gif_database_money: List[str] = [
    'https://media1.tenor.com/m/VnZiBdemf9UAAAAC/watashi-ni-tenshi-money.gif',
    'https://media1.tenor.com/m/yeMLxusxRjMAAAAC/anime-money.gif',
    'https://media1.tenor.com/m/3udfRRClJFoAAAAC/anime-give-me.gif',
    'https://media1.tenor.com/m/TEBw4UwqVTgAAAAd/kikis-delivery-service-anime.gif',
    'https://media1.tenor.com/m/a-DcVEXq7aAAAAAC/alinarin-money.gif',
    'https://media1.tenor.com/m/Fc-Q_H_9Ye4AAAAC/pay-day-anime.gif',
    'https://media1.tenor.com/m/e5o0_lvYPM8AAAAC/tsunade-counting-money.gif'
]


@bot.command()
async def patreon(ctx):
    await ctx.send("Subscribe to Beosti's patreon for teasers, overall suport and "
                   "more!:\nhttps://www.patreon.com/Beosti")
    selected_gif = random.choice(gif_database_money)
    await ctx.send(selected_gif)


@bot.command()
async def soulsdocs(ctx):
    await ctx.send("Read some information about the Souls Awakening mod here!"
                   "\n<https://github.com/Beosti/souls-awakening/blob/master/GAMEPLAY.md>")


@bot.command()
async def soulscode(ctx):
    await ctx.send("You need the code for the souls awakening mod? Sure! Read this and you ready to go:"
                   "\n<https://github.com/Beosti/souls-awakening/blob/master/README.md>")


@bot.command()
async def bc(ctx):
    await ctx.send("At the current time Block Clover is going through a major rework taking some time!")


@bot.command()
async def code(ctx):
    await ctx.send("You want to see how I work? Sure! But check out my documentation first:"
                   "\n<https://github.com/Beosti/blue-assistant/blob/main/README.md>")


load_dotenv()
BOTTOKEN = os.getenv('BOTTOKEN')
bot.run(BOTTOKEN)
