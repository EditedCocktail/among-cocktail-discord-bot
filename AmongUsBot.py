import discord
import random
import time
import string
import asyncio
import json
from PIL import Image, ImageDraw
from discord.ext import commands

client = commands.Bot(command_prefix="$", intents=discord.Intents.all())
client.remove_command("help")
rooms = {}
users = {}
locations = {"Звездолёт":[
	["Комуникация"],
	["Верхний двигатель", "Кафетерия", "Оружейная"],
	["Реактор", "Камеры", "Мед-кабинет", "Кислород", "Навигация"],
	["Нижний двигатель", "Электрика", "Хранильще"], 
	["Щиты"]]}
tasks = [["Эл1", ["Камеры", 10, "Починка элекстричества"]], ["Эл2", ["Электрика", 10, "Починка элекстричества"]], ["Курс", ["Навигация", 15, "Проложение курса"]]]
startTime = time.time()
need={False:"Живой", True:"Мёртвый"}
keys=["🔼","🔽","◀️","▶️","🔧","🚨"]
binds={"🔼":[0, -1], "◀️":[-1, 0], "🔽":[0, 1], "▶️":[1, 0]}

def code(size=6, chars=string.ascii_uppercase + string.digits):
	return "".join(random.choice(chars) for _ in range(size))

@client.event
async def on_ready():
	print("Online!")

@client.event
async def on_message(ctx):
	if not ctx.author.id in users:
		users[ctx.author.id]=False
	await client.process_commands(ctx)

