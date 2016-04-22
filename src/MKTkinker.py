#!/usr/bin/env python
import Tkinter as tk
import os
import MKDatabase

class swntReactorGUI(object):
    def __init__(self, master, **kwargs):
        # database connection
        self.db = MKDatabase.MKDatabase()
        # fullscreen
        self.master=master
        pad=30
        self.geometry_toggle='200x200+0+0'
        self.master.geometry("{0}x{1}+0+0".format(master.winfo_screenwidth(), master.winfo_screenheight()-pad))
        # keyboard capture events.
        self.master.bind('<F4>',self.geometryToggle)
        self.master.bind('<Escape>',self.buttonShutdownFocus)
        self.master.bind("<Key>", self.key)
        self.master.bind("<Return>", self.newline)
        self.master.bind("<KP_Enter>", self.newline)
        # GUI basics
        self.GUI(**kwargs)
        # init GUI Variables
        self.Buffer = ''
        self.bufferDisplay.set("press key")
        self.timerDisplay.set("")
        self.pressureDisplay.set("")
        self.temperatureDisplay.set("")
        self.argonDisplay.set("")
        self.ethanolDisplay.set("")
        self.timer = 0

    def key(self, event):
        self.LabelBufferDisplay.configure(fg='blue')
        self.BufferAdd(event.char)

    def newline(self, event):
        self.LabelBufferDisplay.configure(fg='red')
        self.BufferSend()

    def BufferAdd(self,char):
        if char == '/':
            char = 't'
        elif char == '+':
            char = 'e'
        elif char == '-':
            char = 'a'
        elif char == '*':
            char = 'p'
        self.Buffer = self.Buffer + char
        self.bufferDisplay.set(self.Buffer)

    def BufferSend(self):
        self.db.setMessage(self.Buffer)
        self.BufferClear()

    def BufferClear(self):
        self.Buffer = ''

    def update(self):
        # update database
        self.db.getAll()
        self.timer += 0.1
        # update labels
        self.timerDisplay.set("{0:.1f}".format(self.timer))
        self.pressureDisplay.set("{0:.2f} ({1:.0f})".format(self.db.pressure, self.db.spPressure))
        self.temperatureDisplay.set("{0:.0f} ({1:.0f})".format(self.db.temperature, self.db.spTemperature))
        self.argonDisplay.set("{0:.1f} ({1:.0f})".format(self.db.argon, self.db.spArgon))
        self.ethanolDisplay.set("{0:.1f} ({1:.0f})".format(self.db.ethanol, self.db.spEthanol))
        self.ip.set(self.db.ip)
        if self.db.isRecording(): # needs to call database every time
            self.filename.set(self.db.getLogFile())
        else:
            self.filename.set('')
        # schedule next call
        self.master.after(100, self.update)

    def GUI(self, **kwargs):
        # buttons
        self.frameQuit = tk.Frame(self.master, **kwargs)
        self.frameQuit.pack(side=tk.BOTTOM)
        self.filename = tk.StringVar()
        tk.Label(self.frameQuit, textvariable=self.filename, font=("Helvetica", 14)).pack(side=tk.LEFT)
        tk.Button(self.frameQuit, text="record", command=self.buttonRecord).pack(side=tk.LEFT)
        tk.Button(self.frameQuit, text="quit", command=self.master.quit).pack(side=tk.LEFT)
        self.buttonShutdown = tk.Button(
                self.frameQuit,
                text="shutdown", fg="red",
                command=self.buttonShutdownExec)
        self.buttonShutdown.pack(side=tk.LEFT)
        self.buttonShutdown.bind('<Return>', self.buttonShutdownExec)

        # label timer
        self.timerDisplay = tk.StringVar()
        tk.Label(self.frameQuit, textvariable=self.timerDisplay, font=("Helvetica", 14)).pack(side=tk.LEFT)

        # label ip
        self.ip = tk.StringVar()
        tk.Label(self.frameQuit, textvariable=self.ip, font=("Helvetica", 14)).pack(side=tk.LEFT)

        # input
        self.frameInput = tk.Frame(self.master, **kwargs)
        self.frameInput.pack(side=tk.TOP)
        self.bufferDisplay = tk.StringVar()
        tk.Label(self.frameInput, text="Input: ", font=("Helvetica", 64)).pack(side=tk.LEFT)
        self.LabelBufferDisplay = tk.Label(self.frameInput, textvariable=self.bufferDisplay, font=("Helvetica", 64))
        self.LabelBufferDisplay.pack(side=tk.RIGHT)

        # temperature
        self.frameTemperature = tk.Frame(self.master, **kwargs)
        self.frameTemperature.pack(side=tk.TOP)
        self.temperatureDisplay = tk.StringVar()
        tk.Label(self.frameTemperature, text="Temperature: ", font=("Helvetica", 64)).pack(padx=5,side=tk.LEFT)
        tk.Label(self.frameTemperature, textvariable=self.temperatureDisplay, font=("Helvetica", 64)).pack(side=tk.RIGHT)

        # pressure
        self.framePressure = tk.Frame(self.master, **kwargs)
        self.framePressure.pack(side=tk.TOP)
        self.pressureDisplay = tk.StringVar()
        tk.Label(self.framePressure, text="Pressure: ", font=("Helvetica", 64)).pack(padx=5,side=tk.LEFT)
        tk.Label(self.framePressure, textvariable=self.pressureDisplay, font=("Helvetica", 64)).pack(side=tk.RIGHT)

        # Argon
        self.frameArgon = tk.Frame(self.master, **kwargs)
        self.frameArgon.pack(side=tk.TOP)
        self.argonDisplay = tk.StringVar()
        tk.Label(self.frameArgon, text="Argon: ", font=("Helvetica", 64)).pack(padx=5,side=tk.LEFT)
        tk.Label(self.frameArgon, textvariable=self.argonDisplay, font=("Helvetica", 64)).pack(side=tk.RIGHT)

        # Ethanol
        self.frameEthanol = tk.Frame(self.master, **kwargs)
        self.frameEthanol.pack(side=tk.TOP)
        self.ethanolDisplay = tk.StringVar()
        tk.Label(self.frameEthanol, text="Ethanol: ", font=("Helvetica", 64)).pack(padx=5,side=tk.LEFT)
        tk.Label(self.frameEthanol, textvariable=self.ethanolDisplay, font=("Helvetica", 64)).pack(side=tk.RIGHT)

    def buttonShutdownExec(self,event=None):
        command1 = "/home/matthias/Documents/programs/python/swnt-reactor/script/shutdown"
        command2 = "/home/pi/programs/swnt-reactor/script/shutdown"
        if os.path.isfile(command1):
            print "shutdown was pressed in test environment"
        if os.path.isfile(command2):
            self.filename.set("shutdown in progress ...")
            os.system(command2)
        self.master.quit

    def buttonShutdownFocus(self,event=None):
        self.buttonShutdown.focus()

    def buttonRecord(self, event=None):
        if self.db.isRecording():
            self.db.stopRecording()
        else:
            self.db.startRecording()
        self.timer = 0

    def geometryToggle(self,event=None):
        # event will be filled with Tkinter.Event when Key is Pressed. 
        # save old geom.
        geometry_old=self.master.winfo_geometry()
        # toggle to new
        self.master.geometry(self.geometry_toggle)
        self.geometry_toggle=geometry_old

root=tk.Tk()
app=swntReactorGUI(root)
root.after(100, app.update)
root.mainloop()
