# -----------------------------------------------------------------------------------------------------------------
import asyncio
import sqlite3
from contextlib import closing
import re

import discord
from discord.ext.commands import Bot

# -------------------------------------------------------------------------------------------------------------------
client = Bot(command_prefix='&',pm_help=True)
message_counter = 0
left = '⏪'
right = '⏩'
numbers = 0

def predicate(message,l,r):
    def check(reaction,user):
        if reaction.message.id != message.id or user == client.user:
            return False
        if l and reaction.emoji == left:
            return True
        if r and reaction.emoji == right:
            return True
        return False

    return check

@client.event
async def on_ready():
    print("起動完了じゃああああああああああああああああああああ")

async def change_status():
    await client.wait_until_ready()

    while not client.is_closed:
        await client.change_presence(game=discord.Game(name="ヘルプしてね！"))
        await asyncio.sleep(30)
# -------------------------------------------------------------------------------------------------------------------

@client.event
async def on_message(message):
    global embed
    help_message = [
        f"""[**このBOTの招待**](<https://discordapp.com/api/oauth2/authorize?client_id=474186515111477258&permissions=8&scope=bot>)
        何かがおかしい...。あれ...？なんで動かないの？
        と思ったら[`The.First.Step#3454`]にお申し付けください。
        
        [`1ページ目`]
        このメッセージを表示。
        
        [`2ページ目`]
        このBOTのコマンドの使い方
        
        このBOTは管理者:The.First.Step#3454が制作しました！
        
        1ページ目/2ページ中""",

        f"""
        [`計画スタート`]
        打った内容のスケジュールが開始されます。
        使い方:[`計画スタート 人類補完計画`]
        
        [`メモ`]
        その機能について少しメモを残しておきたい場合にお使いください。
        使い方:[`メモ 1 人類を補完するには～～が必要かもしれない`]
        
        [`計画詳細`]
        打った計画番号の詳細を表示いたします。
        使い方:[`計画詳細 1`]
        
        [`計画変更`]
        計画の内容を変更したい場合にお使いください
        使い方:[`計画変更 1 人類殲滅計画`]
        
        [`計画進捗`]
        その計画の進捗率を変更します。
        使い方:[`計画進捗 50 1`]
        ※もしこうすれば第1計画の進捗率が50%になります。
        
        [`計画中止`]
        計画を中止いたします。
        使い方:[`計画中止 1`]

        [`計画再始動`]
        計画を再始動します。
        使い方:[`計画再始動 1`]

        [`計画表`]
        これで今までの計画全てを閲覧可能です。
        使い方:[`計画表`]

        2ページ目/2ページ中"""]

    if message.content == "ヘルプ":
        index = 0
        while True:
            embed = discord.Embed(
                title="Help一覧:",
                description=help_message[index],
            )
            embed.set_thumbnail(
                url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(client.user)
            )
            msg = await client.send_message(message.channel,embed=embed)
            l = index != 0
            r = index != len(help_message) - 1
            if l:
                await client.add_reaction(msg,left)
            if r:
                await client.add_reaction(msg,right)
            react,user = await client.wait_for_reaction(check=predicate(msg,l,r))
            if react.emoji == left:
                index -= 1
            elif react.emoji == right:
                index += 1
            await client.delete_message(msg)

    if message.content.startswith("計画スタート"):
        try:
            reason = message.content[7:]
        except Exception:
            reason = None
        if not reason:
            embed = discord.Embed(
                description=f"{message.author.mention}さん\n\n計画を始める際は内容を書いてください。\n例:計画スタート 地球征服 ※[`計画スタート 計画内容`]",
                colour=discord.Color.red()
            )
            await client.send_message(message.channel,embed=embed)
            return
        if db_write(int(message.author.id),str(message.content[7:])) == True:
            for row in db_read(message.author.id):
                embed = discord.Embed(
                    description=f"{message.author.mention}さんが以下のスケジュールを開始しました。\n第{int(row[0])}計画情報:\n```{message.content[7:]}```",
                    timestamp=message.timestamp,
                    colour=discord.Color.green()
                )
                embed.set_footer(
                    text="追加時刻:"
                )
            await client.send_message(message.channel,embed=embed)
            return

    if message.content.startswith("メモ"):
        memo = 4 + len(message.content.split()[1])
        try:
            reason = message.content.split()[1]
            reason1 = message.content[memo:]
        except Exception:
            reason = None
            reason1 = None

        if not reason:
            embed = discord.Embed(
                description=f"{message.author.mention}さん\n\n数値をちゃんと入力してください。\n例: [メモ 1 ～～の機能も付けよう。]`※メモ 計画番号 メモ追加内容`",
                colour=discord.Color.red()
            )
            await client.send_message(message.channel,embed=embed)
            return

        elif not reason1:
            embed = discord.Embed(
                description=f"{message.author.mention}さん\n\n内容はちゃんと記入してください。\n例: [メモ 1 ～～の機能も付けよう。]`※メモ 計画番号 メモ追加内容`",
                colour=discord.Color.red()
            )
            await client.send_message(message.channel,embed=embed)
            return

        else:
            for row in db_read(message.author.id):
                if int(message.content.split()[1]) == int(row[0]):
                    if not int(row[4]) % 2 == 0:
                        embed = discord.Embed(
                            description=f"{message.author.mention}さん\nこのスケジュールは停止されてます。\nメモを追加するには進行中のスケジュールでないとダメです。",
                            colour=discord.Color.red()
                        )
                        await client.send_message(message.channel,embed=embed)
                        return
                if int(message.content.split()[1]) == int(row[0]):
                    if int(row[3]) == int(100):
                        embed = discord.Embed(
                            description=f"{message.author.mention}さん\nもうすでに完結したスケジュールにメモ追加はできません。",
                            colour=discord.Color.red()
                        )
                        await client.send_message(message.channel,embed=embed)
                        return
            if db_memo(int(message.author.id),int(message.content.split()[1]),str(message.content[memo:])) == True:
                for row in db_read(message.author.id):
                    for row1 in db_read_memo(message.author.id):
                        if int(row[1]) == int(row1[2]):
                            if int(row[0]) == int(row1[1]):
                                embed = discord.Embed(
                                    description=f"{message.author.mention}さんのスケジュール | 第{int(row[0])}計画情報:\n\n計画内容:```{str(row[2])}```\nメモ追加:\n```{message.content[memo:]}```",
                                    timestamp=message.timestamp
                                )
                                embed.set_footer(
                                    text="追加時刻:"
                                )
                await client.send_message(message.channel,embed=embed)
                return

    if message.content.startswith("計画詳細"):
        try:
            reason = message.content.split()[1]
        except Exception:
            reason = None
        if not reason:
            embed = discord.Embed(
                description=f"{message.author.mention}さん\n\n詳細を知りたい場合は計画番号もご記入ください。\n例:計画番号 1 ※[`計画詳細 計画番号`]",
                colour=discord.Color.red()
            )
            await client.send_message(message.channel,embed=embed)
            return
        else:

            for row in db_read(message.author.id):
                if int(row[0]) == int(message.content.split()[1]):
                    if int(row[3]) == int(100):
                        embed = discord.Embed()
                        embed.add_field(name="[`完`]第" + str(row[0]) + "計画:",
                                         value="```" + str(row[2]) + "```\n`進捗状況: [==========]" + str(row[3]) + "%`")
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(
                            message.author)
                        )
                        await client.send_message(message.channel,embed=embed)
                        async def keikaku_(data_):
                            embed = discord.Embed(
                                title=f"第{message.content.split()[1]}計画のメモ:",
                                description=data_,
                            )
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/attachments/585478940080996352/586164638450843649/memo.jpg"
                            )
                            await client.send_message(message.channel,embed=embed)

                        i = 1
                        data_ = ""
                        for row in db_read(message.author.id):
                            for row1 in db_read_memo(message.author.id):
                                if int(message.content.split()[1]) == int(row[0]) == int(row1[1]):
                                    if int(row[1]) == int(row1[2]):
                                        data_ += "`{}: {}`\n".format(i,str(row1[3]))
                                    else:
                                        data_ += "メモは検出されませんでした。"
                                        await keikaku_(data_)
                                        return
                                    i += 1
                        else:
                            await keikaku_(data_)
                            return

                    if not int(row[4]) % 2 == 0:
                        embed = discord.Embed(
                            colour=discord.Color.gold()
                        )
                        embed.add_field(name="[`停止中`]第" + str(row[0]) + "計画:",
                                       value="```" + str(row[2]) + "```\n進捗状況: `[停止中]`")
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(
                                message.author)
                        )
                        await client.send_message(message.channel,embed=embed)

                        async def keikaku_stop(data_stop):
                            embed = discord.Embed(
                                title=f"第{message.content.split()[1]}計画のメモ:",
                                description=data_stop,
                                color=discord.Color.gold()
                            )
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/attachments/585478940080996352/586164638450843649/memo.jpg"
                            )
                            await client.send_message(message.channel,embed=embed)
                        i = 1
                        data_stop = ""
                        for row in db_read(message.author.id):
                            for row1 in db_read_memo(message.author.id):
                                if int(message.content.split()[1]) == int(row[0]) == int(row1[1]):
                                    if int(row[1]) == int(row1[2]):
                                        data_stop += "`{}: {}`\n".format(i,str(row1[3]))
                                    else:
                                        data_stop += "メモは検出されませんでした。"
                                        await keikaku_stop(data_stop)
                                        return
                                    i += 1
                        else:
                            await keikaku_stop(data_stop)
                            return

                    else:
                        embed = discord.Embed(
                            color=discord.Color.green(),
                        )
                        if int(row[3]) == int(0):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [          ]" + str(
                                                row[3]) + "%`")
                        if int(1) <= int(row[3]) <= int(10):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [>         ]" + str(
                                                row[3]) + "%`")
                        if int(11) <= int(row[3]) <= int(20):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [=>        ]" + str(
                                                row[3]) + "%`")
                        if int(21) <= int(row[3]) <= int(30):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [==>       ]" + str(
                                                row[3]) + "%`")
                        if int(31) <= int(row[3]) <= int(40):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [===>      ]" + str(
                                                row[3]) + "%`")
                        if int(41) <= int(row[3]) <= int(50):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [====>     ]" + str(
                                                row[3]) + "%`")
                        if int(51) <= int(row[3]) <= int(60):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [=====>    ]" + str(
                                                row[3]) + "%`")
                        if int(61) <= int(row[3]) <= int(70):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [======>   ]" + str(
                                                row[3]) + "%`")
                        if int(71) <= int(row[3]) <= int(80):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [=======>  ]" + str(
                                                row[3]) + "%`")
                        if int(81) <= int(row[3]) <= int(90):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [========> ]" + str(
                                                row[3]) + "%`")
                        if int(91) <= int(row[3]) <= int(99):
                            embed.add_field(name="第" + str(row[0]) + "計画:",
                                            value="```" + str(row[2]) + "```\n`進捗状況: [=========>]" + str(
                                                row[3]) + "%`")
                        embed.set_thumbnail(
                            url="https://cdn.discordapp.com/avatars/{0.id}/{0.avatar}.png?size=1024".format(
                                message.author)
                        )
                        await client.send_message(message.channel,embed=embed)

                        async def keikaku(data):
                            embed = discord.Embed(
                                title=f"第{message.content.split()[1]}計画のメモ:",
                                description=data,
                                color=discord.Color.green()
                            )
                            embed.set_thumbnail(
                                url="https://cdn.discordapp.com/attachments/585478940080996352/586164638450843649/memo.jpg"
                            )
                            await client.send_message(message.channel,embed=embed)

                        i = 1
                        data = ""
                        for row in db_read(message.author.id):
                            for row1 in db_read_memo(message.author.id):
                                if int(message.content.split()[1]) == int(row[0]) == int(row1[1]):
                                    if int(row[1]) == int(row1[2]):
                                        data += "`{}: {}`\n".format(i,str(row1[3]))
                                    else:
                                        data += "メモは検出されませんでした。"
                                        await keikaku(data)
                                        return
                                    i += 1
                        else:
                            await keikaku(data)

    if message.content.startswith("計画変更"):
        change = 6 + len(message.content.split()[1])
        try:
            reason = message.content.split()[1]
            reason1 = message.content[change:]
        except Exception:
            reason = None
            reason1 = None
        if not reason:
            embed = discord.Embed(
                description=f"{message.author.mention}さん\n\n計画番号をちゃんと入力してください。\n例: [計画変更 1 やっぱり宇宙制覇。]`※計画変更 計画番号 計画変更内容`",
                colour=discord.Color.red()
            )
            await client.send_message(message.channel,embed=embed)
            return

        elif not reason1:
            embed = discord.Embed(
                description=f"{message.author.mention}さん\n\n計画変更内容はちゃんと記入してください。\n例: [計画変更 1 やっぱり宇宙制覇。]`※計画変更 計画番号 計画変更内容`",
                colour=discord.Color.red()
            )
            await client.send_message(message.channel,embed=embed)
            return
        else:
            for row in db_read(message.author.id):
                if int(message.content.split()[1]) == int(row[0]):
                    if not int(row[4]) % 2 == 0:
                        embed = discord.Embed(
                            description=f"{message.author.mention}さん\nこのスケジュールは停止されてます。\n計画の内容を変更したい場合にはこの計画を再始動してください。",
                            colour=discord.Color.red()
                        )
                        await client.send_message(message.channel,embed=embed)
                        return

                    elif int(row[3]) == int(100):
                        embed = discord.Embed(
                            description=f"{message.author.mention}さん\nもうすでに完結したスケジュールの計画は変更することができません。",
                            colour=discord.Color.red()
                        )
                        await client.send_message(message.channel,embed=embed)
                        return
                    else:
                        if db_read_access(int(message.author.id),int(message.content.split()[1]),str(message.content[change:])) == True:
                            embed = discord.Embed(
                                description=f"{message.author.mention}さんの計画変更情報:\n\n第{message.content.split()[2]}計画の内容が変更されました。\n変更前:```{str(row[2])}```\n変更後:```{message.content[change:]}```",
                                colour=discord.Color.red()
                            )
                            await client.send_message(message.channel,embed=embed)
                            return

    if message.content.startswith("計画進捗"):
        try:
            reason = message.content.split()[1]
            reason1 = message.content.split()[2]
        except Exception:
            reason = None
            reason1 = None
        for row in db_read(message.author.id):
            if str(row[0]) == str(message.content.split()[2]):
                if not reason:
                    embed = discord.Embed(
                        description=f"{message.author.mention}さん\n\n数値をちゃんと入力してください。\n例: [計画進捗 10 1]`※計画進捗 進捗% 計画番号`",
                        colour=discord.Color.red()
                    )
                    await client.send_message(message.channel,embed=embed)
                    return
                elif not reason1:
                    embed = discord.Embed(
                        description=f"{message.author.mention}さん\n\n数値をちゃんと入力してください。\n例: [計画進捗 10 1]`※計画進捗 進捗% 計画番号`",
                        colour=discord.Color.red()
                    )
                    await client.send_message(message.channel,embed=embed)
                    return
                else:
                    if int(message.content.split()[1]) == int(row[3]):
                        embed = discord.Embed(
                            description=f"{message.author.mention}さん\n\n計画の進捗率を同じにすることは出来ません！\n現在の計画の進捗率は[`{str(row[3])}%`]です。",
                            colour=discord.Color.red()
                        )
                        await client.send_message(message.channel,embed=embed)
                        return
                    if int(message.content.split()[1]) >= int(101):
                        embed = discord.Embed(
                            description=f"{message.author.mention}さん\n\n計画の進捗率を100以上にすることは出来ません！\n現在の計画の進捗率は[`{str(row[3])}%`]です。",
                            colour=discord.Color.red()
                        )
                        await client.send_message(message.channel,embed=embed)
                        return
                    if db_access(int(message.content.split()[1]),int(message.content.split()[2]),int(message.author.id)) == True:
                        if int(message.content.split()[1]) == int(100):
                            embed = discord.Embed(
                                description=f"{message.author.mention}さんの進捗率変化\n\nおめでとうございます！！\n第{message.content.split()[2]}計画の進捗率が[`100%`]になりました！\nこれでこの計画は終了です！お疲れさまでした！",
                            )
                            await client.send_message(message.channel,embed=embed)
                            return
                        embed = discord.Embed(
                            description=f"{message.author.mention}さんの進捗率変化\n\n第{message.content.split()[2]}計画の進捗率が[`{str(row[3])}%≫≫{message.content.split()[1]}%`]",
                            color=discord.Color.green()
                        )
                        await client.send_message(message.channel,embed=embed)
                        return
                    if db_access(int(message.content.split()[1]),int(message.content.split()[2]),
                                 int(message.author.id)) == -1:
                        embed = discord.Embed(
                            description=f"{message.author.mention}さん\n\n計画の進捗率を下げることはできませんよ！\n現在の計画の進捗率は[`{str(row[3])}%`]です。",
                            colour=discord.Color.red()
                        )
                        await client.send_message(message.channel,embed=embed)
                        return

    if message.content.startswith("計画中止"):
        try:
            reason = message.content.split()[1]
        except Exception:
            reason = None
        for row in db_read(message.author.id):
            if not reason:
                embed = discord.Embed(
                    description=f"{message.author.mention}さん\n\n数値をちゃんと入力してください。\n例: [計画中止 1]`※計画中止 計画番号`",
                colour=discord.Color.red()
                )
                await client.send_message(message.channel,embed=embed)
                return
            if int(message.content.split()[1]) == int(row[0]):
                if not int(row[4]) % 2 == 0:
                    embed = discord.Embed(
                        description=f"{message.author.mention}さん\nこのスケジュールは既に停止されてます。\n\n再スタートするときは`[再始動 計画番号]`をお願いします。",
                        colour=discord.Color.red()
                    )
                    await client.send_message(message.channel,embed=embed)
                    return
                if int(row[3]) == int(100):
                    embed = discord.Embed(
                        description=f"{message.author.mention}さん\nもうすでに完結したスケジュールは中止できません。",
                        colour=discord.Color.red()
                    )
                    await client.send_message(message.channel,embed=embed)
                    return

        if db_stop(int(message.author.id),int(message.content.split()[1])) == True:
            embed = discord.Embed(
                description=f"{message.author.mention}さんが第{message.content.split()[1]}計画を停止いたしました。",
                colour=discord.Color.gold(),
                timestamp=message.timestamp,
            )
            embed.set_footer(
                text="停止時刻:"
            )
            await client.send_message(message.channel,embed=embed)
            return

    if message.content.startswith("計画再始動"):
        try:
            reason = message.content.split()[1]
        except Exception:
            reason = None
        for row in db_read(message.author.id):
            if not reason:
                embed = discord.Embed(
                    description=f"{message.author.mention}さん\n\n数値をちゃんと入力してください。\n例: [計画再始動 1]`※計画再始動 計画番号`",
                    colour=discord.Color.red()
                )
                await client.send_message(message.channel,embed=embed)
                return
            if int(message.content.split()[1]) == int(row[0]):
                if int(row[4]) % 2 == 0:
                    embed = discord.Embed(
                        description=f"{message.author.mention}さん\nこのスケジュールは中止されてません。\n\n停止するときは`[計画中止 計画番号]`をお願いします。",
                        colour=discord.Color.red()
                    )
                    await client.send_message(message.channel,embed=embed)

        if db_restart(int(message.author.id),int(message.content.split()[1])) == True:
            embed = discord.Embed(
                description=f"{message.author.mention}さんが第{message.content.split()[1]}計画を再始動いたしました。",
                colour=discord.Color.green(),
                timestamp=message.timestamp,
            )
            embed.set_footer(
                text="再始動時刻:"
            )
            await client.send_message(message.channel,embed=embed)
            return

    if message.content == "計画表":
        if len(list(db_read(int(message.author.id)))) == 0:
            embed = discord.Embed(
                description=f"{message.author.mention}さん\nあなたはスケジュールをまだ作成していません。\n\n計画スタート [内容]でスケジュールを建ててみよう!!",
                colour=discord.Color.red()
            )
            await client.send_message(message.channel,embed=embed)
            return
        else:
            async def ok(member):
                await client.send_message(message.channel,embed=member)

            i = 1
            member = discord.Embed(title=f"{str(message.author)}さんの完了したスケジュール表:",colour=discord.Color.dark_grey())
            for row in db_read(message.author.id):
                if int(row[3]) == int(100):
                    member.add_field(name="[`完`]第" + str(row[0]) + "計画:",
                                     value="```" + str(row[2]) + "```\n`進捗状況: [==========]" + str(row[3]) + "%`")
                if i % 10 == 0:
                    await ok(member)
                    member = discord.Embed(title=f"{str(message.author)}さんの完了したスケジュール表:",
                                           colour=discord.Color.dark_grey())
                i += 1
            await ok(member)

            async def stop_shedule(stop):
                await client.send_message(message.channel,embed=stop)

            i = 1
            stop = discord.Embed(title=f"{str(message.author)}さんが停止したスケジュール表:",colour=discord.Color.gold())
            for row in db_read(message.author.id):
                if not int(row[4]) % 2 == 0:
                    stop.add_field(name="[`停止中`]第" + str(row[0]) + "計画:",
                                   value="```" + str(row[2]) + "```\n進捗状況: `[停止中]`")

                if i % 10 == 0:
                    await stop_shedule(stop)
                    stop = discord.Embed(title=f"{str(message.author)}さんが停止したスケジュール表:",
                                         colour=discord.Color.gold())
                i += 1
            await stop_shedule(stop)

            async def send(member_data):
                await client.send_message(message.channel,embed=member_data)

            i = 1
            member_data = discord.Embed(title=f"{str(message.author)}さんのスケジュール表:",colour=discord.Color.green())
            for row in db_read(message.author.id):
                if not int(row[4]) % 2 == 0:
                    pass
                else:
                    if int(row[3]) == int(0):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [          ]" + str(
                                                  row[3]) + "%`")
                    if int(1) <= int(row[3]) <= int(10):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [>         ]" + str(
                                                  row[3]) + "%`")
                    if int(11) <= int(row[3]) <= int(20):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [=>        ]" + str(
                                                  row[3]) + "%`")
                    if int(21) <= int(row[3]) <= int(30):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [==>       ]" + str(
                                                  row[3]) + "%`")
                    if int(31) <= int(row[3]) <= int(40):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [===>      ]" + str(
                                                  row[3]) + "%`")
                    if int(41) <= int(row[3]) <= int(50):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [====>     ]" + str(
                                                  row[3]) + "%`")
                    if int(51) <= int(row[3]) <= int(60):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [=====>    ]" + str(
                                                  row[3]) + "%`")
                    if int(61) <= int(row[3]) <= int(70):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [======>   ]" + str(
                                                  row[3]) + "%`")
                    if int(71) <= int(row[3]) <= int(80):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [=======>  ]" + str(
                                                  row[3]) + "%`")
                    if int(81) <= int(row[3]) <= int(90):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [========> ]" + str(
                                                  row[3]) + "%`")
                    if int(91) <= int(row[3]) <= int(99):
                        member_data.add_field(name="第" + str(row[0]) + "計画:",
                                              value="```" + str(row[2]) + "```\n`進捗状況: [=========>]" + str(
                                                  row[3]) + "%`")
                    if i % 10 == 0:
                        await send(member_data)
                        member_data = discord.Embed(title=f"{str(message.author)}さんのスケジュール表:",
                                                    colour=discord.Color.green())
                    i += 1
            else:
                await send(member_data)
                return

