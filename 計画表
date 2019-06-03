import random
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

@client.event
async def on_ready():
    print("起動完了じゃああああああああああああああああああああ")

# -------------------------------------------------------------------------------------------------------------------

@client.event
async def on_message(message):
    if message.content.startswith("スタート"):
        if db_write(int(message.author.id),str(message.content.split()[1])) == True:
            embed = discord.Embed(
                description=f"{message.author.mention}さんのスケジュール\n```{message.content.split()[1]}```",
                timestamp=message.timestamp
            )
            embed.set_footer(
                text="追加時刻:"
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
            if not reason:
                embed = discord.Embed(
                    description=f"{message.author.mention}さん\n\n数値をちゃんと入力してください。\n例: [計画進捗 10 1]`※計画進捗 進捗% 計画番号`",
                    color=discord.Color(random.randint(0,0xFFFFFF))
                )
                await client.send_message(message.channel,embed=embed)
                return
            elif not reason1:
                embed = discord.Embed(
                    description=f"{message.author.mention}さん\n\n数値をちゃんと入力してください。\n例: [計画進捗 10 1]`※計画進捗 進捗% 計画番号`",
                    color=discord.Color(random.randint(0,0xFFFFFF))
                )
                await client.send_message(message.channel,embed=embed)
                return
            else:
                if int(message.content.split()[1]) >= int(101):
                    embed = discord.Embed(
                        description=f"{message.author.mention}さん\n\n計画の進捗率を100以上にすることは出来ません！\n現在の計画の進捗率は[`{str(row[3])}%`]です。",
                        color=discord.Color(random.randint(0,0xFFFFFF))
                    )
                    await client.send_message(message.channel,embed=embed)
                    return
                if db_access(int(message.content.split()[1]),int(message.content.split()[2]),int(message.author.id)) == True:
                    if int(message.content.split()[1]) == int(100):
                        embed = discord.Embed(
                            description=f"{message.author.mention}さんの進捗率変化\n\nおめでとうございます！！\n第{message.content.split()[2]}計画の進捗率が[`100%`]になりました！\nこれでこの計画は終了です！お疲れさまでした！",
                            color=discord.Color(random.randint(0,0xFFFFFF))
                        )
                        await client.send_message(message.channel,embed=embed)
                        return
                    embed = discord.Embed(
                        description=f"{message.author.mention}さんの進捗率変化\n\n第{message.content.split()[2]}計画の進捗率が[`{str(row[3])}%≫≫{message.content.split()[1]}%`]",
                        color=discord.Color(random.randint(0,0xFFFFFF))
                    )
                    await client.send_message(message.channel,embed=embed)
                    return
                if db_access(int(message.content.split()[1]),int(message.content.split()[2]),
                               int(message.author.id)) == -1:
                    embed = discord.Embed(
                        description=f"{message.author.mention}さん\n\n計画の進捗率を下げることはできませんよ！\n現在の計画の進捗率は[`{str(row[3])}%`]です。",
                        color=discord.Color(random.randint(0,0xFFFFFF))
                    )
                    await client.send_message(message.channel,embed=embed)
                    return

    if message.content == "計画表":
        async def ok(member):
            await client.send_message(message.channel,embed=member)

        i = 1
        member = discord.Embed(title=f"{str(message.author)}さんの完了したスケジュール表:",colour=discord.Color.dark_grey())
        for row in db_read(message.author.id):
            if int(row[3]) == int(100):
                member.add_field(name="[`完`]第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [==========]" + str(row[3]) + "%`")
            if i % 5 == 0:
                await ok(member)
                member = discord.Embed(title=f"{str(message.author)}さんの完了したスケジュール表:")
            i+= 1
        await ok(member)

        async def send(member_data):
            if len(list(db_read(int(message.author.id)))) == 0:
                embed = discord.Embed(
                    description=f"{message.author.mention}さん\nあなたはスケジュールをまだ作成していません。\n\nスタート [内容]でスケジュールを建ててみよう!!",
                    color=discord.Color(random.randint(0,0xFFFFFF))
                )
                await client.send_message(message.channel,embed=embed)
                return
            await client.send_message(message.channel,embed=member_data)

        i = 1
        member_data = discord.Embed(title=f"{str(message.author)}さんのスケジュール表:",colour=discord.Color.green())
        for row in db_read(message.author.id):
            if int(row[3]) == int(0):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [          ]" + str(row[3]) + "%`")
            if int(1) <= int(row[3]) <= int(10):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [>         ]" + str(row[3]) + "%`")
            if int(11) <= int(row[3]) <= int(20):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [=>        ]" + str(row[3]) + "%`")
            if int(21) <= int(row[3]) <= int(30):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [==>       ]" + str(row[3]) + "%`")
            if int(31) <= int(row[3]) <= int(40):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [===>      ]" + str(row[3]) + "%`")
            if int(41) <= int(row[3]) <= int(50):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [====>     ]" + str(row[3]) + "%`")
            if int(51) <= int(row[3]) <= int(60):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [=====>    ]" + str(row[3]) + "%`")
            if int(61) <= int(row[3]) <= int(70):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [======>   ]" + str(row[3]) + "%`")
            if int(71) <= int(row[3]) <= int(80):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [=======>  ]" + str(row[3]) + "%`")
            if int(81) <= int(row[3]) <= int(90):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [========> ]" + str(row[3]) + "%`")
            if int(91) <= int(row[3]) <= int(99):
                member_data.add_field(name="第" + str(row[0]) + "計画:",value="```" + str(row[2]) + "```\n`進捗状況: [=========>]" + str(row[3]) + "%`")
            if i % 5 == 0:
                await send(member_data)
                member_data = discord.Embed(title=f"{str(message.author)}さんのスケジュール表:")
            i+= 1
        else:
            await send(member_data)
            return

def db_read(name):
    name = int(name)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY,name INTEGER,text INTEGER, sintyoku INTEGER)")
        c.execute('SELECT id,name,text,sintyoku FROM schedule where name=?',(name,))
        ans = c.fetchall()
        for row in ans:
            con.commit()
            yield (row[0],row[1],row[2],row[3])


def db_write(name,text):
    name = int(name)
    text = str(text)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY,name INTEGER,text INTEGER, sintyoku INTEGER)")
        c.execute("INSERT INTO schedule(name,text,sintyoku) VALUES(?,?,0)",(name,text))
        return True


def db_access(sintyoku,id,name):
    sintyoku = int(sintyoku)
    name = int(name)
    id = int(id)
    with closing(sqlite3.connect("schedule.db",isolation_level=None)) as con:
        c = con.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS schedule(id INTEGER PRIMARY KEY,name INTEGER,text INTEGER, sintyoku INTEGER)")
        c.execute('SELECT sintyoku FROM schedule WHERE id=? AND name=?',(id,name))
        ok = c.fetchone()
        print(ok)
        if int(re.sub("\\D", "", f"{ok}")) > int(sintyoku):
            return -1
        c.execute("""UPDATE schedule set sintyoku=? where id=? AND name=?""",(sintyoku,id,name))
        return True



client.run("TOKEN")
