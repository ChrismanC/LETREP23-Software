import serial
from threading import Thread
import logging
import time
import os
import subprocess


# Constants
BAUD = 115200


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

        # Public variables for interfacing
        self.torque_update = False
        self.torque_value = 0
        self.pause_fire = True

    def enable(self):
        """
        Sends enable command to the ESP32 to enable to clearpath motor
        """
        logging.debug("UART: Enabling Motor")
        self._send_message("a")
        
        # Release motor incase it might be up
        self.release()

    def disable(self):
        """
        Sends disable command to the ESP32 to disable to clearpath motor
        """
        logging.debug("UART: Disabling Motor")
        self._send_message("d")

    def fire(self):
        # """
        # Sends fire command to the ESP32 to actuate the clearpath motor to the raised position
        # """
        # logging.debug("UART: Firing Motor")
        # self._send_message("c")
        TimeCall = time.time_ns()
        FiringOutput = subprocess.run("C:/Program Files (x86)/Teknic/ClearView/sdk/examples/3a-Example-Motion/x64/Debug/LETREP-Motion.exe", capture_output=True, text=True)
        TimeFire = FiringOutput.stdout.split()[-1]
        self.FireDelay = int(TimeFire)-int(TimeCall)
        #the EMG sample rate is 4370 samples/second
        #FireDelay is in nanoseconds, and measures the time between calling the motor and the motor firing
        #self.fire_point = self.fire_point + FireDelay*4370/(1000000000)

    # def release(self):
    #     """
    #     Sends release command to the ESP32 to return the clearpath motor to starting position
    #     """
    #     logging.debug("UART: Releasing Motor")
    #     self._send_message("b")



    # Function to send messages
    def _send_message(self,msg_to_send):

        if not self.ser.closed and msg_to_send in self._message_ack_enum.keys() :
            logging.debug(f"UART: Sending '{msg_to_send}'")
            self.ser.write(msg_to_send.encode())

                # If not received send again
            if not self._check_for_msg_received(self._message_ack_enum[msg_to_send]):

                logging.warning(f"UART: Ack for Message '{msg_to_send}' Not received, Resending")
                self.ser.write(msg_to_send.encode())
                
                if self._check_for_msg_received(self._message_ack_enum[msg_to_send]):
                    logging.error(f"UART: Ack for Message '{msg_to_send}' Not Received, Giving up")
            else:
                logging.debug(f"UART: Message '{msg_to_send}' was recevied")


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
        """
        Processes the next command and updates the torque value
        """
        while(self._read_msgs_flag):
            if self.ser.in_waiting > 0:
                try:
                    data_from_ser = self.ser.readline().decode().strip()
                    logging.debug(f"UART: Recevied '{str(data_from_ser)}'")
                except UnicodeDecodeError:
                    logging.warning("Unicode Decode Error")
                
                # UART Message Parser
                if data_from_ser[:3] == "TOR":
                    self.torque_value = float(data_from_ser.split(':')[1])
                    self.torque_update = True
                elif data_from_ser == self._expected_message:
                    self._message_received = True

            time.sleep(.01)

    def torque_preload_check(self):
        """
        Checks the motors torque:
        Returns 1 if force is greater than preload_max
        Return 0 if good
        Returens -1 if force is less than preload_min
        """
        #checks emg val instead now
        self._display_emgV = self._preload_emgV[-1] #because app doesn't like list[-1]
        if self._preload_emgV[-1] < self._preload_max:
            return 1
        elif self._preload_emgV[-1] > self._preload_min:
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
        subprocess.run("C:/Program Files (x86)/Teknic/ClearView/sdk/examples/3a-Example-Motion/x64/Debug/LETREP-Home.exe")

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
        time.sleep(4)

        subprocess.run("C:/Program Files (x86)/Teknic/ClearView/sdk/examples/3a-Example-Motion/x64/Debug/LETREP-Disable.exe")

        # Stop comm thread
        if self._comm_thread:
            self._read_msgs_flag = False
            self._comm_thread.join()

        # # Close the serial
        # if self.ser:
        #     self.ser.close()

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
