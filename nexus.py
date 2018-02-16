MAP_SIZE_PIXELS         = 500
MAP_SIZE_METERS         = 10
LIDAR_DEVICE            = '/dev/ttyACM0'
ROBOT_DEVICE            = '/dev/ttyUSB0'

import serial
import time

class NexusRobot:
    '''
    Nexus Robot Library for moving
    '''
    def __init__(self, port):
        self.ser = serial.serial_for_url(port, 9600, do_not_open=True)
        self.ser.open()
        self.pause(3)
        self._spd_calib = 1
        self._ang_calib = 1
        self._dis_calib = 1

    def _calib_spd(self, speed):
        return int(speed * self._spd_calib)

    def _calib_ang(self, angle):
        return int(angle * self._ang_calib)

    def _calib_dis(self, distance):
        return int(distance * self._dis_calib)

    def _wait(self):
        self.ser.readline()
        self.ser.readline()

    def get_telem(self):
        self.ser.write("t;".encode())
        vars = self.ser.readline().splitlines()[0].replace(";","").split(",")
        if vars[0] != "telem":
            return
        return vars[1:]

    def pause(self, duration=1):
        time.sleep(duration)

    def forward(self, speed, dist):
        self.ser.write(
            "g{0},{1};".format(self._calib_spd(speed), self._calib_dis(dist)).encode()
        )
        if dist > 0:
            self._wait()

    def backward(self, speed, dist):
        self.ser.write(
            "b{0},{1};".format(self._calib_spd(speed), self._calib_dis(dist)).encode()
        )
        if dist > 0:
            self._wait()

    def turnRight(self, speed, angle=-1):
        self.ser.write(
            "rr{0},{1};".format(self._calib_spd(speed), self._calib_ang(angle)).encode()
        )
        if angle > 0:
            self._wait()

    def turnLeft(self, speed, angle=-1):
        self.ser.write(
            "rl{0},{1};".format(self._calib_spd(speed), self._calib_ang(angle)).encode()
        )
        if angle > 0:
            self._wait()

    def rotateLeft(self, speed, angle=-1):
        self.ser.write(
            "r-{0},{1},-1;".format(
                self._calib_spd(speed), self._calib_spd(speed)).encode()
        )
        # self._wait()

    def rotateRight(self, speed, angle=-1):
        self.ser.write(
            "r{0},-{1},-1;".format(
                self._calib_spd(speed), self._calib_spd(speed)).encode()
        )
        # self._wait()

    def stop(self, speed=0):
        self.ser.write("s{0};".format(self._calib_spd(speed)).encode())

    def getInfo(self):
        self.ser.write("h;".encode())
        actual_l_speed = int(self.ser.readline().rstrip().split(':')[-1])
        target_l_speed = int(self.ser.readline().rstrip().split(':')[-1])
        actual_r_speed = int(self.ser.readline().rstrip().split(':')[-1])
        target_r_speed = int(self.ser.readline().rstrip().split(':')[-1])
        return actual_l_speed, target_l_speed, actual_r_speed, target_r_speed

from breezyslam.algorithms import RMHC_SLAM
from breezyslam.sensors import XVLidar as LaserModel
from breezyslam.vehicles import WheeledVehicle

from xvlidar import XVLidar as Lidar

from pltslamshow import SlamShow

class NexusRobotOd(WheeledVehicle):
    def __init__(self):
        WheeledVehicle.__init__(self, 55, 1200)

    def extractOdometry(self, timestamp, leftWheel, rightWheel):
        return (int(timestamp) / 1000.0, int(leftWheel) / 2.08, -int(rightWheel) / 2.08)

import signal
import sys
import thread
import readchar

def telem(params):
    speed = 150
    prev_k = None
    while 1:
        k = readchar.readchar()
        if k == 'w' and prev_k != k:
            print('Going Forward')
            robot.backward(speed, -1)
        elif k == 's' and prev_k != k:
            print('Going Backward')
            robot.forward(speed, -1)
        elif k == 'a' and prev_k != k:
            print('Turing left')
            robot.rotateLeft(speed, -1)
        elif k == 'd' and prev_k != k:
            print('Turning right')
            robot.rotateRight(speed, -1)
        elif k == ' ':
            print('Stopping')
            robot.stop()
        elif k == 'h':
            print('Printing info..')
            print(robot.getInfo())
        elif k == '+':
            speed += 20
            if speed > 400:
                speed = 400
            print('Config speed to: {0}'.format(speed))
        elif k == '-':
            speed -= 20
            if speed < 20:
                speed = 20
            print('Config speed to: {0}'.format(speed))
        elif k == '\x03':
            robot.stop()
            sys.exit(0)
        else:
            print('unrecognized key: {0}'.format(k))
        prev_k = k
        # robot.pause()



if __name__ == '__main__':
    import sys
    import tty
    import termios
    import signal
    from threading import Thread

    robot = None
    def signal_handler(signa, frame):
       robot.stop()
       sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        print('Initializing..')
        robot = NexusRobot(ROBOT_DEVICE)
        print('Initialized')
        t = Thread(target=telem, args=(robot,))
        t.daemon = True
        t.start()
        odomRobot = NexusRobotOd()
        # Connect to Lidar unit
        lidar = Lidar(LIDAR_DEVICE)

        # Create an RMHC SLAM object with a laser model and optional robot model
        slam = RMHC_SLAM(LaserModel(), MAP_SIZE_PIXELS, MAP_SIZE_METERS)

        # Set up a SLAM display
        display = SlamShow(MAP_SIZE_PIXELS, MAP_SIZE_METERS*1000/MAP_SIZE_PIXELS, 'SLAM')

        # Initialize an empty trajectory
        trajectory = []

        # Initialize empty map
        mapbytes = bytearray(MAP_SIZE_PIXELS * MAP_SIZE_PIXELS)

        while True:
            lidar_scan = lidar.getScan()
            telem = robot.get_telem()
            vel = odomRobot.computeVelocities(telem[0],telem[1],telem[2])

            # Update SLAM with current Lidar scan, using first element of (scan, quality) pairs
            slam.update([pair[0] for pair in lidar_scan], vel)

            # Get current robot position
            x, y, theta = slam.getpos()
            print '(' + str(x) + ',' + str(y) + ',' + str(theta) +')'

            # Get current map bytes as grayscale
            slam.getmap(mapbytes)

            display.displayMap(mapbytes)

            display.setPose(x, y, theta)

            # Exit on ESCape
            key = display.refresh()
            if key != None and (key&0x1A):
               robot.stop()
               exit(0)
    except KeyboardInterrupt:
        exit(0)
    except serial.serialutil.SerialException, e:
        print(str(e))
    except Exception:
	raise
