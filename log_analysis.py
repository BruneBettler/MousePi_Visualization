from data_loader import *
from utils import *

'''
Function prints information about the gap times between licks from a lick array 
and creates a histogram for easy visualisation  
'''
def all_gap_info(lick_array, decimals, file_title):
    gap_array = []
    for trial in lick_array:
        if len(trial) > 10: # so we can see clusters
            prev_lick = None
            for curr_lick in trial:
                if prev_lick is None:
                    prev_lick = curr_lick
                else:
                    gap_array.append(curr_lick - prev_lick)
                    prev_lick = curr_lick

    all_gaps = np.array(gap_array)

    # clean "uniqueness" (0.002999999 == 0.00300000)
    rounded = np.around(all_gaps, decimals=decimals)

    unique_gaps, counts = np.unique(rounded, return_counts=True)

    if unique_gaps[0] == 0.0:
        gap_num = len(all_gaps) - counts[0]
        unique_gaps = unique_gaps[1:]
        counts = counts[1:]
    else: gap_num = len(all_gaps)

    print(f'\nGap info for "{file_title}"\nTotal gap count: {gap_num} ')

    for gap, count in zip(unique_gaps, counts):
        print(f"Gap Length (s): {gap}, Count: {count}")

    # Plotting the histogram
    fig = plt.figure(figsize=(10, 6))
    plt.bar(unique_gaps, counts, width=0.001, edgecolor='black')
    plt.xlabel("Gap lengths between licks")
    plt.title(f'Gap Lengths Between Licks \n{file_title}')
    plt.ylabel('Count (log)')
    plt.yscale('log')
    plt.grid(True)
    plt.show()

    return unique_gaps, counts


'''
Function returns the average time in seconds between the open valve and next lick  
'''
def avg_valveLick(single_day_data):
    post_valve_lick_times = []
    valve_open = False

    for n, line in enumerate(single_day_data):  # iterate through all trials

        split_data = line.split(',')

        if split_data[2][:5] == '01000':  # indicates an open valve
            valve_open_time = split_data[1]
            valve_open = True
        elif valve_open and split_data[2][:5] == '11010':  # indicates a lick occuring after an open valve
            time = time_dif(valve_open_time, split_data[1]) # time in seconds
            post_valve_lick_times.append(time)
            valve_open = False

    post_valve_lick_times = np.array(post_valve_lick_times)
    mean = np.mean(post_valve_lick_times)
    return mean


"""
    Check if after a lick during the pre-trial period,there is a 2 second delay before the sample period starts
        * end off ITT followed on next line by end of trial then shortly after a trial start
        * after a trial start, check the last "01110" lick occured during trial start
        * sample period == cue starts (11001: start of display screen)
"""
def bad_lick_bout_analysis(log_by_trial_array):
    all_gap_times = []
    prev_bLick = [None, None]

    for n, trial in enumerate(log_by_trial_array):
        # determine if trial
        #       1.) has 01110 codes in it (lick during wait time) (False)
        #       2.) has 11001 code meaning its a "true trial"     (True)

        for m, event in enumerate(trial[1]):
            # check if trial has any 01110 licks in it
            # if so, record the last one
            if '01110' in event:
                prev_bLick = [n, event]

            elif '11001' in event:
                current_sample_period_time = event.split(',')[1] # as a string

                if prev_bLick[0] == n-1: # (previous trial had bad licks)
                    prev_bad_lick_time = prev_bLick[1].split(',')[1]
                    # find time difference
                    time_diff = time_dif(prev_bad_lick_time, current_sample_period_time)  # seconds
                    all_gap_times.append(time_diff)

    '''
    ANALYZING THE GAP BETWEEN LICKS DURING PRE-TRIAL TIME AND NEXT TRIAL SAMPLE START 
    '''
    plt.hist(all_gap_times, 15)
    plt.title('Gap between previous trial 01110 and current trial 11001\n POPPY 05-26')
    plt.xlabel('Gap duration in seconds')
    plt.ylabel('Occurrence')
    plt.show()

    return np.array(all_gap_times)


'''
Function graphs a sort of summary information image for a single mouse for a single session
all licks for all trials and sorts them into the different colors
 Blue = 
 Green = 
'''
def graph_singleMouse_Lick_summary(log_data_by_trial):
    # basic info: total trial #, go trial # (# of hit in there) nogo trial # (and number of withold trials): number of successes over time
    # trial info to get 1.) if it's a failed start, or true trial: go, or nogo and then of these, failed or passed 2.) trial start time

    return 0



if __name__ == '__main__':
    data = single_day_data(path='/Volumes/MATT_0/MousePi Data/Phase_1 Log Files/05-26/POPPY_SP2_05_26_2024_16_44_50.log')
    #lick_array, trial_times, lick_window_times = get_go_lick_times_per_trial(data)

    log_by_trial = get_log_by_trial(data)
    bad_lick_bout_analysis(log_by_trial)