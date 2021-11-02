import clr
clr.AddReference(
    "resources/DelsysAPI")
clr.AddReference("System.Collections")
from System import Int32
from System.Collections.Generic import List
from Aero import AeroPy
from collections import deque
import threading
from time import sleep


key = "MIIBKjCB4wYHKoZIzj0CATCB1wIBATAsBgcqhkjOPQEBAiEA/////wAAAAEAAAAAAAAAAAAAAAD///////////////8wWwQg/////wAAAAEAAAAAAAAAAAAAAAD///////////////wEIFrGNdiqOpPns+u9VXaYhrxlHQawzFOw9jvOPD4n0mBLAxUAxJ02CIbnBJNqZnjhE50mt4GffpAEIQNrF9Hy4SxCR/i85uVjpEDydwN9gS3rM6D0oTlF2JjClgIhAP////8AAAAA//////////+85vqtpxeehPO5ysL8YyVRAgEBA0IABKtktl6PHswln5DTRdPbDJtbDN+KTpbIjfcmBQeGmBRqq/61zfuFgaRVuOTNbPm4rDTHnbap/KzNttIofOzAOLs="
license = "<License>"\
          "<Id>9f6b5edf-19ab-45a2-aa33-acb8d5f1fbfc</Id>"\
          "<Type>Standard</Type>"\
          "<Quantity>10</Quantity>"\
          "<LicenseAttributes>"\
          "<Attribute name=\"Software\">VS2012</Attribute>"\
          "</LicenseAttributes>"\
          "<ProductFeatures>"\
          "<Feature name=\"Sales\">True</Feature>"\
          "<Feature name=\"Billing\">False</Feature>"\
          "</ProductFeatures>"\
          "<Customer>"\
          "<Name>Kotaro Sasaki</Name>"\
          "<Email>KoSasaki@letu.edu</Email>"\
          "</Customer>"\
          "<Expiration>Wed, 01 Jan 2031 05:00:00 GMT</Expiration>"\
          "<Signature>MEYCIQCo6q0QdGF6/Yx8SNk23u+XBSvAoqWTPsrLU2YZqzHT+wIhAOgzi0LuVav4wj/JH3wNXI7uMz/98/bydSm4IKtnePoV</Signature>"\
          "</License>"


class TrignoBase():
    def __init__(self):
        self.BaseInstance = AeroPy()




class emg:
    def __init__(self):
        self.array_to_store = []
        self.samples_to_collect = 0

        self._emg_collect = False
        self._cont_emg = False
        self.emg_data_collected = False
        self._start_collect = False



        base = TrignoBase()
        self.TrigBase = base.BaseInstance
        self.TrigBase.ValidateBase(key, license, "RF")

        # scan for any available sensors
        self.TrigBase.ScanSensors().Result
        self.SensorsFound = len(self.TrigBase.ListSensorNames())
        self.TrigBase.ConnectSensors()

       # start the data stream from Sensors
        newTransform = self.TrigBase.CreateTransform("raw")
        self.index = List[Int32]()

        self.TrigBase.ClearSensorList()

        for i in range(self.SensorsFound):
            selectedSensor = self.TrigBase.GetSensorObject(i)
            self.TrigBase.AddSensortoList(selectedSensor)
            self.index.Add(i)

        self.TrigBase.StreamData(self.index, newTransform, 2)

        self.threadManager()
        print("Done")

    def emg_trig_collection(self, array, sam_to_collect):
        """Starts periodic data collection of a certian number of samples collected at 1925Hz and stores into the passed array"""
        self.samples_to_collect = sam_to_collect
        self.array_to_store = array
        self._start_collect = True

    def start_cont_collect(self, array):
        """Starts emg continous data collection into the provided array"""
        self.array_to_store = array
        self._cont_emg = True

    def stop_cont_collect(self):
        """Stops EMG continous data collection"""
        self._cont_emg = False

    def _read_emg(self, temp_array):
        """This function reads the data from the emg and stores it in a passed array"""
        dataReady = self.TrigBase.CheckDataQueue()
        if dataReady:
            DataOut = self.TrigBase.PollData()
            # print(list(DataOut))
            temp_array.extend([abs(sample)
                               for sample in list(DataOut)[0][0]])

    def streaming(self):
        """This is the EMG communication thread, it chooses which array the data is stored into and how much data to store"""
        while(self._emg_collect):
            sleep(.0005)

            # Check if continous EMG collection is activated
            if self._cont_emg:
                self._read_emg(self.array_to_store)
                self.emg_data_collected = True

            # Check if triggered emg collection is started
            elif self._start_collect:

                while(len(self.array_to_store) < self.samples_to_collect):
                    sleep(.0005)
                    self._read_emg(self.array_to_store)

                self._start_collect = False
            
            # Store data from EMG
            else:
                dead_array = []
                self._read_emg(dead_array)

    def exit(self):
        """Callback to stop the data stream"""
        self.TrigBase.StopData()
        self._emg_collect = False
        self._cont_emg = False
        self._start_collect = False
        if hasattr(self, "t1"):
            self.t1.join()

    def threadManager(self):
        """Handles the threads for the DataCollector gui"""
        self._emg_collect = True

        self.t1 = threading.Thread(target=self.streaming)

        self.t1.start()


def main():
    arr = []
    emg_obj = emg()
    input()

    print("TrigCollect")
    # emg_obj.start_cont_collect()
    emg_obj.emg_trig_collect()
    input()

    emg_obj.stop()
    xs = [i for i in range(0, 5001)]

    ys = [i for i in range(0, 200)]
    ys = arr
    # n = 20
    # list1 = [sum(ys[i:i+n])/n for i in range(0,len(ys),n)]

    xs = xs[-1*len(ys):]

    # Draw x and y lists
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax.clear()
    ax.plot(xs, ys)

    # Format plot
    plt.title('EMG Readings')
    plt.ylim([0,
              3])
    plt.show()


if __name__ == "__main__":
    main()
