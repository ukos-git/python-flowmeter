class MKFlowLogFile():
    def __init__(self, logfile):
        self.reset()
        self.logfile = logfile

    def reset(self):
        self.logfile = ''
        self.openmode = 'r'
        self.fsoOpen = False

    def open(self):
        if not self.fsoOpen:
            try:
                self.fso = open(self.logfile, self.openmode)
            except:
                self.close()
                raise ValueError('cannot open log file at ' + self.logfile)
            else:
                self.fsoOpen = True

    def close(self):
        if self.fsoOpen:
            try:
                self.fso.close()
            except:
                raise ValueError('cannot close log file at ' + self.logfile)
            else:
                self.fsoOpen = False

    def read(self):
        try:
            self.open()
            message1 = self.fso.readline()
            message2 = self.fso.readline()
            if (len(message2) == 0):
                raise EOF("end of file reached")
        except EOF:
            self.close()
            raise EOF
        except:
            message1 = ''
            message2 = ''
        return message1, message2

    def start(self):
        self.alive = True

    def stop(self):
        try:
            self.close()
            self.reset()
        except:
            print 'error closing logfile'
        else:
            self.alive = False

    def isReady(self):
        # ready while alive for log file
        return self.isAlive()

    def isAlive(self):
        return self.alive

class EOF(Exception):
    pass

