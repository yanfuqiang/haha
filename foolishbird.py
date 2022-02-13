'''
	Foolishbird2.0版本
	注意：可能会有一些bug，使用者自行修复
	      还有地方写法可能较差
'''
import websocket
import json
import re
import os
import fanyi
import re
import tkinter
from tkinter import *
from tkinter import scrolledtext 
import time
from multiprocessing import Process
from multiprocessing import Queue
import threading
import random
from study.study import Handle
from study.study import Chatobj

def sendd(text):
	'''
		text:发送的内容
	'''
	return json.dumps({"cmd":"chat","text":str(text)})

	
class Runbox:
	def __init__(self,room,name):
		# 包含了房间名称，bot的名称
		self.room = room
		self.name = name
		self.roll_player_list = []
		self.roll_start_num = 0
		self.roll_status = False
		self.roll_lim = None
		self.blacklist = []
		self.afk_user = {}
		self.user_talk_time = {}

	
	def handle(self,json_data,ws):
		'''
			将对应的cmd类型和对应的函数结合
		'''
		self.ws = ws
		self.json_data = json_data
		if "cmd" in self.json_data:    # 如果接受到了包含cmd的json数据
			# 说话类型
			if self.json_data["cmd"] == "chat":
				self.chat()

			# 用户进入类型
			elif self.json_data["cmd"] == "onlineAdd":
				self.onlineadd()

			# 进入聊天时用户的列表
			elif self.json_data["cmd"] == "onlineSet":
				self.onlineset()

			elif self.json_data["cmd"] == "onlineRemove":
				self.onlineremove()

			else:
				pass
	
	def chat(self):
		'''
			当json数据中的cmd是chat类型将会调用
		'''

		# 关于不同的数据的处理方式
		# if self.json_data["nick"] != self.name:         # 如果不是foolishbird自己说的话
		# 	# if self.json_data["text"] in ["hello","hi"]:     # 打招呼
		# 	# 	self.ws.send(sendd("hello,{}".format(self.json_data["nick"])))
				
		# 	# elif self.json_data["text"] in ["who are you"]:
		# 	# 	self.ws.send(sendd("I am a modern robot called foolishbird.I'm not foolish!"))
			
		# 	# elif self.json_data["text"] in ["fuck you","bitch"]:
		# 	# 	time.sleep(1)
		# 	# 	self.ws.send(sendd("...You've changed."))
			
		# 	# elif self.json_data["text"] in ["how to use this website"]:
		# 	# 	self.ws.send(sendd("https://tieba.baidu.com/p/6833224084"))
			
		# 	# elif self.json_data["text"] in ["image"]:
		# 	# 	self.ws.send(sendd("https://imgtu.com/"))
			
		# 	# elif re.findall(r"^\*\*.+$",self.json_data["text"]) != []:    # 在说的话前加上两个星号可以实现翻译
		# 	# 	self.ws.send(sendd(fanyi.fanyi(re.findall(r"^\*\*(.+)$",self.json_data["text"])[0]))) 
				
		# 	# elif self.json_data["text"] in ["how are you"]:
		# 	# 	self.ws.send(sendd("I,m fine"))

		# 	# elif self.json_data["text"] in ["afk"]:
		# 	# 	self.ws.send(sendd(r"**@{} is now afk**".format(self.json_data["nick"])))

		# 	# else:
		# 	# 	#self.ws.send(sendd(talk(self.json_data["text"])))
		# 	# 	...
		# 智能回复模块
		# if self.json_data["nick"] != self.name:
		# 	with open("./lu.txt","r") as fp:
		# 		content = fp.read()
		# 		tuple_obj_list = re.findall(r"(\w+)\n(.+)\n\n",content)
		# 	chatobj_list = []
		# 	for index,tuple_obj in enumerate(tuple_obj_list):
		# 		chatobj_list.append(Chatobj(tuple_obj))
		# 	handle = Handle(chatobj_list)
		# 	a = self.json_data["text"]
		# 	txt = ""
		# 	print(handle.count(handle.find_ans(a),way=1))
		# 	print(handle.count(handle.find_ans(a),way=2))
		# 	for text,times in handle.count(handle.find_ans(a),way=1).items():
		# 		if times >= 3:
		# 			for text,chance in handle.count(handle.find_ans(a),way=2).items():
		# 				if chance >= 15:
		# 					print("最佳方案=================")
		# 					print("次数：",times)
		# 					print("概率：",chance,"%")
		# 					txt = text
		# 					break
		# 		if txt != "":
		# 			break
		# 	self.ws.send(sendd(txt))

		# 真心话
		if self.json_data["nick"] != self.name and self.json_data["nick"] not in self.blacklist:
			# 如果有管理员的话游戏才能进行
			if self.roll_lim != None:
				# 如果输入内容等于roll join的话，意味着玩家加入但玩家不能是管理员，因为管理员已经在列表里了
				if self.json_data["text"] == "roll join" and self.json_data["nick"] != self.roll_lim:
					# 如果人数已经满了
					if len(self.roll_player_list) >= self.roll_start_num:
						self.ws.send(send("人数已满"))
					# 如果这个玩家不在列表中而且人数也没有满
					if self.json_data["nick"] not in self.roll_player_list and len(self.roll_player_list) < self.roll_start_num:
						# 那么就添加他到玩家列表
						self.roll_player_list.append(self.json_data["nick"])
						self.ws.send(sendd("{}加入了游戏,已有{}人加入了游戏".format(self.json_data["nick"],len(self.roll_player_list))))
				# 如果输入内容等于roll left，这意味着谁都可以退出游戏（包括管理员）
				if self.json_data["text"] == "roll left":
					# 如果这个人在玩家列表中而且是普通玩家
					if self.json_data["nick"] in self.roll_player_list and self.json_data["nick"] != self.roll_lim:
						# 从列表中清除他
						del self.roll_player_list[self.roll_player_list.index(self.json_data["nick"])]
						self.ws.send(sendd("{}离开了游戏,剩余{}人".format(self.json_data["nick"],len(self.roll_player_list))))
					# 如果这个退出的人是管理员
					if self.json_data["nick"] == self.roll_lim:
						self.ws.send(sendd("管理员{}已离开游戏，请重新开始".format(self.roll_lim)))
						# 不仅从列表中清楚他，而且将管理员设置为待定（None）
						self.roll_lim = None
						self.roll_player_list = []
						self.blacklist = []
				# 如果输入内容等于roll start而且管理员身份
				if self.json_data["text"] == "roll start" and self.json_data["nick"] == self.roll_lim:
					# 玩家大于一，也就是最少两人的时候。开始游戏
					if len(self.roll_player_list) > 1:
						as_a = random.choice(self.roll_player_list)
						as_b = ""
						while True:
							as_b = random.choice(self.roll_player_list)
							if as_a != as_b:
								break
						self.ws.send(sendd("请{}向{}提出问题".format(as_a,as_b)))
					else:
						self.ws.send(sendd("人数不足"))

				if self.json_data["text"] == "roll list":
					string = ""
					for i in self.roll_player_list:
						string = string + "**{}**".format(i) + " , "
					self.ws.send(sendd(string.rstrip(", ")))

			if self.json_data["nick"] == self.roll_lim:
				pattern1 = r"^kick (@?\w+)$"
				match1 = re.findall(pattern1,self.json_data["text"].strip())
				if match1 != []:
					if match1[0].lstrip("@") in self.roll_player_list and match1[0].lstrip("@") != self.roll_lim:
						del self.roll_player_list[self.roll_player_list.index(match1[0].lstrip("@"))]
						self.ws.send(sendd("{}被管理员踢出了游戏".format(match1[0].lstrip("@"))))
				pattern2 = r"^blacklist (@?\w+)$"
				match2 = re.findall(pattern2,self.json_data["text"].strip())
				if match2 != []:
					if match2[0].lstrip("@") not in self.blacklist and match2[0].lstrip("@") != self.roll_lim:
						self.blacklist.append(match2[0].lstrip("@"))
						self.ws.send(sendd("{}被管理员加入了黑名单".format(match2[0].lstrip("@"))))
				pattern3 = r"^blacklist rm (@?\w+)$"
				match3 = re.findall(pattern3,self.json_data["text"].strip())
				if match3 != []:
					if match3[0].lstrip("@") in self.blacklist:
						del self.blacklist[self.blacklist.index(match3[0].lstrip("@"))]
						self.ws.send(sendd("{}被管理员从黑名单移除".format(match3[0].lstrip("@"))))

			if self.json_data["nick"] == self.roll_lim or self.roll_lim == None:
				# 没有管理员的话
				pattern = r"^reset ([0-9]+)$"
				match = re.findall(pattern,self.json_data["text"].strip())
				# 如果有匹配的结果：数字
				if match != []:
					if int(match[0]) > 1:
						# 将游戏人数设置为这个
						self.roll_start_num = int(match[0])
						# 管理员设置为这个人
						self.roll_lim = self.json_data["nick"]
						# 游戏人数列表中添加这个人
						self.roll_player_list.append(self.json_data["nick"])
						self.ws.send(sendd("已将最多人数设置为{},{}为管理员".format(self.roll_start_num,self.roll_lim)))
			if self.json_data["text"].strip() == "roll help":
				self.ws.send(sendd("> roll 10 创建游戏设置人数并成为管理员\n"
								   "> roll join 玩家加入\n"
								   "> roll left 玩家退出\n"
								   "> roll start 人数合适时管理员开始游戏\n"
								   "> roll list 查看加入游戏的用户\n"
								   "> kick 踢出用户\n"
								   "> blacklist 将用户加入黑名单\n"
								   "> blacklist rm 将用户从黑名单移除"))

		# afk
		if self.json_data["nick"] != self.name:
			afk_pattern = r"afk (\w+)"
			afk_match = re.findall(afk_pattern,self.json_data["text"].strip())

			if self.json_data["nick"] in self.afk_user:
				if afk_match == [] and self.json_data["text"].strip() != "afk":
					self.ws.send(sendd("{}欢迎回来!".format(self.json_data["nick"])))
					del self.afk_user[self.json_data["nick"]]

				if afk_match != [] or self.json_data["text"].strip() == "afk":
					self.ws.send(sendd("{}停止了{}，但没完全停止。".format(self.json_data["nick"],self.afk_user[self.json_data["nick"]])))
					del self.afk_user[self.json_data["nick"]]
			if afk_match != []:
				self.ws.send(sendd("{}开始{}".format(self.json_data["nick"],afk_match[0])))
				self.afk_user[self.json_data["nick"]] = afk_match[0]

			# 这段我他喵的写不了了
			# if self.json_data["nick"] in self.user_talk_time:
			# 	if self.json_data["time"]-self.user_talk_time[self.json_data["nick"]] >= 3000000: # 如果超过了5分钟则算作挂机
			# 		if self.json_data["nick"] not in self.afk_user:
			# 			self.afk_user[self.json_data["nick"]] = "摸鱼"
			# else:
			# 	self.user_talk_time[self.json_data["nick"]] = self.json_data["time"]

			if self.json_data["text"].strip() == "afk":
				self.ws.send(sendd("{}开始摸鱼".format(self.json_data["nick"])))
				self.afk_user[self.json_data["nick"]] = "摸鱼"

			for name in self.afk_user:
				if "@{}".format(name) in self.json_data["text"]:
					self.ws.send(sendd("{}正在{}".format(name,self.afk_user[name])))

	
	def onlineadd(self):
		'''
			当json数据中的cmd是onlineAdd类型将会调用
		'''
		self.ws.send(sendd("hello,{}".format(self.json_data["nick"])))
		
	def onlineset(self):
		'''
			当json数据中的cmd是onlineSet类型将会调用
		'''
		#for t in self.json_data["nicks"]:
			#self.ws.send(sendd("hello,{}".format(t)))
		pass

	def onlineremove(self):
		if self.json_data["nick"] in self.roll_player_list and self.json_data["nick"] != self.roll_lim:
			# 从列表中清除他
			del self.roll_player_list[self.roll_player_list.index(self.json_data["nick"])]
			self.ws.send(sendd("{}离开了游戏,剩余{}人".format(self.json_data["nick"],len(self.roll_player_list))))
		# 如果这个退出的人是管理员
		if self.json_data["nick"] == self.roll_lim:
			self.ws.send(sendd("管理员{}已离开游戏，请重新开始".format(self.roll_lim)))
			# 不仅从列表中清楚他，而且将管理员设置为待定（None）
			self.roll_lim = None
			self.roll_player_list = []
			self.blacklist = []
			