@client.event
async def on_reaction_add(reaction, user):
	if user.id==client.user.id:
		return
	if not users[user.id]:
		return
	if reaction.message.id!=rooms[users[user.id]]["users"][user.id]["msg"].id:
		return
	cords=rooms[users[user.id]]["cords"][user.id]
	if reaction.emoji in ["🔼", "🔽", "▶️", "◀️"]:
		if int(time.time() - startTime)>=rooms[users[user.id]]["users"][user.id]["taskcd"]:
			if cords[1]+binds[reaction.emoji][1] < len(locations[rooms[users[user.id]]["map"]]) and cords[1]+binds[reaction.emoji][1]>=0:
				if cords[0]+binds[reaction.emoji][0] < len(locations[rooms[users[user.id]]["map"]][cords[1]+binds[reaction.emoji][1]]) and cords[0]+binds[reaction.emoji][0]>=0:
					rooms[users[user.id]]["cords"][user.id]=[cords[0]+binds[reaction.emoji][0], cords[1]+binds[reaction.emoji][1]]
					cords=rooms[users[user.id]]["cords"][user.id]
					emb = discord.Embed(title="Передвижение", description=f"""
Локация: `{locations[rooms[users[user.id]]["map"]][cords[1]][cords[0]]}`
Игроки: `{", ".join(["["+client.get_user(i).name+":"+need[rooms[users[user.id]]["users"][i]["dead"]]+"]" for i in rooms[users[user.id]]["cords"] if rooms[users[user.id]]["cords"][i]==cords])}`
Задания: {", ".join([i[1][2] for i in rooms[users[user.id]]["users"][user.id]["tasks"] if i[1][0]==locations[rooms[users[user.id]]["map"]][cords[1]][cords[0]]])}""", color=discord.Color.blurple())
					await rooms[users[user.id]]["users"][user.id]["msg"].edit(embed = emb)
	elif reaction.emoji=="🔧":
		if int(time.time() - startTime)>=rooms[users[user.id]]["users"][user.id]["taskcd"] and [i for i in rooms[users[user.id]]["users"][user.id]["tasks"] if i[1][0]==locations[rooms[users[user.id]]["map"]][cords[1]][cords[0]]]!=[]:
			tsk = random.choice([i for i in rooms[users[user.id]]["users"][user.id]["tasks"] if i[1][0]==locations[rooms[users[user.id]]["map"]][cords[1]][cords[0]]])
			if rooms[users[user.id]]["imposter"]!=user.id:
				rooms[users[user.id]]["users"][user.id]["taskcd"]=int(time.time() - startTime)+tsk[1][1]
				rooms[users[user.id]]["tasks"]-=1
			else:
				rooms[users[user.id]]["users"][user.id]["taskcd"]=0
			if rooms[users[user.id]]["imposter"]==user.id:
				emb = discord.Embed(title="Выполнение фальшивого задания", description=f"""
Задание: {tsk[1][2]}""", color=discord.Color.blurple())
			else:
				emb = discord.Embed(title="Выполнение задания", description=f"""
Задание: {tsk[1][2]}
Время: {tsk[1][1]}сек""", color=discord.Color.blurple())
			await rooms[users[user.id]]["users"][user.id]["msg"].edit(embed = emb)
			await asyncio.sleep(tsk[1][1])
			rooms[users[user.id]]["users"][user.id]["tasks"].remove(tsk)
			emb = discord.Embed(title="Передвижение", description=f"""
Локация: `{locations[rooms[users[user.id]]["map"]][cords[1]][cords[0]]}`
Игроки: `{", ".join(["["+client.get_user(i).name+":"+need[rooms[users[user.id]]["users"][i]["dead"]]+"]" for i in rooms[users[user.id]]["cords"] if rooms[users[user.id]]["cords"][i]==cords])}`
Задания: {", ".join([i[1][2] for i in rooms[users[user.id]]["users"][user.id]["tasks"] if i[1][0]==locations[rooms[users[user.id]]["map"]][cords[1]][cords[0]]])}""", color=discord.Color.blurple())
			await rooms[users[user.id]]["users"][user.id]["msg"].edit(embed = emb)
			if rooms[users[user.id]]["tasks"]==0:
				emb = discord.Embed(title="Задания", description=f"""
{user.name} выполнил последнее задание!
Победа членов экипажа!""", color=discord.Color.green())
				c = users[user.id]
				for i in rooms[users[user.id]]["lobby"]:
					await client.get_user(i).send(embed=emb)
					users[i]=False
				rooms.pop(c, None)
	elif reaction.emoji=="☠" and rooms[users[user.id]]["imposter"]==user.id and [i for i in rooms[users[user.id]]["cords"] if rooms[users[user.id]]["cords"][i]==cords and i!=user.id]!=[]:
		if int(time.time() - startTime)>=rooms[users[user.id]]["users"][user.id]["taskcd"]:
			rooms[users[user.id]]["users"][user.id]["taskcd"]=int(time.time() - startTime)+20
			emb = discord.Embed(title="Смерть", description=f"""
{user.name} вас убил!""", color=discord.Color.red())
			ruser = random.choice([i for i in rooms[users[user.id]]["cords"] if rooms[users[user.id]]["cords"][i]==cords and i!=user.id])
			await client.get_user(ruser).send(embed=emb)
			emb = discord.Embed(title="Рядом произошло убийство", description=f"""
{client.get_user(ruser).name} был убит!
Нажмите на 🚨, чтобы начать совещание!""", color=discord.Color.green())
			if len([i for i in rooms[users[user.id]]["lobby"] if not rooms[users[user.id]]["users"]["dead"]])==2:
				emb = discord.Embed(title="Убийство", description=f"""
{user.name} убил {client.get_user(ruser).name}!
Победа предателя!""", color=discord.Color.green())
				c = users[user.id]
				for i in rooms[users[user.id]]["lobby"]:
					await client.get_user(i).send(embed=emb)
					users[i]=False
				rooms.pop(c, None)
			else:
				for i in [i for i in rooms[users[user.id]]["cords"] if rooms[users[user.id]]["cords"][i]==cords and not i in [user.id, ruser]]:
					await client.get_user(i).send(embed=emb)
		else:
			emb = discord.Embed(title="Ошибка", description=f"""
Подождите ещё {int(time.time() - startTime)-rooms[users[user.id]]["users"][user.id]["taskcd"]} сек!""", color=discord.Color.red())
			await user.send(embed=emb)
	elif reaction.emoji=="🚨":
		if rooms[users[user.id]]["users"][user.id]["btns"]==0:
			emb = discord.Embed(title="Ошибка", description=f"""
У вас кончились нажатия на кнопку!""", color=discord.Color.red())
			await user.send(embed=emb)
		elif rooms[users[user.id]]["voiting"]:
			emb = discord.Embed(title="Ошибка", description=f"""
Уже идёт совещание!""", color=discord.Color.red())
			await user.send(embed=emb)
		else:
			emb = discord.Embed(title="Голосование", description="""
	Напишите текст, который будет отправлен всем игрокам в лс, у вас есть 30 сек!""", color=discord.Color.green())
			await user.send(embed=emb)
			check = lambda mes: mes.author.id==user.id
			text = await client.wait_for("message", check=check, timeout=30)
			emb = discord.Embed(title="Голосование", description=f"""
	Сообщение от `{user.name}`
	Проголосовать: `{client.command_prefix}vote [0 - {len(rooms[users[user.id]]["lobby"])-1}]`
	{text.content}""", color=discord.Color.green())
			rooms[users[user.id]]["voiting"]=True
			for i in rooms[users[user.id]]["lobby"]:
				await client.get_user(i).send(embed=emb)

