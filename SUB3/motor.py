import serial
from threading import Thread
import logging
import time
import os
import subprocess
import win32pipe, win32file, pywintypes
import struct
import multiprocessing


# Constants
BAUD = 115200

def runC2():
    subprocess.run("C:/Program Files (x86)/Teknic/ClearView/sdk/examples/3a-Example-Motion/x64/Debug/LETREP-Full.exe")


class motor:
    def __init__(self, com, max, min):
        # Serial for communication with ESP32
        # self.ser = serial.Serial(com, BAUD, timeout=.1)

        self._comm_thread = None

        # Values for preload
        self._preload_max = max
        self._preload_min = min
        self._preload_emgV = []
        self._display_emgV = 0

        # Fire delay for framework fire point calculations
        self.FireDelay = 0
        self.FootSpeed = 0

        # Ack timeout in seconds
        self._ack_timeout = .4

        # Messages and their respective acks
        self._message_ack_enum = {
            "a": "enabled",  # Enabled Motor
            "b": "ack",  # Released Motor Fired Motor
            "c": "ack",  # Fired Motor
            "d": "disabled"  # Disabled Motor
        }

        # Flags for communcation/messaging thread
        self._read_msgs_flag = True
        self._message_received = False
        self._expected_message = ""

        # Flags for controlling motor
        self._fire_motor_flag = True

        #without a microcontroller, we don't use the above flags and letters^
        #instead, we use a pipe!
        #declare both pipes
          #pipe toCpp sends to C++
        #C++ client example reads from Foo; this writes to Foo
        self.toCpp = win32pipe.CreateNamedPipe(
          r'\\.\\pipe\\Foo',
          win32pipe.PIPE_ACCESS_DUPLEX,
          win32pipe.PIPE_TYPE_MESSAGE | win32pipe.PIPE_READMODE_MESSAGE | win32pipe.PIPE_WAIT,
           1, 65536, 65536,
           0,
           None)

        C_thread = multiprocessing.Process(target=runC2, args=())
        C_thread.start()

        #this function waits for a connection to the pipe toCpp
        win32pipe.ConnectNamedPipe(self.toCpp, None)

        #once connected, data can be sent as send_message(self.toCpp, word) where word is a variable*
        #*c expects a wchar_t array encoded to ascii, send_message currently encodes var given to a string
          #pipe fromCpp reads from C++
        #C++ server writes to Fan
        #this reads from Fan
        time.sleep(3)
        self.fromCpp = win32file.CreateFile(
            r'\\.\\pipe\\Fan',
            win32file.GENERIC_READ,
            0,
            None,
            win32file.OPEN_EXISTING,
            0,
            None
        )
        #once the above receiving pipe handle is created, the following can read from the cpp pipe
        #messages sent must always be read or a process will hang!
        #the below reads an array of bytes from the pipe 'fromCpp'
        #note readfile()[0] is a boolean regarding whether the file was read correctly
        #then, it decodes the bytes from readfile()[1] into the ascii symbols they represent
        #so resp contains a string (which probably had a number written to it on the C side)
        #and print prints that to console
        #resp = win32file.ReadFile(self.fromCpp, 64*1024)[1].decode('ascii')
        #        print(f"message: {resp}")
        #make sure you read when the pipe exists, the pipe is not closed, and a message has been sent
        #or you may encounter problems

        # Public variables for interfacing
        self.torque_update = False
        self.torque_value = 0
        self.pause_fire = True


    # def runC(self):



    def enable(self):
        """
        Sends enable command to the ESP32 to enable to clearpath motor
        """
        logging.debug("UART: Enabling Motor")
        self._send_message("a")
        
        # Release motor incase it might be up
        self.release()
    
    def send_message(self, pipe, words):
            # convert to bytes and write string to pipe
            #some_data = str.encode(f"{words}") #encodes variable words into an fstring, didn't help
            #other_data = bytes(chr(words).encode('utf-8')) #didn't help us
            #chop num into digits
            some_data = struct.pack('P', words) #encodes to ascii bytes C can read (7 is a bell sound!!!!!!!!!!!)
            win32file.WriteFile(pipe, some_data)

    def disable(self):
        """
        Sends disable command to the ESP32 to disable to clearpath motor
        """
        logging.debug("UART: Disabling Motor")
        self._send_message("d")

    def fire(self,speed):

        # **********************************************************************************************
        # Needs to be completely changed based on communication :)
        # **********************************************************************************************
        # """
        # Sends fire command to the ESP32 to actuate the clearpath motor to the raised position
        # """
        # logging.debug("UART: Firing Motor")
        # self._send_message("c")
        # FiringOutput = subprocess.run("C:/Program Files (x86)/Teknic/ClearView/sdk/examples/3a-Example-Motion/x64/Debug/LETREP-Motion.exe", capture_output=True, text=True)
        # TimeFire = FiringOutput.stdout.split()[-1]
        # self.FireDelay = int(TimeFire)-int(TimeCall)
        #the EMG sample rate is 4370 samples/second
        #FireDelay is in nanoseconds, and measures the time between calling the motor and the motor firing
        #self.fire_point = self.fire_point + FireDelay*4370/(1000000000)
        sendSpeed=int(((speed-135)/9)+6)

        TimeCall = time.time_ns()
        print("TimeCall: ", TimeCall)
        ##########################################################################################
        # Send speed through pipe
        self.send_message(self.toCpp, sendSpeed)
        ##########################################################################################
        ##########################################################################################
        # Recieve pipe time, store as TimeFire
        pipeTime = win32file.ReadFile(self.fromCpp, 64*1024)[1].decode('utf-16')
        TimeFire = int(pipeTime)
        print("TimeFire: ", TimeFire)

        #receive pipe duration, store as FireDuration
        pipeDuration = win32file.ReadFile(self.fromCpp, 64*1024)[1].decode('utf-16')
        FireDuration = float(pipeDuration)
        print("FireDuration: ", pipeDuration)
        self.FootSpeed = 6000/FireDuration
        print("FootSpeed: ", self.FootSpeed)
        ##########################################################################################
        self.FireDelay = int(TimeFire)-int(TimeCall)
        print("Delay: ", self.FireDelay)


    def release(self):
        """
        Sends release command to the ESP32 to return the clearpath motor to starting position
        """
        logging.debug("UART: Releasing Motor")
        self._send_message("b")

    ## Function to send messages (FOR MICROCONTROLLER and not pipes)
    # def _send_message(self,msg_to_send):

    #     if not self.ser.closed and msg_to_send in self._message_ack_enum.keys() :
    #         logging.debug(f"UART: Sending '{msg_to_send}'")
    #         self.ser.write(msg_to_send.encode())

    #             # If not received send again
    #         if not self._check_for_msg_received(self._message_ack_enum[msg_to_send]):

    #             logging.warning(f"UART: Ack for Message '{msg_to_send}' Not received, Resending")
    #             self.ser.write(msg_to_send.encode())
                
    #             if self._check_for_msg_received(self._message_ack_enum[msg_to_send]):
    #                 logging.error(f"UART: Ack for Message '{msg_to_send}' Not Received, Giving up")
    #         else:
    #             logging.debug(f"UART: Message '{msg_to_send}' was recevied")


    # Checks for a received message given timeout
    def _check_for_msg_received(self,expected_message):
        logging.debug(f"UART: Checking for expected message: {expected_message}")
        self._expected_message = expected_message
        start_time = time.time()
        while(True):
            # Wait for specified timeout
            if time.time() - start_time > self._ack_timeout:
                return False
            
            if self._message_received:
                return True
                


    def _read_msgs_from_esp(self):
        # """
        # Processes the next command and updates the torque value
        # """
        # while(self._read_msgs_flag):
        #     if self.ser.in_waiting > 0:
        #         try:
        #             data_from_ser = self.ser.readline().decode().strip()
        #             logging.debug(f"UART: Recevied '{str(data_from_ser)}'")
        #         except UnicodeDecodeError:
        #             logging.warning("Unicode Decode Error")
                
        #         # UART Message Parser
        #         if data_from_ser[:3] == "TOR":
        #             self.torque_value = float(data_from_ser.split(':')[1])
        #             self.torque_update = True
        #         elif data_from_ser == self._expected_message:
        #             self._message_received = True


        ################################################################################
        # Pipe 2
        self.send_message(self.toCpp, 2)
        ################################################################################
        ################################################################################
        # Recieve pipe theTrq, store as self.torque_value
        pipeTrq = win32file.ReadFile(self.fromCpp, 64*1024)[1].decode('utf-16')
        #print(f"message: {pipeTrq}") #print variable into an fstring
        #strungTrq = ''.join(map(chr, pipeTrq))
        #print(strungTrq)
        self.torque_value = float(pipeTrq)
        ################################################################################
        self.torque_update=True
        time.sleep(.01)

    def torque_preload_check(self):
        """
        Checks the motors torque:
        Returns 1 if force is greater than preload_max
        Return 0 if good
        Returens -1 if force is less than preload_min
        """
        #checks emg val instead now
        #self._display_emgV = self._preload_emgV[-1] #because app.py doesn't like to call list[-1]
        self._preload_emgV[-1]=abs(self._preload_emgV[-1])
        self._display_emgV = sum(self._preload_emgV[-500:])/500.0 #sasaki wants a rolling avg because it flickery
        self.torque_update=True
        if self._display_emgV > self._preload_max:
            return 1
        elif self._display_emgV < self._preload_min:
            return -1
        else:
            return 0


    def update_pre_emg(self,pre_emgV):
        self._preload_emgV = pre_emgV

    def update_preloads(self,pre_min, pre_max):
        self._preload_min = pre_min
        self._preload_max = pre_max

    def start(self):
        # """
        # Starts the system's threads and enables the motor
        # """
        # self._start_threads()
        # # Added sleep to allow esp to configure UART
        # time.sleep(1)
        # self.enable()
        # subprocess.run("C:/Program Files (x86)/Teknic/ClearView/sdk/examples/3a-Example-Motion/x64/Debug/LETREP-Home.exe")
        logging.info("Motor Homing")
        ####################################################################################################
        # Pipe 1
        self.send_message(self.toCpp, 1)
        ####################################################################################################


    def play_pause(self):
        """"
        Pauses the motor firing ability until turned back on
        """
        self.pause_fire = not self.pause_fire

    def exit(self):
        """
        Closes serial stops all threads and disables the motor
        """
        # Turn off motor
        logging.info("Motor is exiting")
        # self.disable()
        # time.sleep(4)
        # subprocess.run("C:/Program Files (x86)/Teknic/ClearView/sdk/examples/3a-Example-Motion/x64/Debug/LETREP-Disable.exe")
        # Stop comm thread
        # if self._comm_thread:
        #     self._read_msgs_flag = False
        #     self._comm_thread.join()
        # # Close the serial
        # if self.ser:
        #     self.ser.close()

        ###########################################################################################
        # Pipe 4
        self.send_message(self.toCpp, 4)
        ##########################################################################################
        self._read_msgs_flag = False


    def _start_threads(self):
        """
        starts threads for serial and system firing
        """
        # Create Thread(s)
        self._comm_thread = Thread(target=self._read_msgs_from_esp)

        # Start Thread(s)
        self._comm_thread.start()


def main():
    mot = motor("COM15", .53, .51)
    mot.start()
    time.sleep(3)
    mot.exit()


if __name__ == "__main__":
    main()