class Main:
	def __init__(self,room,name,q,ttomq,execq):
		'''
			从ProBot传来的参数
		'''
		self.auto = True        # 自动回复开关，True为开启,False为关闭
		self.translate = False    # 翻译开关，True为开启,False为关闭
		self.runbox = Runbox(room,name)   # 处理信息库，主要负责自动回复
		self.room = room
		self.name = name
		self.pbuser = []
		self.q = q                 # 将从hackchat收到的消息发送到Tkhand
		self.ttomq = ttomq         # 接收从Tkhand传来的消息并发送到hackchat
		self.execq = execq         # 接收来自Tkhand 传来的指令

	def askmsg(self,ws):
		'''
		    一直向queue队列中询问有没有消息，如果有就发送
		'''
		while True:  
			if not self.ttomq.empty():
				if self.translate:
					ws.send(sendd(fanyi.fanyi(self.ttomq.get())))
				else:
					ws.send(sendd(self.ttomq.get()))

	def askexec(self,ws):
		'''
			向execq队列询问有没有消息，如果有就执行
		'''
		while True:
			if not self.execq.empty():
				execing = self.execq.get().strip()

				cmd_name = r"(\w+) \[.+\]"
				obj = r"\w+ \[(.+)\]"
				alone_cmd = r"^(\w+)$"
 
				cmd_name_m = re.findall(cmd_name,execing)
				obj_m = re.findall(obj,execing)
				alone_cmd_m = re.findall(alone_cmd,execing)
				try:
					cmd = cmd_name_m[0]
					obj = obj_m[0]
				except:
					cmd = None
					obj = None

				try:
					alone_cmd = alone_cmd_m[0]
				except:
					alone_cmd = None

				# cmd : 命令的名称
				## args : 包含命令的列表
				# obj : 对象的名称

				if cmd == "fuck":
					with open("./ma.txt","r") as fp:
						ma_list = fp.readlines()
						if obj != "":
							self.ttomq.put("@{},{}".format(obj,random.choice(ma_list)))
						else:
							self.ttomq.put("{}".format(random.choice(ma_list)))

				if cmd == "wfuck":
					with open("./ma.txt","r") as fp:
						ma_list = fp.readlines()
						if obj != "":
							self.ttomq.put("/whisper @{} {}".format(obj,random.choice(ma_list)))

				if cmd == "auto":
					if obj == "False":
						self.auto = False
						self.tkshow("### 自动回复已关闭")
					if obj == "True":
						self.auto = True
						self.tkshow("### 自动回复已开启")

				if cmd == "wt":
					if obj == "False":
						self.translate = False
						self.tkshow("### 翻译已关闭")
					if obj == "True":
						self.translate = True
						self.tkshow("### 翻译已开启")

				if alone_cmd == "help":
					help_msg = "### auto [False或True]\n### wt [False或True] <---开或关翻译\n"\
							   "### pb [屏蔽对象]\n### delpb [解除屏蔽的对象]\n### showpb <---查看屏蔽列表"
					self.tkshow(help_msg)

				if cmd == "pb" and obj != "":
					if self.pbuser.count(obj) == 0:
						self.pbuser.append(obj)
						self.tkshow("### 已屏蔽来自{}的信息".format(obj))
					else:
						self.tkshow("### {}已存在于屏蔽名单".format(obj))

				if cmd == "delpb" and obj != "":
					if self.pbuser.count(obj) == 1:
						del self.pbuser[self.pbuser.index(obj)]
						self.tkshow("### 已从屏蔽名单中移除{}".format(obj))
					else:
						self.tkshow("### 未找到{}".format(obj))

				if alone_cmd == "showpb":
					pblist = ""
					for every in self.pbuser:
						pblist = pblist + "### " + every + "\n"
					self.tkshow(pblist)

	def tkshow(self,text):
		self.q.put(text)
		
	def on_message(self,ws,message):
		js_ms = json.loads(message)
		if self.auto:
			self.runbox.handle(js_ms,ws)
		if js_ms["cmd"] == "emote":
			self.tkshow("[INFO]:{}".format(js_ms["text"]))
		if js_ms["cmd"] == "onlineSet":
			onlineuser = "Onlineuser:"
			for e in js_ms["nicks"]:
				if e != js_ms["nicks"][-1]:
					onlineuser = onlineuser + e + ","
				else:
					onlineuser = onlineuser + e
			self.tkshow(onlineuser)
		if js_ms["cmd"] == "chat" and js_ms["nick"] not in self.pbuser:
			with open("./lu.txt","a+") as fp:
				ms = js_ms["nick"] + "\n" + js_ms["text"] + "\n\n"
				fp.write(ms)
			if self.translate:
				pattern = r"[^\u4e00-\u9fa5\u3002\uff1f\uff01\uff0c\u3001\uff1b\uff1a"\
					       "\u300c\u300d\u300e\u300f\u2018\u2019\u201c\u201d\uff08\uff09"\
					       "\u3014\u3015\u3010\u3011\u2014\u2026\u2013\uff0e\u300a\u300b"\
					       "\u3008\u3009\u0032-\u0064\u0091-\u0096\u0123-\u0127]"
				if re.findall(pattern,js_ms["text"]) != [] and js_ms["nick"] != self.name:
					self.tkshow("{}:{}".format(js_ms["nick"],fanyi.fanyi(js_ms["text"])))
				else:
					self.tkshow("{}:{}".format(js_ms["nick"],js_ms["text"]))
			else:
				self.tkshow("{}:{}".format(js_ms["nick"],js_ms["text"]))
		if js_ms["cmd"] == "onlineAdd":
			self.tkshow("* {} join".format(js_ms["nick"]))
		if js_ms["cmd"] == "onlineRemove":
			self.tkshow("* {} left".format(js_ms["nick"]))
		if js_ms["cmd"] == "info":
			self.tkshow("[INFO]:{}".format(js_ms["text"]))
		
	def on_error(self,ws,error):
		'''
		    如果发生错误了则调用
		'''
		self.tkshow("error:{}".format(error))

	def on_close(self,ws):
		'''
		    如果退出了则调用
		'''
		print("### closed ###")
		
	def on_open(self,ws):
		'''
		    连接上服务器了则调用
		'''
		self.readttomp = threading.Thread(target=self.askmsg,args=(ws,)) 
		self.readttomp.start()
		self.readexecq = threading.Thread(target=self.askexec,args=(ws,)) 
		self.readexecq.start()
		ws.send(json.dumps({"cmd": "join", "channel": str(self.room), "nick": str(self.name)}))