def db_read(name):
    name = int(name)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY,name INTEGER,text INTEGER, sintyoku INTEGER, stop INTEGER)")
        c.execute('SELECT id,name,text,sintyoku,stop FROM schedule where name=?',(name,))
        ans = c.fetchall()
        for row in ans:
            yield (row[0],row[1],row[2],row[3],row[4])

def db_read_memo(name):
    name = int(name)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS schedule_memo(id INTEGER PRIMARY KEY,number INTEGER, name INTEGER,text INTEGER)")
        c.execute('SELECT id,number,name,text FROM schedule_memo where name=?',(name,))
        ans = c.fetchall()
        for row in ans:
            yield (row[0],row[1],row[2],row[3])

def db_read_access(name,id,text):
    name = int(name)
    id = int(id)
    text = str(text)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute(
            "CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY,name INTEGER,text INTEGER, sintyoku INTEGER, stop INTEGER)")
        c.execute("UPDATE schedule set text=? where name=? AND id=?",(text,name,id))
        return True

def db_write(name,text):
    name = int(name)
    text = str(text)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY,name INTEGER,text INTEGER, sintyoku INTEGER, stop INTEGER)")
        c.execute("INSERT INTO schedule(name,text,sintyoku,stop) VALUES(?,?,0,0)",(name,text))
        return True

