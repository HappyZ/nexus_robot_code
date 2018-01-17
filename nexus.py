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

    def pause(self, duration=1):
        time.sleep(duration)

    def forward(self, speed, dist):
        self.ser.write(
            "g{0},{1};".format(self._calib_spd(speed), self._calib_dis(dist))
        )
        if dist > 0:
            self._wait()

    def backward(self, speed, dist):
        self.ser.write(
            "b{0},{1};".format(self._calib_spd(speed), self._calib_dis(dist))
        )
        if dist > 0:
            self._wait()

    def turnRight(self, speed, angle=-1):
        self.ser.write(
            "rr{0},{1};".format(self._calib_spd(speed), self._calib_ang(angle))
        )
        if angle > 0:
            self._wait()

    def turnLeft(self, speed, angle=-1):
        self.ser.write(
            "rl{0},{1};".format(self._calib_spd(speed), self._calib_ang(angle))
        )
        if angle > 0:
            self._wait()

    def rotateLeft(self, speed, angle=-1):
        self.ser.write(
            "r-{0},{1},-1;".format(
                self._calib_spd(speed), self._calib_spd(speed))
        )
        # self._wait()

    def rotateRight(self, speed, angle=-1):
        self.ser.write(
            "r{0},-{1},-1;".format(
                self._calib_spd(speed), self._calib_spd(speed))
        )
        # self._wait()

    def stop(self, speed=0):
        self.ser.write("s{0};".format(self._calib_spd(speed)))

    def getInfo(self):
        self.ser.write("h;")
        actual_l_speed = int(self.ser.readline().rstrip().split(':')[-1])
        target_l_speed = int(self.ser.readline().rstrip().split(':')[-1])
        actual_r_speed = int(self.ser.readline().rstrip().split(':')[-1])
        target_r_speed = int(self.ser.readline().rstrip().split(':')[-1])
        return actual_l_speed, target_l_speed, actual_r_speed, target_r_speed


if __name__ == '__main__':
    import sys
    import tty
    import termios

    class _Getch:
        def __call__(self):
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                try:
                    tty.setraw(sys.stdin.fileno())
                    ch = sys.stdin.read(1)
                finally:
                    termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                return ch

    def get():
        inkey = _Getch()
        while 1:
            k = inkey()
            if k != '':
                break
        return k

    robot = None
    speed = 100
    try:
        print('Initializing..')
        robot = NexusRobot('/dev/cu.usbserial-AL00YYCA')
        print('Initialized')
        prev_k = None
        while 1:
            k = get()
            if k == 'w' and prev_k != k:
                print('Going Forward')
                robot.forward(speed, -1)
            elif k == 's' and prev_k != k:
                print('Going Backward')
                robot.backward(speed, -1)
            elif k == 'a' and prev_k != k:
                print('Turing left')
                robot.rotateLeft(speed, -1)
            elif k == 'd' and prev_k != k:
                print('Turing right')
                robot.rotateRight(speed, -1)
            elif k == ' ':
                print('Stopping')
                robot.stop()
            elif k == 'h':
                print('Printing info..')
                print(robot.getInfo())
            elif k == '+':
                speed += 20
                if speed > 200:
                    speed = 200
                print('Config speed to: {0}'.format(speed))
            elif k == '-':
                speed -= 20
                if speed < 20:
                    speed = 20
                print('Config speed to: {0}'.format(speed))
            elif k == '\x03':
                raise KeyboardInterrupt
            else:
                print('unrecognized key: {0}'.format(k))
            prev_k = k
            # robot.pause()
    except serial.serialutil.SerialException, e:
        print(str(e))
    except KeyboardInterrupt:
        if robot:
            robot.stop()
    except Exception:
        raise