@client.command()
async def help(ctx):
	emb = discord.Embed(title="🍹CocktailTests", description=f"""
`{client.command_prefix}play` ~ Создать комнату
`{client.command_prefix}join [код игры]` ~ Зайти в комнату по коду
`{client.command_prefix}start [код игры]` ~ Начать игру по коду (Только для создателя комнаты)""", color=discord.Color.orange())
	emb.set_thumbnail(url=ctx.guild.icon_url)
	await ctx.send(embed = emb)

@client.command()
async def play(ctx):
	if users[ctx.author.id]:
		emb = discord.Embed(title="Ошибка", description=f"""
Вы уже в комнате `{users[ctx.author.id]}`""", color=discord.Color.red())
	else:
		c = code()
		while c in rooms:
			c = code()
		emb = discord.Embed(title="Комната создана!", description=f"""
`{client.command_prefix}join {c}`""", color=discord.Color.dark_gold())
		users[ctx.author.id]=c
		rooms[c]={"owner":ctx.author.id, "start":False, "lobby":[ctx.author.id], "users":{}, "cords":{}, "map":"Звездолёт", "votes":{}, "voiting":False, "tasks":0}
	emb.set_thumbnail(url=ctx.author.avatar_url)
	await ctx.send(embed = emb)

@client.command()
async def join(ctx, c=None):
	if c is None:
		emb = discord.Embed(title="Ошибка", description="""
Укажите код комнаты!""", color=discord.Color.red())
	elif not c in rooms:
		emb = discord.Embed(title="Ошибка", description=f"""
Комната {c} не существует!""", color=discord.Color.red())
	elif users[ctx.author.id]==c:
		emb = discord.Embed(title="Ошибка", description=f"""
Вы уже в комнате `{c}`""", color=discord.Color.red())
	elif rooms[c]["start"]:
		emb = discord.Embed(title="Ошибка", description=f"""
Игра `{c}` уже началась!""", color=discord.Color.red())
	elif len(rooms[users[ctx.author.id]]["lobby"])==10:
		emb = discord.Embed(title="Ошибка", description=f"""
Достигнут лимит в 10 игроков!""", color=discord.Color.red())
	else:
		users[ctx.author.id]=c
		rooms[c]["lobby"].append(ctx.author.id)
		emb = discord.Embed(title="Присоединение", description=f"""
Вы успешно присоединились к комнате {c}
Создатель: <@{rooms[c]["owner"]}>""", color=discord.Color.green())
	emb.set_thumbnail(url=ctx.author.avatar_url)
	await ctx.send(embed = emb)

