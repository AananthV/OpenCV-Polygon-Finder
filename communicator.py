import serial
import time

STOP, FORWARD, LEFT, RIGHT, ONEEIGHTY, FLASH = 0, 1, 2, 3, 4, 5

class Guider:

    def __init__(self, x, y):
        self.deltas = [[1,0],[0,1],[-1,0],[0,-1]]
        self.x = x
        self.y = y
        self.initx = x
        self.inity = y
        self.delta = []
        self.destx = 0
        self.desty = 0
        self.phase = 0
        self.arduino = serial.Serial('COM9', 38400, timeout=1)
        self.sensorOutputs = [0,0,0,0]
        self.mode = 0

    def receiveSensorOutputs(self):
        for i in range(self.arduino.in_waiting):
            self.sensorOutputs[i] = self.arduino.read()

    def detectJunction(self):
        self.receiveSensorOutputs()
        if self.sensorOutputs[0] and self.sensorOutputs[3]:
            self.x = self.x + self.delta[0]
            self.y = self.y + self.delta[1]
            if self.x == self.destx and self.y == self.desty:
                self.sendMotorLogic(STOP)
            elif self.x == self.destx:
                if self.y > self.desty:
                    self.right90()
                if self.y < self.desty:
                    self.left90()
            elif self.y == self.desty:
                if self.x > self.destx:
                    self.left90()
                if self.x < self.destx:
                    self.right90()
            else:
                self.lineFollower()
        else:
            self.lineFollower()


    def lineFollower(self):
        if self.sensorOutputs[1] and self.sensorOutputs[2]:
            self.sendMotorLogic(FORWARD)
        elif not self.sensorOutputs[1]:
            self.sendMotorLogic(RIGHT)
        elif not self.sensorOutputs[2]:
            self.sendMotorLogic(LEFT)
        time.sleep(0.05)
        self.detectJunction()

    def left90(self):
        self.sendMotorLogic(LEFT90)
        self.receiveSensorOutputs()
        while self.sensorOutputs[1] == 0 or self.sensorOutputs[2] == 0:
            self.sendMotorLogic(LEFT)
            self.receiveSensorOutputs()
        self.delta = (self.delta+1)%4
        self.lineFollower()


    def right90(self):
        self.sendMotorLogic(RIGHT90)
        self.receiveSensorOutputs()
        while self.sensorOutputs[1] == 0 or self.sensorOutputs[2] == 0:
            self.sendMotorLogic(RIGHT)
            self.receiveSensorOutputs()
        self.delta = (self.delta-1)%4
        self.lineFollower()

    def one80(self):
        self.sendMotorLogic(ONEEIGHTY)
        self.receiveSensorOutputs()
        while self.sensorOutputs[1] == 0 or self.sensorOutputs[2] == 0:
            self.sendMotorLogic(ONEEIGHTY)
            self.receiveSensorOutputs()
        self.delta = (self.delta+2)%4
        self.lineFollower()

    def stopBot(self):
        self.sendMotorLogic(FLASH)
        if self.phase == 1:
            self.initDest()
        else:
            self.nextDest()

    def detectPhase(self):
        self.phase = int(input("Enter Phase: ")) - 1

    def nextDest(self):
        self.destx = int(input("Enter Next x:"))
        self.desty = int(input("Enter Next y:"))
        if (self.x == self.destx and self.desty > self.y and self.delta == [0,-1]) or (self.x == self.destx and self.desty < self.y and self.delta == [0,1]) or (self.y == self.desty and self.destx > self.x and self.delta == [-1,0]) or (self.y == self.desty and self.destx < self.x and self.delta == [1,0]):
           self.one80()
        else:
            self.detectJunction()

    def initDest(self):
        self.destx = initx
        self.desty = inity
        if (self.x == self.destx and self.desty > self.y and self.delta == [0,-1]) or (self.x == self.destx and self.desty < self.y and self.delta == [0,1]) or (self.y == self.desty and self.destx > self.x and self.delta == [-1,0]) or (self.y == self.desty and self.destx < self.x and self.delta == [1,0]):
           self.one80()
        else:
            self.detectJunction()

    def sendMotorLogic(self, x):
        self.arduino.write(str(x).encode('utf-8'))

bot = Guider(2,-1)
bot.detectPhase()
bot.nextDest()
