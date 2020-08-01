import os
import typing
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import isthereanydeal
import ggdeals
import howlongtobeat
import wallhaven
import nasa as nasapy

load_dotenv()

cmdlist = (
    ('.help', 'Shows this message, optional parameters [amount] [query] [date]', False),
    ('.ping', 'Shows bot latency', False),
    ('-', isthereanydeal.home_url, False),
    ('.itad', 'Shows bundles and special deals', True),
    ('.itad free', 'Shows giveaways', True),
    ('.itad [game]', 'Shows game information and deals', True),
    ('-', ggdeals.home_url, False),
    ('.ggd', 'Shows best deals', True),
    ('.ggd free', 'Shows freebies', True),
    ('-', howlongtobeat.home_url, False),
    ('.hltb [game]', 'Gives game completion times', True),
    ('-', wallhaven.home_url, False),
    ('.wh', 'Gets featured wallpapers', False),
    ('.wh p [amount] [query]', 'Gets __p__ertinent wallpaper(s)', True),
    ('.wh r [amount] [query]', 'Gets __r__andom wallpaper(s)', True),
    ('.wh l [amount] [query]', 'Gets __l__atest wallpaper(s)', True),
    ('.wh v [amount] [query]', 'Gets most __v__iewed wallpaper(s)', True),
    ('.wh f [amount] [query]', 'Gets most __f__avored wallpaper(s)', True),
    ('.wh t [amount] [query]', 'Gets __t__op wallpaper(s)', True),
    ('-', nasapy.home_url, False),
    ('.nasa [date]', '(date as YYYY-MM-DD) Gets Astronomy Picture of the Day from NASA', False)
)

error_command_unknown = "I couldn't understand the command."
error_command_fail = "The command didn't work."

discord_token = os.getenv('DISCORD_TOKEN')
nasa_api_key = os.getenv('NASA_API_KEY')
itad_api_key = os.getenv('ITAD_API_KEY')
itad_region = os.getenv('ITAD_REGION')

bot_change_presence_delay = 600

bot = commands.Bot(command_prefix='.', case_insensitive=True)
bot.remove_command('help')


@bot.event
async def on_ready():
    print('We have logged in as {0.user}'.format(bot))


@bot.command(pass_context=True)
async def help(ctx):
    print_out(ctx)
    embed = discord.Embed()

    for cmd in cmdlist:
        embed.add_field(
            name=cmd[0],
            value=cmd[1],
            inline=cmd[2]
        )

    await ctx.send(embed=embed)


@bot.command()
@commands.is_owner()
async def clear(ctx, amount: typing.Optional[int] = 2):
    print_out(ctx)
    await ctx.channel.purge(limit=amount)


@bot.command()
@commands.is_owner()
async def logout(ctx):
    print_out(ctx)
    await ctx.send("I'll be back.")
    await bot.logout()


@bot.command()
async def ping(ctx):
    print_out(ctx)
    await ctx.send(
        embed=discord.Embed(

        ).add_field(
            name='Bot Latency:',
            value='{} ms'.format(round(bot.latency * 1000))
        ).set_footer(
            text='@{0.author}'.format(ctx)
        )
    )


@bot.command()
async def itad(ctx, *, command: typing.Optional[str]):
    print_out(ctx)

    if not command:
        await ctx.send(embed=isthereanydeal.bundles_specials())

    elif command.lower() == 'free':
        await ctx.send(embed=isthereanydeal.specials('giveaway'))

    elif command:
        embed = isthereanydeal.search_game(itad_api_key, command, itad_region)
        if not embed:
            await ctx.send(error_command_fail)
        else:
            await ctx.send(embed=embed)

    else:
        await ctx.send(error_command_unknown)


@itad.error
async def itad_error(ctx, error):
    await ctx.send(error)


@bot.command()
async def ggd(ctx, *, command: typing.Optional[str]):
    print_out(ctx)

    if not command:
        await ctx.send(embed=ggdeals.best_deals())

    elif command.lower() == 'free':
        await ctx.send(embed=ggdeals.search_freebies())

    else:
        await ctx.send(error_command_unknown)


@ggd.error
async def ggd_error(ctx, error):
    await ctx.send(error)


@bot.command()
async def hltb(ctx, *, game):
    print_out(ctx)
    embed = howlongtobeat.search_game(game)
    if not embed:
        await ctx.send(error_command_fail)
    else:
        await ctx.send(embed=embed)


@bot.command()
async def wh(ctx, command: typing.Optional[str], amount: typing.Optional[int] = 1, *, query: typing.Optional[str]):
    print_out(ctx)

    if not command:
        for embed in wallhaven.featured():
            await ctx.send(embed=embed)

    elif command.lower() == 'p':
        for embed in wallhaven.relevance(query)[:amount]:
            await ctx.send(embed=embed)

    elif command.lower() == 'r':
        for embed in wallhaven.random(query)[:amount]:
            await ctx.send(embed=embed)

    elif command.lower() == 'l':
        for embed in wallhaven.date_added(query)[:amount]:
            await ctx.send(embed=embed)

    elif command.lower() == 'v':
        for embed in wallhaven.views(query)[:amount]:
            await ctx.send(embed=embed)

    elif command.lower() == 'f':
        for embed in wallhaven.favorites(query)[:amount]:
            await ctx.send(embed=embed)

    elif command.lower() == 't':
        for embed in wallhaven.toplist(query)[:amount]:
            await ctx.send(embed=embed)

    else:
        await ctx.send(error_command_unknown)


@wh.error
async def wp_error(ctx, error):
    await ctx.send(error)


@bot.command()
async def nasa(ctx, *, date: typing.Optional[str]):
    print_out(ctx)
    await ctx.send(embed=nasapy.get_apod(nasa_api_key, date))


@nasa.error
async def nasa_error(ctx, error):
    await ctx.send(error)


async def bot_change_presence(delay):
    await bot.wait_until_ready()
    print('Starting bot_change_presence')

    while not bot.is_closed():
        print('Running bot_change_presence')
        size = len(bot.guilds)
        msg = 'servers' if size > 1 else 'server'
        await bot.change_presence(activity=discord.Game('on {} {}'.format(size, msg)))
        await asyncio.sleep(delay)


def print_out(ctx):
    print('[{0.message.created_at}] {0.author}: {0.message.content}'.format(ctx))


bot.loop.create_task(bot_change_presence(bot_change_presence_delay))
bot.run(discord_token)
