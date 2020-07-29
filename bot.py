import os
import typing
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import isthereanydeal
import howlongtobeat
import wallhaven
import nasa as nasa_py

load_dotenv()

cmdlist = (
    ('.help', 'Shows this message, optional parameters [amount] [query] [date]', False),
    ('.ping', 'Shows bot latency', False),
    ('-', isthereanydeal.home_url, False),
    ('.itad', 'Shows bundles and special deals', True),
    ('.itad giveaway', 'Shows giveaways', True),
    ('.itad [game]', 'Shows game information and deals', True),
    ('-', howlongtobeat.home_url, False),
    ('.hltb [game]', 'Gives game completion times', False),
    ('-', wallhaven.home_url, False),
    ('.wh', 'Gets featured wallpapers', False),
    ('.wh p [amount] [query]', 'Gets __p__ertinent wallpaper(s)', True),
    ('.wh r [amount] [query]', 'Gets __r__andom wallpaper(s)', True),
    ('.wh l [amount] [query]', 'Gets __l__atest wallpaper(s)', True),
    ('.wh v [amount] [query]', 'Gets most __v__iewed wallpaper(s)', True),
    ('.wh f [amount] [query]', 'Gets most __f__avored wallpaper(s)', True),
    ('.wh t [amount] [query]', 'Gets __t__op wallpaper(s)', True),
    ('-', nasa_py.home_url, False),
    ('.nasa [date]', '(date as YYYY-MM-DD) Gets Astronomy Picture of the Day from NASA', False)
)

error_command_unknown = "I couldn't understand the command."

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
        await ctx.send(embed=itad_embed(isthereanydeal.bundles_specials()))

    elif command.lower() == 'giveaway':
        await ctx.send(embed=itad_embed_giveaway(isthereanydeal.specials('giveaway'), 'Giveaways'))

    elif command:
        dic = isthereanydeal.search_game(itad_api_key, command, itad_region)
        if not type(dic) is dict:
            for x in dic:
                await ctx.send('.itad {}'.format(x['title']))
        else:
            await ctx.send(embed=itad_embed_search(dic))
    else:
        await ctx.send(error_command_unknown)


def itad_embed(lis):
    embed = discord.Embed(
        title='Bundles and Special Deals',
        url=isthereanydeal.home_url
    )

    for li in lis:
        embed.add_field(
            name=li[0],
            value='{}\n{} ({}) [details]({})'.format(li[1], li[4], li[3], li[2]),
            inline=False
        )

    return embed


def itad_embed_giveaway(lis, command):
    embed = discord.Embed(
        title='Specials {}'.format(command),
        url=isthereanydeal.specials_url
    )

    for li in lis:
        embed.add_field(
            name=li[0],
            value='{}\n{} [details]({})'.format(li[1], li[4], li[2]),
            inline=True
        )

    return embed


def itad_embed_search(dic):
    embed = discord.Embed(
        title=dic['title'],
        url=dic['url_game']
    )

    embed.add_field(name='-', value='__Current Prices__', inline=False)

    for x in dic['prices_list']:
        embed.add_field(
            name=x['shop']['name'],
            value='{:.2f} {} ({}% off)\n{}'.format(x['price_new'], dic['currency'], x['price_cut'], x['url']),
            inline=True
        )

    embed.add_field(name='-', value='__Historical Low Prices__', inline=False)

    for x in dic['storelow_list']:
        embed.add_field(
            name=x['shop'],
            value='{:.2f} {}'.format(x['price'], dic['currency']),
            inline=True
        )

    return embed


@itad.error
async def itad_error(ctx, error):
    await ctx.send(error)


@bot.command()
async def hltb(ctx, *, game):
    print_out(ctx)

    dic = howlongtobeat.search_game(game)

    embed = discord.Embed(
        title=dic['title'],
        url=dic['url']
    ).set_thumbnail(
        url=dic['img_url']
    )

    labels = dic['labels']
    times = dic['times']
    for i in range(len(labels)):
        embed.add_field(
            name=labels[i],
            value=times[i] if len(times) > i else '-',
            inline=True
        )

    await ctx.send(embed=embed)


@bot.command()
async def wh(ctx, command: typing.Optional[str], amount: typing.Optional[int] = 1, *, query: typing.Optional[str]):
    print_out(ctx)

    if not command:
        for img in wallhaven.featured():
            await ctx.send(embed=wh_embed(img))

    elif command.lower() == 'p':
        for img in wallhaven.relevance(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command.lower() == 'r':
        for img in wallhaven.random(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command.lower() == 'l':
        for img in wallhaven.date_added(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command.lower() == 'v':
        for img in wallhaven.views(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command.lower() == 'f':
        for img in wallhaven.favorites(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command.lower() == 't':
        for img in wallhaven.toplist(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    else:
        await ctx.send(error_command_unknown)


def wh_embed(img):
    return discord.Embed(
        title=img,
        url=img
    ).set_image(
        url=img
    )


@wh.error
async def wp_error(ctx, error):
    await ctx.send(error)


@bot.command()
async def nasa(ctx, *, date: typing.Optional[str]):
    print_out(ctx)
    j = nasa_py.get_apod(nasa_api_key, date)
    await ctx.send(embed=get_nasa_apod_embed(j))


def get_nasa_apod_embed(j):
    return discord.Embed(
        title=j['title'],
        description=j['explanation'],
        url=j['url']
    ).set_image(
        url=j['hdurl']
    ).set_footer(
        text='{} | {}'.format(j['date'], j['copyright'])
    )


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