def db_memo(name,number,text):
    name = int(name)
    number = int(number)
    text = str(text)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schedule_memo(id INTEGER PRIMARY KEY,number INTEGER, name INTEGER,text INTEGER)")
        c.execute("INSERT INTO schedule_memo(name,number,text) VALUES(?,?,?)",(name,number,text))
        return True

def db_stop(name,text):
    name = int(name)
    text = int(text)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY,name INTEGER,text INTEGER, sintyoku INTEGER, stop INTEGER)")
        c.execute("UPDATE schedule set stop = stop + 1 where name=? AND id=?",(name,text))
        return True

def db_restart(name,text):
    name = int(name)
    text = int(text)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY,name INTEGER,text INTEGER, sintyoku INTEGER, stop INTEGER)")
        c.execute("UPDATE schedule set stop = stop - 1 where name=? AND id=?",(name,text))
        return True

def db_access(sintyoku,id,name):
    sintyoku = int(sintyoku)
    name = int(name)
    id = int(id)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY,name INTEGER,text INTEGER, sintyoku INTEGER, stop INTEGER)")
        c.execute('SELECT sintyoku FROM schedule WHERE id=? AND name=?',(id,name))
        ok = c.fetchone()
        if int(re.sub("\\D", "", f"{ok}")) > int(sintyoku):
            return -1
        c.execute("""UPDATE schedule set sintyoku=? where id=? AND name=?""",(sintyoku,id,name))
        return True

client.loop.create_task(change_status())
client.run("TOKEN")