@client.command()
async def start(ctx):
	if not users[ctx.author.id]:
		emb = discord.Embed(title="Ошибка", description="""
Для начала создайте игру!""", color=discord.Color.red())
	elif rooms[users[ctx.author.id]]["owner"]!=ctx.author.id:
		emb = discord.Embed(title="Ошибка", description=f"""
Вы не создатель комнаты, в которой вы находитесь!
Создатель: <@{rooms[users[ctx.author.id]]["owner"]}>""", color=discord.Color.red())
	elif len(rooms[users[ctx.author.id]]["lobby"])<3:
		emb = discord.Embed(title="Ошибка", description=f"""
Минимум 3 игрока!
Игроки: `{len(rooms[users[ctx.author.id]]["lobby"])}`""", color=discord.Color.red())
	else:
		emb = discord.Embed(title="Начало игры", description=f"""
Запускаем игру `{users[ctx.author.id]}`...""", color=discord.Color.green())
		smsg = await ctx.send(embed = emb)
		emb = discord.Embed(title="Передвижение", description=f"""
Локация: `{locations[rooms[users[ctx.author.id]]["map"]][1][1]}`
Игроки: `{", ".join(["["+client.get_user(i).name+":Живой]" for i in rooms[users[ctx.author.id]]["lobby"]])}`""", color=discord.Color.blurple())
		emb.set_thumbnail(url=ctx.author.avatar_url)
		user = random.choice(rooms[users[ctx.author.id]]["lobby"])
		rooms[users[ctx.author.id]]["imposter"]=user
		await client.get_user(user).send("Ваша роль: Предатель")
		msg = await client.get_user(user).send(embed=emb)
		for i in keys+["☠"]:
			await msg.add_reaction(i)
		rooms[users[ctx.author.id]]["users"][user]={"dead":False,"tasks":[["Фейк", [random.choice(tasks)[1][0], 0, "Фальшивое задание"]] for i in range(random.randint(1, 5))], "btns":1, "taskcd":0, "msg":msg, "voted":False}
		rooms[users[ctx.author.id]]["cords"][user]=[1, 1]
		rooms[users[ctx.author.id]]["votes"][user]=0
		other = json.loads(str(rooms[users[ctx.author.id]]["lobby"]))
		other.remove(user)
		for i in other:
			await client.get_user(user).send("Ваша роль: Член экипажа")
			msg = await client.get_user(i).send(embed=emb)
			for i in keys:
				await msg.add_reaction(i)
			rooms[users[ctx.author.id]]["users"][i]={"dead":False, "tasks":[random.choice(tasks) for i in range(random.randint(1, 5))], "btns":1, "taskcd":0, "msg":msg, "voted":False}
			rooms[users[ctx.author.id]]["tasks"]+=len(rooms[users[ctx.author.id]]["users"][i]["tasks"])
			rooms[users[ctx.author.id]]["cords"][i]=[1, 1]
			rooms[users[ctx.author.id]]["votes"][i]=0
		emb = discord.Embed(title="Начало игры", description=f"""
Вы успешно начали игру `{users[ctx.author.id]}`""", color=discord.Color.green())
		await smsg.edit(embed=emb)
		rooms[users[ctx.author.id]]["start"]=True

@client.command()
async def map(ctx):
	if not users[ctx.author.id]:
		emb = discord.Embed(title="Ошибка", description=f"""
Вы не в комнате!""", color=discord.Color.red())
	elif not rooms[users[ctx.author.id]]["start"]:
		emb = discord.Embed(title="Ошибка", description=f"""
Игра `{users[ctx.author.id]}` не началась!""", color=discord.Color.red())
	else:
		l = max([len(i) for i in locations[rooms[users[ctx.author.id]]["map"]]])
		ll = locations[rooms[users[ctx.author.id]]["map"]]
		mapstr = ""
		for y in range(len(ll)):
			for x in range(l):
				if [x, y]==rooms[users[ctx.author.id]]["cords"][ctx.author.id]:
					mapstr+="🙂"
				elif x < len(ll[y]):
					if [i for i in rooms[users[ctx.author.id]]["users"][ctx.author.id]["tasks"] if i[1][0]==locations[rooms[users[ctx.author.id]]["map"]][y][x]]!=[]:
						mapstr+="🔧"
					elif [x, y] in list(rooms[users[ctx.author.id]]["cords"].values()):
						mapstr+="○"
					else:
						mapstr+="□"
				elif [x, y] in list(rooms[users[ctx.author.id]]["cords"].values()):
					mapstr+="○"
				else:
					mapstr+="■"
			mapstr+="\n"
		emb = discord.Embed(title="Карта игры", description=mapstr, color=discord.Color.blurple())
	await ctx.send(embed=emb)

