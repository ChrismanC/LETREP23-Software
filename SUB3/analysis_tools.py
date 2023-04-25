from os import listdir
from os.path import isfile, join, splitext
import json
from block import block

# Opens all json files in a directory and returns 2D list
# [[Block1,Block2,Block3],
#  [Block1,Block2,Block3]]
#
def open_json_files(directory):

    sessions = {}

    # Get only json files
    json_files = [join(directory,f) for f in listdir(directory) if isfile(
        join(directory, f)) and splitext(join(directory, f))[1] == ".json" and f != "options.json" ]

    # Open all JSON files
    for f in json_files:
        
        with open(f, "r") as json_file:
            jdict = json.load(json_file)
            blk = block().obj_from_json(jdict["block"])
            if blk.session in sessions.keys():
                sessions[blk.session][blk.blocknum] = blk
            else:
                sessions[blk.session] = {blk.blocknum: blk}
                
    #make array for patient ids
    #grab them from IDs in blocks in sessions
    #return if there are multiple
    patids = []
    for sess in sessions.values():
        for blk in sess.values():
            if blk.patID not in patids:
                patids.append(blk.patID)
    if len(patids)>1:
        return sessions, True

    return sessions, False

#makes a session CSV file from JSON
def sess_to_csv(sess, folder_name):
    for blk in sess.values():
        with open(join(folder_name,f"Block{blk.blocknum}_{blk.date}.csv"), "w") as csv_file:
            trls = list(blk.trials)
            for i, trl in enumerate(trls):
                csv_file.write(f"Trial {i} emg, Trial {i} acc,")
            csv_file.write("\n")
            max_len = max([len(data) for trl in trls for data in (trl.emg_data, trl.acc_data)])
            for i in range(max_len):
                for trl in trls:
                    if len(trl.emg_data) > i:
                        csv_file.write(str(trl.emg_data[i]))
                    csv_file.write(",")
                    if len(trl.acc_data) > i:
                        csv_file.write(str(trl.acc_data[i]))
                    csv_file.write(",")
                csv_file.write("\n")

#returns average max delay and peak from (sessions) - for use with base sessions
def avg_base_sessions(sessions):
    maxdelayms_values = []
    maxpeak_values = []
    num_of_trials = 0
    for sess in sessions.values():
        for blk in sess.values():
            print(blk.blocknum, blk.compute_avg_peak())
            for trl in blk.trials:
                num_of_trials+=1
                maxdelayms_values.append(trl.max_delay_ms)
                maxpeak_values.append(trl.peak)



    return sum(maxdelayms_values)/num_of_trials, sum(maxpeak_values)/ num_of_trials

