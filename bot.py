import os
from dotenv import load_dotenv
import discord
from discord.ext import commands
import typing
import isthereanydeal
import wallhaven

cmdlist = (
    ('.help', 'Shows this message, optional parameters [amount] [query]', False),
    ('.ping', 'Shows bot latency', False),
    ('.clear [amount]', 'Owner only: Clears newest channel messages', False),
    ('-', isthereanydeal.home_url, False),
    ('.itad', 'Shows bundles and special deals from isthereanydeal', False),
    ('-', wallhaven.home_url, False),
    ('.wh', 'Gets featured wallpapers from wallhaven', False),
    ('.wh relevant [amount] [query]', 'Gets relevant wallpaper(s)', True),
    ('.wh random [amount] [query]', 'Gets random wallpaper(s)', True),
    ('.wh latest [amount] [query]', 'Gets latest wallpaper(s)', True),
    ('.wh views [amount] [query]', 'Gets most viewed wallpaper(s)', True),
    ('.wh favorites [amount] [query]', 'Gets most favored wallpaper(s)', True),
    ('.wh top [amount] [query]', 'Gets top wallpaper(s)', True)
)

errorlist = (

)

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
async def itad(ctx):
    print_out(ctx)
    dic = isthereanydeal.bundles_specials()
    embed = discord.Embed(
        title='Bundles and Special Deals',
        url=isthereanydeal.home_url
    )

    for i in range(len(dic['title'])):
        embed.add_field(
            name=dic['title'][i],
            value='{}\n{} ({}) [details]({})'.format(
                dic['title_url'][i],
                dic['time'][i],
                dic['shop'][i],
                dic['details_url'][i]),
            inline=False
        )

    await ctx.send(embed=embed)


@itad.error
async def itad_error(ctx, error):
    await ctx.send(error)


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
        await ctx.send("Unknown")


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


def print_out(ctx):
    print('[{0.message.created_at}] {0.author}: {0.message.content}'.format(ctx))


bot.run(os.getenv('DISCORD_TOKEN'))