@client.command()
async def vote(ctx, num=None):
	if not users[ctx.author.id]:
		emb = discord.Embed(title="Ошибка", description=f"""
Вы не в комнате!""", color=discord.Color.red())
	elif not rooms[users[ctx.author.id]]["start"]:
		emb = discord.Embed(title="Ошибка", description=f"""
Игра `{users[ctx.author.id]}` не началась!""", color=discord.Color.red())
	elif rooms[users[ctx.author.id]]["users"][ctx.author.id]["voted"]:
		emb = discord.Embed(title="Ошибка", description=f"""
Вы уже проголосовали!""", color=discord.Color.red())
	elif not num.isdigit():
		emb = discord.Embed(title="Ошибка", description=f"""
Уквжите число!""", color=discord.Color.red())
	elif int(num)<0 or int(num)>len(rooms[users[ctx.author.id]]["lobby"]):
		emb = discord.Embed(title="Ошибка", description=f"""
Укажите число от 0 до {len(rooms[users[ctx.author.id]]["lobby"])-1}!""", color=discord.Color.red())
	elif rooms[users[ctx.author.id]]["users"][rooms[users[ctx.author.id]]["lobby"][int(num)]]["dead"]:
		emb = discord.Embed(title="Ошибка", description=f"""
Нельзя голосовать за мёртвых!""", color=discord.Color.red())
	else:
		rooms[users[ctx.author.id]]["users"][ctx.author.id]["voted"]=True
		rooms[users[ctx.author.id]]["votes"][rooms[users[ctx.author.id]]["lobby"][int(num)]]+=1
		emb = discord.Embed(title="Голосование", description=f"""
Вы проголосовали за `{client.get_user(rooms[users[ctx.author.id]]["lobby"][int(num)]).name}`!""", color=discord.Color.green())
	await ctx.send(embed=emb)
	if len([i for i in rooms[users[ctx.author.id]]["lobby"] if rooms[users[ctx.author.id]]["users"][i]["voted"]])==len(rooms[users[ctx.author.id]]["lobby"]):
		user=list(rooms[users[ctx.author.id]]["votes"].keys())[list(rooms[users[ctx.author.id]]["votes"].values()).index(max(list(rooms[users[ctx.author.id]]["votes"].values())))]
		rooms[users[ctx.author.id]]["users"][user]["dead"]=True
		if rooms[users[ctx.author.id]]["imposter"]==user:
			emb = discord.Embed(title="Голосование", description=f"""
`{client.get_user(user).name}` был предателем!
Победа членов экипажа!""", color=discord.Color.green())
		else:
			emb = discord.Embed(title="Голосование", description=f"""
`{client.get_user(user).name}` не был предателем!""", color=discord.Color.green())
			if len([i for i in rooms[users[ctx.author.id]]["lobby"] if not rooms[users[ctx.author.id]]["users"]["dead"]])==2:
				emb = discord.Embed(title="Голосование", description=f"""
`{client.get_user(user).name}` не был предателем!
Победа предателя!""", color=discord.Color.green())
		rooms[users[ctx.author.id]]["votes"]={}
		c = users[ctx.author.id]
		for i in rooms[users[ctx.author.id]]["lobby"]:
			await client.get_user(i).send(embed=emb)
			rooms[users[i]]["votes"][i]=0
			rooms[users[i]]["users"][i]["voted"]=False
			rooms[users[i]]["cords"][i]=[1, 1]
			embd = discord.Embed(title="Передвижение", description=f"""
Локация: `{locations[rooms[users[i]]["map"]][1][1]}`
Игроки: `{", ".join(["["+client.get_user(i).name+":"+need[rooms[users[i]]["users"][i]["dead"]]+"]" for i in rooms[users[i]]["cords"]])}`
Задания: {", ".join([i[1][2] for i in rooms[users[ctx.author.id]]["users"][ctx.author.id]["tasks"] if i[1][0]==locations[rooms[users[ctx.author.id]]["map"]][1][1]])}""", color=discord.Color.blurple())
			await rooms[users[i]]["users"][i]["msg"].edit(embed = embd)
			if rooms[users[ctx.author.id]]["imposter"]==user:
				users[i]=False
		rooms[c]["voiting"]=False
		if not users[ctx.author.id]:
			rooms.pop(c, None)

client.run("ODEzNzQwMDM5MTcwMjkzODIx.YDTsdw.og44tawODftIRkVUpamFe8Fx__Q")