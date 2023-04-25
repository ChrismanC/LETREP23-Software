
import itertools
from os import stat
from time import sleep
from tkinter.scrolledtext import ScrolledText
from tkinter import *
from tkinter import filedialog, messagebox
from global_funcs import *

import statistics

from PIL import ImageTk, Image
from analysis_tools import *

from object_browser import Browser

#analysis
#calculates the coefficient of variation
#todo

folder_name = filedialog.askdirectory(title="Select Patient Folder")
if folder_name != "":
    
    sessions, multiple_patids = open_json_files(folder_name)
    
    if multiple_patids:
        messagebox.showwarning(
            "Data Loading Error!", "Loaded Blocks Contain Differeing Patient IDs")

    # The data pattern, [peak,max_delay_ms,succcess,pre_avg]
    total_trls = [[],[],[],[]]

    trials_output = [[""]]
    trials_output[0].extend([f"Trial {x}" for x in range(1,81)])

    session_output = [["Session"], ["Peak"], ["ms Delay"], ["Success"], ["Preload Avg"],["Preload StDev"]]
    block_output = [[["","Block 1 Peaks", "ms Delay", "Success", "Preload Avg", "Preload StDev"]], 
        [["","Block 2 Peaks", "ms Delay", "Success", "Preload Avg", "Preload StDev"]], 
        [["","Block 3 Peaks", "ms Delay", "Success", "Preload Avg", "Preload StDev"]], 
        [["","Block 4 Peaks", "ms Delay", "Success", "Preload Avg", "Preload StDev"]]]
    trial_header_output = []

    for sess in sessions.values():
        # The data pattern, [peak,max_delay_ms,succcess,pre_avg]
        sess_data = [[], [], [], []]
        for blk in sess.values():
            i = len(trials_output)

            trials_output.extend([["Peak"],["ms Delay"],["Success"],["Preload AVG"],["Preload StDev"],[""]])

            # The data pattern, [peak,max_delay_ms,succcess,pre_avg]
            block_data = [[],[],[],[]]
            for trl in blk.trials:

                trl.pre_avg = statistics.mean(trl.emg_data[0:400])
                
                trials_output[i].append(trl.peak)
                trials_output[i+1].append(trl.max_delay_ms)
                trials_output[i+2].append(trl.success)
                trials_output[i+3].append(trl.pre_avg)
                trials_output[i+4].append(statistics.stdev(trl.emg_data[0:400]))
                trials_output[i+5].append("")

                # Storing trial data for block
                block_data[0].append(trl.peak)
                block_data[1].append(trl.max_delay_ms)
                block_data[2].append(trl.success)
                block_data[3].append(trl.pre_avg)


            # Copy data to session
            for num, row in enumerate(sess_data):
                row.extend(block_data[num])
            
            block_output[blk.blocknum-1].append(["",statistics.mean(block_data[0]),
                                               statistics.mean(block_data[1]),
                                               statistics.mean(block_data[2]),
                                               statistics.mean(block_data[3]),
                                               statistics.stdev(block_data[3])])
       

        for num, blk in sess.items():
            if num == 1:
                session_output[0].append(blk.session)
                session_output[1].append(statistics.mean(sess_data[0]))
                session_output[2].append(statistics.mean(sess_data[1]))
                session_output[3].append(statistics.mean(sess_data[2]))
                session_output[4].append(statistics.mean(sess_data[3]))
                session_output[5].append(statistics.stdev(sess_data[3]))
            trial_header_output.extend(["Session", blk.session, "Block", blk.blocknum, "", ""])
            
        # Copy data to total    
        for i, row in enumerate(total_trls):
            row.extend(sess_data[i])    

    # Transpose some arrays
    session_output = list(
        map(list, itertools.zip_longest(*session_output, fillvalue='"')))

    trials_output = list(
        map(list, itertools.zip_longest(*trials_output, fillvalue='"')))

    
    
    for i in range(3):
        block_output[3].insert(i+1,["","","","","",""])
    
    for index,row in enumerate(session_output):
        for i in range(4):
            try:
                if block_output[i][index]:
                    row.extend(block_output[i][index])
            except:
                row.extend(["", "", "", "", "", ""])

    # Create header
    header_output = [[list(list(sessions.values())[0].values())[0].patID]]
    header_output.append(["Success Rate Avg", statistics.mean(total_trls[2])])
    header_output.append(["M1 avg height", statistics.mean(total_trls[0])])
    header_output.append(["ms Max Delay", statistics.mean(total_trls[1])])
    header_output.append(["Preload Avg", statistics.mean(total_trls[3])])
    header_output.append(["Preload StDev", statistics.stdev(total_trls[3])])
    
    
    with open(join(folder_name, f"{list(list(sessions.values())[0].values())[0].patID}.csv"), "w") as csv:

        for i in header_output:
            for j in i:
                csv.write(f"{j},")
            csv.write("\n")
        csv.write("\n")

        

        for i in session_output:
            for j in i:
                csv.write(f"{j},")
            csv.write("\n")
        csv.write("\n")
        csv.write("\n")

        csv.write(",")
        for j in trial_header_output:
            csv.write(f"{j},")
        csv.write("\n\n")
        

        for i in trials_output:
            for j in i:
                if j != '"':
                        csv.write(f"{j},")
                else:
                    csv.write(",")
            csv.write("\n")
