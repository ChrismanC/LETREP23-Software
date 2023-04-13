from datetime import date
from trial import trial

#Block.py handles data from framework and processes it into a file; particularly, a JSON file.
#note that the max.py files handle blocks weirdly;
#since they are not the complete data collection on their own, they pass data to their app.py
#this means they call r_block instead of stop_block, which is a little different in processing
class block():
    def __init__(self, patID=1234, date=str(date.today()), sess=1, blocknum=0):
        #basic patient/session data
        self.patID = patID
        self.date = date
        self.session = sess
        self.blocknum = blocknum
        self.trials = list()
        self.avg_max_trq = 0
        self.avg_max_emg = 7
    
    def obj_from_json(self, json):
        self.patID = json['info']['patID']
        self.date = json['info']['date']
        self.session = json['info']['session']
        self.blocknum = json['info']['blocknum']
        self.avg_success = json['results']['avgsuccess']
        self.trials = [trial().obj_from_json(t)
                       for t in list(json['trials'].values())] #process all trials

        return self

    def compute_avg_success(self):
        if self.trials:
            return sum([trl.success for trl in self.trials]) / len(self.trials)

    def compute_avg_peak(self):
        if self.trials:
            sum_of_peaks = []
            for trl in self.trials:
                if trl.peak:
                    sum_of_peaks.append(trl.peak)
            if sum_of_peaks:
                return sum(sum_of_peaks) / len(sum_of_peaks)
        return 0

    def number_of_trials(self):
        return len(self.trials)

    def copy_block(self):
        return block(self.patID, self.date, self.session, self.blocknum + 1)

