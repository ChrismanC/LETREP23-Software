
from scipy import signal
freq=19250
#was 1925 from jesse
#from specs, 4370 sa/sec from emg
#but cassie says 19250
# bc yes
#but not everywhere...
#the accelerometer is 963 sa/sec

def base_peak(emg,factor):

    # maxes = list(signal.find_peaks(emg[500:], height=find_peak_min_thresh(emg, factor))[0])
    # print("max: ", maxes)
    # print("emg: ", emg)
    if (len(emg)>1):
        #if the data exists, find the highest point
        real_max = max(emg)
    # print("new max:", real_max)
        #get that point's location
        peak = emg.index(real_max)
    # peak = peak + 500
        #average a bunch of points around the peak
        sum = 0
        print(peak)
        print(len(emg))
        if(len(emg)>=peak+100):
            for i in range((peak-10),(peak+10)):
                sum=sum+emg[i]
            avg_peak=sum/20
        else:
            for i in range((peak-100),(peak)):
                sum=sum+emg[i]
            avg_peak=sum/20            
        peak_ms = (peak)/freq * 1000
    # if maxes:
    #     peak=maxes[0]
    #     peak += 500
    #     sum=0
    #     for i in range((peak-100),(peak+100)):
    #         sum=sum+emg[i]
    #     avg_peak=sum/20
    #     peak_ms = (peak-500)/freq * 1000
    else:
        avg_peak=0
        peak_ms=0
    return(avg_peak, peak_ms)



def condition_peak(emg, avg_time,factor):

    print(avg_time)
    M1_avg=int((avg_time*freq/1000)+500)
    print(M1_avg)
    range_emg=emg[M1_avg-200:M1_avg+200]
    # for x in range_emg:
    #     print(range_emg[int(x)]*1000)
    print(".............................................................................................")
    # maxes = list(signal.find_peaks(emg[1200:1600], height=find_peak_min_thresh(emg,factor))[0])
    maxes = list(signal.find_peaks(emg[1300:1500], height=find_peak_min_thresh(emg,factor))[0])
    # if maxes[0]:
    #     for i in maxes:
    #         print(maxes[i])
    # else:
    #     print("fail")
    if maxes:
        peak=maxes[0]
        print(maxes[0])
        # peak=peak+M1_avg-20
        peak=int(peak)+1300
        sum=0
        for i in range((peak-100),(peak+100)):
            sum=sum+emg[i]
        avg_peak=sum/20
        peak_ms = (peak-500)/freq * 1000
    else:
        return 0,0

    return(avg_peak, peak_ms)


def find_peak_min_thresh(emg,factor):
    
    num = 5
    peaks = []
    peaks_pos = list(signal.find_peaks(emg[0:400], height=0)[0])
    for x_pos in peaks_pos:
        peaks.append(emg[x_pos])
    peaks = sorted(peaks, reverse=True)

    return sum(peaks[:num])/num * factor

