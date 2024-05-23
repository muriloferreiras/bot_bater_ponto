import discord
from discord.ext import commands
from datetime import datetime, timedelta
import asyncio

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
client = commands.Bot(command_prefix='!', intents=intents)

@client.command()
async def start(ctx: commands.Context):
    await ctx.channel.purge(limit=1)
    current_time = datetime.now()
    user = ctx.author.mention
    username = ctx.author.nick
    start_time_str = current_time.strftime("%H:%M %d/%m")
    guild = ctx.guild
    new_channel = await guild.create_text_channel(name=f"Point-{username}-{start_time_str}")
    await new_channel.set_permissions(ctx.guild.default_role, read_messages=False)
    await new_channel.set_permissions(ctx.author, read_messages=True)
    log_channel = guild.get_channel('INSERT_LOG_CHANNEL_ID_HERE')
    await log_channel.send(f'Start time recorded for {user}: {start_time_str}')
    await new_channel.send(f'Hello {user}, your hours are being recorded. Click on the `!stop` command to finish.')

@client.command()
async def stop(ctx: commands.Context):
    user = ctx.author.mention
    username = ctx.author.nick
    start_time = datetime.now()  # Define the interaction duration
    end_time = datetime.now()
    start_time_str = start_time.strftime("%H:%M %d/%m")
    end_time_str = end_time.strftime("%H:%M %d/%m")
    try:
        await ctx.send(f'{user}, you ended your shift at {end_time_str}')
        await ctx.send(f'All set, hours sent to the #recorded-hours channel. This channel will be deleted soon...')
        guild = ctx.guild
        log_channel = guild.get_channel('INSERT_LOG_CHANNEL_ID_HERE')
        await log_channel.send(f'End time recorded for {user}: {end_time_str}')
        time_diff = end_time - start_time
        hours, remainder = divmod(time_diff.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)
        formatted_time = "{:02}:{:02}".format(int(hours), int(minutes))
        recorded_channel = guild.get_channel('INSERT_HOURS_RECORDS_CHANNEL_ID_HERE')
        await recorded_channel.send(embed=discord.Embed(
            title=f'Hours of {username}',
            description=f'{user}'
                        f'\nStart time'
                        f'```\n {start_time_str}```'
                        f'\nEnd time'
                        f'```\n {end_time_str}```'
                        f'\nTotal hours'
                        f'```\n{formatted_time}```'
        ))
        await asyncio.sleep(8)
        await ctx.channel.delete()
    except discord.NotFound:
        pass

client.run("YOUR_TOKEN_HERE")
