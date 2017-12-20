import serial
import time

class NexusRobot:

  def __init__(self, port):
    self.ser = serial.serial_for_url(port, 9600, do_not_open = True)
    self.ser.open()
    time.sleep(3)

  def _wait(self):
    self.ser.readline()
    self.ser.readline()

  def pause(self):
    time.sleep(1)
   
  def forward(self, speed, dist):
    self.ser.write("g%d,%d;" % (speed, dist))
    self._wait()

  def reverse(self, speed, dist):
    self.ser.write("b%d,%d;" % (speed, dist))
    self._wait()

  def turnRight(self, speed, angle):
    self.ser.write("rr%d,%d;" % (speed, angle))
    self._wait()

  def turnLeft(self, speed, angle):
    self.ser.write("rl%d,%d;" % (speed, angle))
    self._wait()

  def stop(self, speed=0):
    self.ser.write("s%d;" % (speed))
    self._wait()

  
     
if __name__ == '__main__'':
  try:
    robot = NexusRobot('/dev/cu.usbserial-AL00YYCA')
    while 1:
      robot.forward(200,20)
      robot.pause()
      robot.reverse(200,20)
      robot.pause()
#     robot.forward(200,10)
#     robot.pause()
#     robot.turnRight(200,90)
#     robot.pause()
#     robot.forward(200,10)
#     robot.pause()
#     robot.turnRight(200,90)
#     robot.pause()
#     robot.forward(200,10)
#     robot.pause()
#     robot.turnRight(200,90)
#     robot.pause()
  except KeyboardInterrupt:
    robot.stop()
  except BasicException:
    raise
