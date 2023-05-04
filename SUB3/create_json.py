from datetime import datetime
import os
import random
from block import block
from trial import trial
import json

#makes JSON files

#trials:
def JSONTrialMaker(trialobject: trial, file):
    jdict = {
        "trial":
                {"speed": trialobject.speed,
                "measured_speed": trialobject.foot_speed,
                "success": trialobject.success,
                "failure-reason": trialobject.failure_reason,
                "peakvalue": trialobject.peak,
                "maxdelayms": trialobject.max_delay_ms,
                "emgoffset": trialobject.emg_offset,
                "emgdata": trialobject.emg_data,
                 "accdata": trialobject.acc_data
                }
            
    }

    json.dump(jdict, file, indent=4)

#block:
def JSONmaker(blockobject: block, file):
    jdict = {
                "block":{
                    "info":{
                        "patID": blockobject.patID,
                        "date": blockobject.date,
                        "session": blockobject.session,
                        "blocknum": blockobject.blocknum
                    },
                    "results":{
                        "avgsuccess": blockobject.compute_avg_success(),
                        "numoftrials": blockobject.number_of_trials()
                    },
                    "trials":{}
                }
            }

    i = 0
    for t in blockobject.trials:
        t: trial
        i += 1

        jdict["block"]["trials"].update({f"trial{i}":
                                            {"speed": t.speed,
                                            "measured_speed": t.foot_speed,
                                            "success": t.success,
                                            "failure-reason": t.failure_reason,
                                            "peakvalue": t.peak,
                                            "maxdelayms": t.max_delay_ms,
                                            "emgoffset": t.emg_offset,
                                            "emgdata": t.emg_data,
                                            "accdata": t.acc_data
                                            }
                                        })

    json.dump(jdict, file, indent=4)

#this one is for max collections
def maxJSON(blockobject: block, file):
    jdict = {
                "block":{
                    "info":{
                        "patID": blockobject.patID,
                        "date": blockobject.date,
                        "session": blockobject.session,
                        "blocknum": "Max"
                    },
                    "results":{
                        "MaxTrq": blockobject.avg_max_trq,
                        "TrqNM": blockobject.avg_max_trq*(.325),
                        "MaxEMG" : blockobject.avg_max_emg,
                        "numoftrials": blockobject.number_of_trials()
                    }
                }
            }
    json.dump(jdict, file, indent=4)

#for testing:
def main():
    blockobject = block()
    import random
    for _ in range(5):
        t = trial()
        t.acc_data = [random.random() for __ in range(30 + random.randint(0, 5))]
        t.emg_data = [random.random() for __ in range(30 + random.randint(0, 5))]
        blockobject.trials.append(t)
    print(blockobject.date)
    with open("myfile.json", "w") as file:
        JSONmaker(blockobject, file)


if __name__ == "__main__":
    main()
