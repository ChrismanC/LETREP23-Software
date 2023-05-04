from os import listdir
from os.path import isfile, join, splitext
import os
from tkinter import filedialog, messagebox
from create_json import JSONmaker
from analysis_tools import open_json_files
from peak import base_peak

#for updating peak
#opens json files
#processes peaks
folder_name = filedialog.askdirectory(title="Select Patient Folder")
if folder_name != "":
    sessions, multiple_patids = open_json_files(folder_name)
    print(sessions)
    if multiple_patids:
        messagebox.showwarning(
            "Data Loading Error!", "Loaded Blocks Contain Differeing Patient IDs")

    for sess in sessions.values():
        for blk in sess.values():
            for i, trial in enumerate(blk.trials):
                emg_dc_offset = sum(trial.emg_data[0:400])/400
                emg = [sample-emg_dc_offset for sample in trial.emg_data]
                trial.peak, trial.max_delay_ms = base_peak(
                    emg, .06)
                if trial.peak < 0:
                    print(i, trial.peak, trial.max_delay_ms)

            file_name = [ f for f in os.listdir(folder_name) if isfile(join(folder_name, f)) and splitext(join(folder_name, f))[1] == ".json" and f'Block{blk.blocknum}_{blk.date[2:]}' in f][0]
            print(file_name)

            json_dir = os.path.join(os.path.join(
                os.environ['USERPROFILE']), f'Desktop\\LETREP2\\Data\\{blk.patID}\\')
            if not os.path.exists(json_dir):
                os.makedirs(json_dir)
            with open(json_dir+file_name, "w") as file:
                JSONmaker(blk, file)
print("I exist")