class Tkhand(Process):
	def __init__(self,q,ttomq,execq):
		Process.__init__(self)
		self.q = q
		self.ttomq = ttomq
		self.execq = execq
		
	def run(self):
		# tkinter 框架
		# row 行
		# column 列
		# sticky
		self.top = Tk()
		self.top.title("foolishbird control")
		#self.top.configure(bg="#FAF9DE")
		self.show_text = scrolledtext.ScrolledText(self.top, width=105, relief=GROOVE,height=35)
		self.show_text.grid(row=0,column=0,columnspan=2)

		self.enter_text = scrolledtext.ScrolledText(self.top,width=88,height=5,relief=GROOVE)
		self.enter_text.grid(row=2,column=0,rowspan=1,ipady=0)

		self.send_button = Button(self.top,text="SEND",width=15,relief=GROOVE,height=3,command=self.sendmsg)
		self.send_button.grid(row=2,column=1,rowspan=1)

		self.exec_button = Button(self.top,text="EXEC",width=15,height=1,relief=GROOVE,command=self.exec)
		self.exec_button.grid(row=1,column=1,sticky="s")

		self.exec_label = Label(self.top,text="$")
		self.exec_label.grid(row=1,column=0,padx=3,sticky="w")

		self.exec_text = Text(self.top,width=85,height="1p",relief=GROOVE,foreground="red")
		self.exec_text.grid(row=1,column=0,sticky="e",ipady=6)

		#self.exec_s = Text(self.top,width=55,height=1,relief=GROOVE,foreground="blue")
		#self.exec_s.grid(row=1,column=0,columnspan=2,sticky="w")

		#threadread以线程的形式一直运行
		self.readq = threading.Thread(target=self.askmsg) 
		self.readq.start()

		self.top.mainloop()

	def askmsg(self):
		# 一直向q队列中询问有没有消息，如果有就提出
		while True:  
			if not self.q.empty():
				self.show_text.insert(END,self.q.get())
				self.show_text.insert(END,"\n\n")
				self.show_text.see(END)

	def sendmsg(self):
		'''
			发送信息：将输入框中的信息发到队列并由"Main"发送
			队列：ttomq
		'''
		msg = self.enter_text.get(1.0,END)
		if msg != "":
			self.enter_text.delete(1.0,END)
			self.ttomq.put(msg)

	def exec(self):
		self.execq.put(self.exec_text.get(1.0,END).strip())

		#self.exec_sl.destroy()


