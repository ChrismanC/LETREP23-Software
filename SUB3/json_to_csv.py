import csv
import json

#makes json into csv
#pretty... simple

def json_to_csv(json_file, csv_file):
    jdict = json.load(json_file)

    trials = jdict["block"]["trials"]
    trials = list(trials.values())

    for i, trial in enumerate(trials):
        csv_file.write(f"Trial {i} emg, Trial {i} acc,")
    csv_file.write("\n")
    max_len = max([len(data) for trial in trials for data in (trial["emgdata"], trial["accdata"])])

    for i in range(max_len):
        for trial in trials:
            if len(trial["emgdata"]) > i:
                csv_file.write(str(trial["emgdata"][i]))
            csv_file.write(",")
            if len(trial["accdata"]) > i:
                csv_file.write(str(trial["accdata"][i]))
            csv_file.write(",")
        csv_file.write("\n")

def main():
    with open("myfile.json", "r") as json_file:
        with open("myfile.csv", "w") as csv_file:
            json_to_csv(json_file, csv_file)

if __name__ == "__main__":
    main()