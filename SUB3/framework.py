
from concurrent.futures import process
from datetime import datetime
import logging
import os
import threading
from time import sleep, time
from random import random, randrange
from tkinter import messagebox

from block import block
from trial import trial
from motor import motor
from emg import emg
from create_json import JSONmaker, maxJSON
import scipy as sp
from scipy import signal
import peak

#framework does most of the heavy lifting for calculations. It does not display to the user; app does that.

class framework():
    def __init__(self, COM, patID=1234, sess=1, blocknum=-1, premin=-.06, premax=.04, no_motor = False, no_emg = False):
        self.preload_max = premax
        self.preload_min = premin

        self.block = block(patID, sess=sess, blocknum=blocknum)

        #print("check motor")
        if not no_motor:
            if not 'self.mot' in globals():
                self.mot = motor(COM, self.preload_max, self.preload_min)
                self.mot.start()
                # Give motor time to enable
                sleep(10)
                logging.info("Done Enabling motor")
            else:
                print("")
        else:
            self.mot = None
        #print("check EMG")
        if not no_emg:
            self.emg = emg()
        else:
            self.emg = None
        #print("all good")
        
        # This bit stops the block
        self.running = False

        # This bit pauses the block
        self.paused = True

        # THis bit indicates trial ending
        self.finished_trial = False

        # This bit indicates trial starting
        self.starting_trial = False

        # Counts blocks and trials
        self.block_count = 1
        self.trial_count = -1
        #this variable carries the fire point to the truncating code
        self.fire_point = 0
        print("init done")

    def exit(self):
        self.running = False
        if self.mot:
            self.mot.exit()
        else:
            logging.warn("No Motor, Exiting")
        if self.emg:
            self.emg.exit()
        else:
            logging.warn("No EMG, Exiting")

    def fire(self, failure, trial_start_time, speed):
        #logged to the 'run' log files, as far as I can tell.
        logging.info("FIRE! "+str( time()-trial_start_time)+ "  Failure:"+str( failure))
        self.mot.fire(speed)
        # sleep(1.5)

        # self.mot.release()

    def preload_failure_handler(self, trial_start_time):
        """
        Checks for the patient to regain preloading. If they fail to do so by a certain time, they fail

        returns: Bool, true = Fire, false = Continue with other task
        """
        logging.info("Preload failure")
        good_start_time = time()
        while(1):
            sleep(.01)
            if time()-good_start_time >= 1:
                logging.info("Failure Recovery")
                return False

            if time()-trial_start_time >= 5:
                return True

             # Check if out of torque (now EMG) limits
            
            if self.mot.torque_preload_check() != 0:

                # Check if out of time for Failure Handler
                if time()-trial_start_time > 4:

                    self.current_trial.success = False

                    #what kind of preload fail?
                    if self.mot.torque_preload_check() < 0:
                        self.current_trial.failure_reason = "prelow"
                    else:
                        self.current_trial.failure_reason = "prehigh"
                    return True
                else:
                    #or when was the success?
                    good_start_time = time()

    def preload_randomizer(self, trial_start_time):
        random_fire_time = time() + (5+trial_start_time-time()) * random()
        logging.info("Random Fire Time:"+ str( random_fire_time-time()))
        while(1):
            sleep(.1)
            # Check if preload amount is good
            if time()-random_fire_time > 0:
                return False

            # Check if out of torque (EMG) limits
            if self.mot.torque_preload_check() != 0:
                # Check if out of time for Failure Handler
                if time()-trial_start_time > 4:

                    self.current_trial.success = False

                    if self.mot.torque_preload_check() < 0:
                        self.current_trial.failure_reason = "prelow"
                    else:
                        self.current_trial.failure_reason = "prehigh"

                # Call failure handler
                else:
                    if self.preload_failure_handler(trial_start_time):
                        return True
                    else:
                        return self.preload_randomizer(trial_start_time)

    def retake_trial(self):
        #remove the block being retaken from the count; pause
        self.block.trials.pop(-1)
        self.trial_count -= 1
        self.pause_block()

    #this fn does preload and trials proper, with failure handling:
    def take_trial(self, speed):
        if self.paused:
           sleep(1) 
        else:
            # Update Trial Count
            self.trial_count += 1
            self.starting_trial = True

            if not self.mot or not self.emg:
                #if no motor/EMG, run fake values for test purposes
                logging.info("Missing EMG or Motor, Doing Fake Trial")
                self.current_trial = trial()
                trial_start_time = time()
                self.current_trial.speed=speed
                self.current_trial.foot_speed = speed
                sleep(.5)
                self.finished_trial = True
                self.block.trials.append(self.current_trial)
                while(time()-trial_start_time < 1):
                    sleep(.1)
                return

            if self.block:
                logging.info("Starting Trial: "+ str(self.trial_count))
                
                self.current_trial = trial()
                trial_start_time = time()
                trial_data = [[],[]] #this array of 2 arrays receives [EMG, Accelerometer] data
            
                #begin continuous collection of EMG + accel
                #emg.py constantly collects from this point on, appending to the arrays in trial_data
                self.emg.start_cont_collect(trial_data)
                # Trial starts, debounce half a second
                sleep(1.25)
                #Send the motor the emg array
                self.mot.update_pre_emg(trial_data[0]) 

                # Preload while checking torque for 1.25 seconds past start time
                failure_status = False
                while(1):
                    sleep(.1)
                    if time()-trial_start_time > 1.25:
        
                        break

                    if self.mot.torque_preload_check() != 0:     
                        #if preload check is not good
                        #handle failure:
                        failure_status = self.preload_failure_handler(trial_start_time)
                        break

                # Randomizer
                if not failure_status:
                    failure_status = self.preload_randomizer(trial_start_time)

                if not self.paused:
                    #if failure is true, success is false
                    self.current_trial.success = not failure_status
                    #we are firing at the current point
                    self.fire_point = len(trial_data[0]) -1
                    self.fire(failure_status, trial_start_time, speed)
                    self.current_trial.speed=speed
                    self.current_trial.foot_speed = self.mot.FootSpeed
                    #the EMG sample rate is 4370 samples/second
                    #FireDelay is in nanoseconds, and measures the time between calling the motor and the motor firing
                    #so the adjusted true fire point is:
                    self.fire_point = self.fire_point + int(self.mot.FireDelay*4370/(1000000000))
                    
                    #fire point = the current data point at time of firing
                    #note that self.fire logs to a 'run' log file the time that correlates with this
                else:
                    #if paused, don't collect data
                    self.emg.stop_cont_collect()

                    # Decrementing trial_count due to not completing trial
                    self.trial_count-=1
                    return

                sleep(.8)
                self.emg.stop_cont_collect()
            
                # Save data to trial
                self.current_trial.emg_data = trial_data[0]
                self.current_trial.acc_data = trial_data[1]
                self.current_trial.emg_offset = sum(self.current_trial.emg_data[0:400])/400
                #Average of the starting neutral 400 data points to determine the EMG 'dc offset' ^^^

                # Process the data
                self.truncate_data()

                self.block.trials.append(self.current_trial)
                print(f"Number of trials in block is {len(self.block.trials)}")
                logging.info(f"Number of trials in block is {len(self.block.trials)}")

                # Notify trial finished
                self.finished_trial = True

                while(time()-trial_start_time < 10 or self.finished_trial):
                    sleep(.1)

    # Update for a change in options
    def update_options(self, options):
        self.premin = options["pre_min"]
        self.premax = options["pre_max"]
        if self.mot:
            self.mot.update_preloads(self.premin, self.premax)
        if options["pat_id"] != self.block.patID or options["block_count"] != self.block_count:
            self.block = block(patID=options["pat_id"], date=self.block.date, 
                sess=options["sess"], blocknum=options["block_count"])
        else:
            self.block.session = options["sess"]
            
    # Processes emg data by trunkating and smoothing
    def truncate_data(self):

        #Average acc data
        """
        acc_avg = sum(self.current_trial.acc_data[0:500])/500
        
        for i, smpl in enumerate(self.current_trial.acc_data):
            if len(self.current_trial.acc_data) - 801 > i > 1001 and abs(smpl - acc_avg) > .3:
                fire_point = i 
                logging.info("Fire point found at sample number %d" % i)
                break
        
        else:
            logging.warning("Trial has no change in Acc Data. Using middle")
            fire_point = len(self.current_trial.acc_data)/2
            return
        """
        #we set the fire point when fire() runs instead of the above code!
        fire_point = self.fire_point
        print("Fire point: ", fire_point)
        # #Truncate data
        self.current_trial.acc_data = self.current_trial.acc_data[fire_point -
                                                                    500:fire_point+1600]
        self.current_trial.emg_data = self.current_trial.emg_data[fire_point -
                                                                    500:fire_point+1600]


    def new_block(self):
        sleep(5)
        self.block_count+=1
        self.trial_count = -1
        self.block = self.block.copy_block()

    def pause_block(self):
        self.paused = not self.paused
        
    def stop_block(self):
        self.running = False
        self.paused = True
        b = self.block
        logging.info(f"Number of trials in block is {len(b.trials)}")
        json_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), f'Desktop\\LETREP23\\Data\\{b.patID}\\')
        # json_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), f'Downloads\\LETREP2\\Data\\{b.patID}\\')
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        with open(json_dir+f'Session{b.session}_Block{b.blocknum}_{b.date[2:]}_{datetime.now().strftime("%H-%M-%S")}.json', "w") as file: 
            JSONmaker(self.block, file)
        messagebox.showinfo("Block Saved","Block saved to: "
                 + json_dir+f'Session{b.session}_Block{b.blocknum}_{b.date[2:]}_{datetime.now().strftime("%H-%M-%S")}.json')
        self.new_block()

    def r_block(self):
        self.running = False
        self.paused = True
        b = self.block
        logging.info(f"Number of trials in block is {len(b.trials)}")
        json_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), f'Desktop\\LETREP23\\Data\\{b.patID}\\')
        # json_dir = os.path.join(os.path.join(os.environ['USERPROFILE']), f'Downloads\\LETREP2\\Data\\{b.patID}\\')
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)
        with open(json_dir+f'R1_Max_{b.date[2:]}_{datetime.now().strftime("%H-%M-%S")}.json', "w") as file: 
            maxJSON(self.block, file)
        messagebox.showinfo("Block Saved","Block saved to: "
                 + json_dir+f'R1_Max_{b.date[2:]}_{datetime.now().strftime("%H-%M-%S")}.json')
        self.block_count+=1
        self.trial_count = -1
        sleep(5)
        self.block = block(self.block.patID, sess=self.block.session, blocknum=self.block_count)
                 
    def r_start(self):
        if self.running == False:
            self.running = True
            self.paused = False
            self.trial_thread = threading.Thread(
                target=self._r_thread)
            self.trial_thread.start()

    def _r_thread(self):
        emg_max=0
        torque_max=0
        while(self.running):
            if self.paused:
                sleep(1) 
            else:
                self.trial_count += 1
                self.starting_trial = True

                if not self.mot or not self.emg:
                    logging.info("Missing EMG or Motor, Doing Fake Baseline")
                    self.current_trial = trial()
                    trial_start_time = time()
                    emg_max = 1
                    torque_max = 2
                    self.block.avg_max_trq = torque_max
                    self.block.avg_max_emg = emg_max
                    sleep(3)
                    #-update box color to blue for complete, then skip to next loop
                    # baseline_display.set_record(baselineCount -1, 5)
                    self.finished_trial = True
                    self.block.trials.append(self.current_trial)
                    while(time()-trial_start_time < 10):
                        sleep(.1)
                    # root.update()
                    continue
                    
                # root.update()
                #fresh arrays every loop!

                self.current_trial = trial()
                trial_start_time = time()

                emg_data = [[],[]]
                baseTorque = []

                # Tell them to press
                # general_info_lbl.configure(text="Collect Max")

                #start collecting data from EMG
                self.emg.start_cont_collect(emg_data)
                # Trial starts, debounce half a second
                # sleep(.75)
                #collect torque data to 100 datapoints; EMG will collect in background simultaneously
                while(len(baseTorque) < 100):
                    self.mot._read_msgs_from_esp()
                    if self.mot.torque_update:
                        if(self.mot.torque_value<0):
                            self.mot.torque_value=self.mot.torque_value*-1
                        baseTorque.append(self.mot.torque_value)
                        # print(self.mot.torque_value)
                        self.mot.torque_update = False
                
                # emg_max=0
                # torque_max=0
                #-grab highest data points for this round;
                # *************************************************************
                # print(len(emg_data[1]))
                # print(len(baseTorque))
                # emg_max_point = emg_data[0].index(max(emg_data[0]))
                # emg_bucket = 0
                # for i in range((emg_max_point -20), (emg_max_point)):
                #     emg_bucket = emg_bucket + emg_data[0][i]
                # emg_average = emg_bucket/21
                
                # emg_max = ((emg_max)*(self.trial_count) + emg_average)/(self.trial_count+1) 
                # ***********************************************************************
                trq_index = baseTorque.index(max(baseTorque))
                emg_index  = int((trq_index/99)*(len(emg_data[1])))
                if(emg_index<100):
                    emg_range = emg_data[0][:emg_index]
                else:
                    emg_range = emg_data[0][emg_index-100:emg_index]
                emg_average=max(emg_range)
                print(max(emg_data[0]))
                print(emg_average)
                
                emg_max = ((emg_max)*(self.trial_count) + emg_average)/(self.trial_count+1)
                print(emg_max)
                torque_max = ((torque_max)*(self.trial_count) + max(baseTorque))/(self.trial_count+1)
                #^undoes previous loop average; adds maximum value in new emg array; re-performs average
                self.block.avg_max_trq = torque_max
                self.block.avg_max_emg = emg_max
                sleep(5)

                self.finished_trial = True
                self.block.trials.append(self.current_trial)

    def start_block(self, speed_arr):
        if self.running == False:
            self.running = True
            self.paused = False
            self.trial_thread = threading.Thread(
                target=self._data_collection_thread, args=[speed_arr])
            self.trial_thread.start()

    def _data_collection_thread(self, speed_arr):
        while(self.running):
            i=randrange(len(speed_arr))
            while(speed_arr[i][1]==0):
                i=(i+51)%(len(speed_arr))
                print("SpeedCom: ", i)
            speed=speed_arr[i][0]
            print("SpeedComActual: ", speed)
            speed_arr[i][1]=(speed_arr[i][1]-1)
            self.take_trial(speed)