class ProBot(Process):
	def __init__(self,hcroom,botname,q,ttomq,execq):
		'''
			hcroom:聊天室名称
			botname:机器人的名称
			q:队列
			ttomp:队列
			execq:队列
		'''
		Process.__init__(self)
		# 调用main这个类传递所有参数
		self.main = Main(room=hcroom,name=botname,q=q,ttomq=ttomq,execq=execq)

	def run(self):
		'''
			连接hackchat
		'''
		websocket.enableTrace(True)
		ws = websocket.WebSocketApp("wss://hack.chat/chat-ws",
								on_message=self.main.on_message,
								on_error=self.main.on_error,
								on_close=self.main.on_close)
		ws.on_open=self.main.on_open	
		ws.run_forever()


if __name__ == '__main__':
	q = Queue()       # 如果收到消息就发送到这个队列，并由Tkhand显示出内容
	ttomq = Queue()   # 在Tkhand中把消息发送到ttomp这个队列，并由main处理发送到hackchat
	execq = Queue()   # 在Tkhand中把指令发送到execq这个队列，并在main中处理
	p1 = ProBot(hcroom="your-channel",botname="FoolishBird",q=q,ttomq=ttomq,execq=execq)
	p2 = Tkhand(q=q,ttomq=ttomq,execq=execq)
	p1.start()
	p2.start()
	p1.join()
	p1.join()
			
			
			
			
			
			
			
	
