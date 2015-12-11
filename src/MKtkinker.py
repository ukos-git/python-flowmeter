#!/usr/bin/env python
import Tkinter as tk
import os

class swntReactorGUI(object):
	def __init__(self, master, **kwargs):
		# fullscreen
		self.master=master
		pad=3
		self.geometry_toggle='200x200+0+0'
		self.master.geometry("{0}x{1}+0+0".format(
			master.winfo_screenwidth()-pad, master.winfo_screenheight()-pad))
		# keyboard capture events.
		self.master.bind('<F4>',self.geometryToggle)
		self.master.bind('<Escape>',self.buttonShutdownFocus)
		self.master.bind("<Key>", self.key)
		self.master.bind("<Return>", self.newline)
		# GUI basics
		self.frame = tk.Frame(self.master, **kwargs)
		self.frame.pack()
		self.GUI()
		# init GUI Variables
		self.Buffer = ''
		self.LabelInputText.set("keyboard input")
	
	def key(self, event):
		self.BufferAdd(event.char)
				
	def newline(self, event):
		self.LabelInput.configure(fg='red')
		self.BufferSend()

	def GUI(self):
		# buttons
		self.buttonQuit	= tk.Button(self.frame, 
							 text="quit",
							 command=self.frame.quit)
		self.buttonQuit.pack(side=tk.LEFT)
		self.buttonShutdown = tk.Button(self.frame,
							 text="shutdown", fg="red",
							 command=self.buttonShutdownExec)
		self.buttonShutdown.pack(side=tk.LEFT)
		self.buttonShutdown.bind('<Return>', self.buttonShutdownExec)
		# labels
		self.LabelInputText = tk.StringVar()
		self.LabelInput = tk.Label(self.master, textvariable=self.LabelInputText)
		self.LabelInput.pack()		
	# Buttons
	def buttonShutdownExec(self,event=None):
		command1 = "/home/matthias/CVDapp/system/test"
		command2 = "/home/pi/CVDapp/system/shutdown"
		if os.path.isfile(command1):
			print "shutdown was pressed in test environment"
		if os.path.isfile(command2):
			os.system(command)
		self.frame.quit
		exit()
	def buttonShutdownFocus(self,event=None):
		self.buttonShutdown.focus()
	# Buffer
	def BufferAdd(self,char):		
		self.Buffer = self.Buffer + char		
		self.LabelInputText.set(self.Buffer)		
		self.LabelInput.configure(fg='blue')
	def BufferClear(self):
		self.Buffer = ''
	def BufferSend(self):
		print self.Buffer
		# this has to be logged to file so that t400 etc. can be redirected to existing programs.
		# a file is better than an instance because we can then control it at other instances too.
		# file should probably be in /var/local/run
		# after redirecting the content of file it has to be cleared.
		self.BufferClear()
		
	def geometryToggle(self,event=None):
		# event will be filled with Tkinter.Event when Key is Pressed. 
		# save old geom.
		geometry_old=self.master.winfo_geometry()
		# toggle to new
		self.master.geometry(self.geometry_toggle)
		self.geometry_toggle=geometry_old

root=tk.Tk()
app=swntReactorGUI(root)
root.mainloop()
