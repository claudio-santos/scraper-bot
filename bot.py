import os
import typing
from dotenv import load_dotenv
import discord
from discord.ext import commands
import asyncio
import isthereanydeal
import howlongtobeat
import wallhaven

cmdlist = (
    ('.help', 'Shows this message, optional parameters [amount] [query]', False),
    ('.ping', 'Shows bot latency', False),
    ('.clear [amount]', 'Owner only: Clears newest channel messages', False),
    ('-', isthereanydeal.home_url, False),
    ('.itad', 'Shows bundles and special deals', True),
    ('.itad giveaways', 'Shows giveaways', True),
    ('-', howlongtobeat.home_url, False),
    ('.hltb [game]', 'Gives game completion times', False),
    ('-', wallhaven.home_url, False),
    ('.wh', 'Gets featured wallpapers', False),
    ('.wh relevant [amount] [query]', 'Gets relevant wallpaper(s)', True),
    ('.wh random [amount] [query]', 'Gets random wallpaper(s)', True),
    ('.wh latest [amount] [query]', 'Gets latest wallpaper(s)', True),
    ('.wh views [amount] [query]', 'Gets most viewed wallpaper(s)', True),
    ('.wh favorites [amount] [query]', 'Gets most favored wallpaper(s)', True),
    ('.wh top [amount] [query]', 'Gets top wallpaper(s)', True)
)

error_command_unknown = "I couldn't understand the command."

database = 'database.db'
check_new_bundles_specials_db_delay = 21600
bot_change_presence_delay = 600

load_dotenv()

bot = commands.Bot(command_prefix='.')
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
async def clear(ctx, amount: typing.Optional[int] = 100):
    print_out(ctx)
    await ctx.channel.purge(limit=amount)


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
async def itad(ctx, command: typing.Optional[str]):
    print_out(ctx)

    if not command:
        await ctx.send(embed=itad_embed(isthereanydeal.bundles_specials()))

    elif command == 'giveaway':
        await ctx.send(embed=itad_embed_compact(isthereanydeal.specials('giveaway'), 'Giveaways'))

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


def itad_embed_compact(lis, command):
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

    elif command == 'relevant':
        for img in wallhaven.relevance(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command == 'random':
        for img in wallhaven.random(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command == 'latest':
        for img in wallhaven.date_added(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command == 'views':
        for img in wallhaven.views(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command == 'favorites':
        for img in wallhaven.favorites(query)[:amount]:
            await ctx.send(embed=wh_embed(img))

    elif command == 'top':
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


# todo change env variable to a saved channel id in database
async def check_new_bundles_specials_db(db, delay):
    await bot.wait_until_ready()
    print('Starting check_new_bundles_specials_db')

    while not bot.is_closed():
        print('Running check_new_bundles_specials_db')
        lis = isthereanydeal.check_new_bundles_specials_db(database)
        if lis:
            await bot.get_channel(int(os.getenv('CHANNEL_ITAD'))).send(embed=itad_embed(lis))
        await asyncio.sleep(delay)


async def bot_change_presence(delay):
    await bot.wait_until_ready()
    print('Starting bot_change_presence')

    while not bot.is_closed():
        print('Running bot_change_presence')
        await bot.change_presence(activity=discord.Game('on {} server'.format(len(bot.guilds))))
        await asyncio.sleep(delay)


def print_out(ctx):
    print('[{0.message.created_at}] {0.author}: {0.message.content}'.format(ctx))


bot.loop.create_task(check_new_bundles_specials_db(database, check_new_bundles_specials_db_delay))
bot.loop.create_task(bot_change_presence(bot_change_presence_delay))
bot.run(os.getenv('DISCORD_TOKEN'))
