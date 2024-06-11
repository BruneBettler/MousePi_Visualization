import os
from scipy.stats import linregress
import matplotlib
matplotlib.use('TkAgg')  # Set the backend to Agg for non-interactive plotting
import matplotlib.pyplot as plt
from utils import *

'''
Function separates log file data into a list of per-trial arrays 
trial array = [line_of_trial_start_in_OG_log (starts with n=0), log_lines_in_trial (from 01010 trial start to 10101 trial end)
'''
def get_log_by_trial(log_file_data):
    log_by_trial = []
    trial_array = [None, None]
    start_stop = [None, None]  # used for debugging / to have access to the start and stop lines in the OG log file
    curr_trial_data = []
    record = False

    for n, line in enumerate(log_file_data):  # iterate through all lines
        split_data = line.split(',')

        if split_data[2][:5] == '01010':  # indicates a trial start
            start_stop[0] = n
            record = True

        if record:
            curr_trial_data.append(line)

        if split_data[2][:5] == '10101':  # indicates a trial end
            record = False
            start_stop[1] = n
            trial_array[0] = start_stop
            trial_array[1] = curr_trial_data
            log_by_trial.append(trial_array)
            curr_trial_data = []
            trial_array = [None, None]
            start_stop = [None, None]

    return log_by_trial

'''
Function returns all contents of a single log file given either 
a mouse_info array (format [phase,date,mouse], ex: [1, '02-12', 'FANNY'] or path (ex. 'path/to/data.log')
'''
def single_day_data(mouse_info=None, path=None):
    if path is None: # mouse info is provided
        phase = mouse_info[0]
        date = mouse_info[1]
        mouse = mouse_info[2]
        path = f"Data/Phase {str(phase)}/{str(date)}"

        for _, _, files in os.walk(path):
            for file_name in files:
                if file_name[-4:] == '.log' and file_name[:len(mouse)] == mouse:
                    file = open(path + '/' + file_name)
                    data = file.readlines()
                    file.close()
                    return data
    else: # path is provided
        file = open(path)
        data = file.readlines()
        file.close()
        return data

'''
Function returns all contents of all log files from a given phase for a SINGLE MOUSE given either 
a mouse_info array (format [phase, mouse] ex: [1, 'ODELIA']) 
or [mouse,path] array (ex: ['ODELIA', 'path/to/phase_folder'])
'''
def multi_day_data(mouse_info=None, path_array=None):
    multi_day_data = []
    session_dates = []

    if path_array is None: # mouse_info provided
        phase = mouse_info[0]
        mouse = mouse_info[1]
        home = f"Data/Phase {str(phase)}/"

    else: # path is given
        mouse = path_array[0]
        home = path_array[1]
        if home[-1] != '/':
            home = home + '/'

    for root, dirs, files in os.walk(home):
        dirs.sort()
        for session in dirs:
            path = home + session
            for _, _, files in os.walk(path):
                for file_name in files:
                    if file_name[-4:] == '.log' and file_name[:len(mouse)] == mouse:
                        file = open(path + '/' + file_name)
                        data = file.readlines()
                        multi_day_data.append(data)
                        file.close()
                        session_dates.append(session)
                        break

    return multi_day_data, session_dates


'''
Function returns MultiD array containing an array for each mouse 
with data_file info from each session as a new list
input mouse_name_array and either phase (ex: 1) or a string path to the phase folder
'''
def get_multiDay_mice_data(mouse_name_array, phase=None, path=None):
    mice_data_array = []

    if path is None:  # phase is given
        for mouse in mouse_name_array:
            multiD_data, mouse_sessions = multi_day_data(mouse_info=[phase, mouse])
            mice_data_array.append([multiD_data, mouse_sessions])
    else:  # path is given
        for mouse in mouse_name_array:
            multiD_data, mouse_sessions = multi_day_data(path_array=[mouse, path])
            mice_data_array.append([multiD_data, mouse_sessions])

    return mice_data_array

"""
Function takes data from a single log file and returns a list of trials 
each containing a list of all lick times during that trial 
all times are in seconds 
"""
# sample period = start of true trial
def get_lick_times_per_true_trial(file_data):
    total_licks = []
    trial_licks = []
    true_trial_times = []
    tt_start = 0

    sampling = False
    for n, line in enumerate(file_data):   # iterate through all trials

        split_data = line.split(',')

        if split_data[2][:5] == '11001': # indicates start of sample period
            sampling = True
            tt_start = split_data[1]

        elif sampling and split_data[2][:5] == '11010': # mouse lick
            time = time_dif(tt_start, split_data[1])
            trial_licks.append(np.array(time))

        elif sampling and split_data[2][:5] == '11101': # indicates end of lick window
            sampling = False
            true_trial_times.append((tt_start,split_data[1])) # adds the start and end times of the tracked licking period
            if len(trial_licks) != 0: total_licks.append(trial_licks)
            trial_licks = []

    return total_licks, true_trial_times


"""
Function takes data from a single log file and returns a list of go trials in which a go lick occured
each containing a list of all lick times during that trial (from start of sampling window through the trial end code (includes the ITT))
all times are in seconds 
"""
# sample period = start of true trial
def get_go_lick_times_per_trial(file_data):
    total_licks = []
    trial_licks = []
    true_trial_times = []
    lick_window_times = []
    tt_start = 0
    record = False
    sampling = False

    for n, line in enumerate(file_data):   # iterate through all trials

        split_data = line.split(',')

        if split_data[2][:5] == '11001': # indicates start of sample period
            sampling = True
            tt_start = split_data[1]
            trial_licks = []
            lick_window_start = None
            lick_window_end = None
            continue

        elif sampling and split_data[2][:5] == '01100': # start of lick window
            lick_window_start = split_data[1]
            continue

        elif sampling and split_data[2][:5] == '11010': # mouse lick
            time = time_dif(tt_start, split_data[1])
            trial_licks.append(np.array(time))
            continue

        elif sampling and split_data[2][:5] == '10010': # indicates a go lick / hit
            record = True
            continue

        elif sampling and split_data[2][:5] == '11101': # end of lick window
            lick_window_end = split_data[1]
            continue

        elif record and split_data[2][:5] == '10101': # indicates end of trial
            total_licks.append(trial_licks)
            true_trial_times.append((tt_start, split_data[1]))  # adds the start and end times of the tracked trial period
            lick_window_times.append([time_dif(tt_start, lick_window_start), time_dif(tt_start, lick_window_end)])

            sampling = False
            record = False
            trial_licks = []
            continue

    return total_licks, true_trial_times, lick_window_times

"""
Function takes data from a single log file and returns a list of No go trials in which a lick occured
each trial is a list of all lick times during that trial (from start of sampling window through the trial end code (includes the ITT))
all times are in seconds 
"""
# sample period = start of true trial
def get_noGo_lick_times_per_trial(file_data):
    total_licks = []
    trial_licks = []
    true_trial_times = []
    lick_window_times = []
    tt_start = 0
    record = False
    sampling = False

    for n, line in enumerate(file_data):   # iterate through all trials

        split_data = line.split(',')

        if split_data[2][:5] == '11001': # indicates start of sample period
            sampling = True
            tt_start = split_data[1]
            trial_licks = []
            lick_window_start = None
            lick_window_end = None
            continue

        elif sampling and split_data[2][:5] == '01100': # start of lick window
            lick_window_start = split_data[1]
            continue

        elif sampling and split_data[2][:5] == '11010': # mouse lick
            time = time_dif(tt_start, split_data[1])
            trial_licks.append(np.array(time))
            continue

        elif sampling and split_data[2][:5] == '00011': # indicates a noGo lick
            record = True
            continue

        elif sampling and split_data[2][:5] == '11101': # end of lick window
            lick_window_end = split_data[1]
            continue

        elif record and split_data[2][:5] == '10101': # indicates end of trial
            total_licks.append(trial_licks)
            true_trial_times.append((tt_start, split_data[1]))  # adds the start and end times of the tracked trial period
            lick_window_times.append([time_dif(tt_start, lick_window_start), time_dif(tt_start, lick_window_end)])

            sampling = False
            record = False
            trial_licks = []
            continue

    return total_licks, true_trial_times, lick_window_times


"""
Function returns an array of hits as a function of time for a given mouse. 
    A hit is defined as a Go lick (code 10010) 
"""
def get_hits_over_time(file_data):
    hits = []
    for n, line in enumerate(file_data):   # iterate through all trials

        split_data = line.split(',')

        if split_data[2][:5] == '00110':   # indicates Session Start
            session_start = stime_to_ntime(split_data[1])
        elif split_data[2][:5] == '10010':   # indicates presence of a Go Lick
            hits.append(stime_to_ntime(split_data[1]))

    return np.array(hits), session_start


"""
Function returns an array of trial starts as a function of time for a given mouse. 
    A trial start is defined as a Start Trial (code 01010) 
"""
def get_trialstarts_over_time(file_data):
    trial_time = 0
    ts = []
    for n, line in enumerate(file_data):  # iterate through all trials

        split_data = line.split(',')

        if split_data[2][:5] == '00110':  # indicates Session Start
            session_start = stime_to_ntime(split_data[1])
        elif split_data[2][:5] == '01010':  # indicates presence of a Trial Start
            trial_time = stime_to_ntime(split_data[1])
        elif split_data[2][:5] == '01100':  # indicates start of lick window (trial was successful)
            ts.append(trial_time)

    return np.array(ts), session_start

'''
Function returns the inter-trial-fire times for a single session 
Itt is calculated as the time between the open value of a previous 
session and the trial start of a next (properly started) trial  
'''
def get_session_ITTs(file_data):
    ITTs = []
    track = False
    for n, line in enumerate(file_data):  # iterate through all data file lines

        split_data = line.split(',')

        if split_data[2][:5] == '01000':  # indicates Open Valve
            start_time = stime_to_ntime(split_data[1])
            track = True

        elif track and split_data[2][:5] == '01010':  # indicates presence of a Trial Start
            trial_time = stime_to_ntime(split_data[1])

        elif track and split_data[2][:5] == '01100': # indicates start of lick window (trial was successful)
            itt = trial_time - start_time
            ITTs.append(itt)

    return np.array(ITTs)

'''
Function returns an array containing the per-day slope value of hits over all days for a single mouse
'''
def get_hit_heatmap(multi_day_data):
    slope_array = []
    for session_data in multi_day_data:
        hit_array, _ = get_hits_over_time(session_data)
        y = range(len(hit_array))
        slope, intercept, r_value, p_value, std_err = linregress(hit_array, y)
        slope_array.append(slope)

    return np.array(slope_array)

'''
Function returns an array containing the per-day slope value of trials initiated over time over all days for a single mouse
'''
def get_Itrials_heatmap(multi_day_data):
    slope_array = []
    for session_data in multi_day_data:
        Itrials_array, _ = get_trialstarts_over_time(session_data)
        y = range(len(Itrials_array))
        slope, intercept, r_value, p_value, std_err = linregress(Itrials_array, y)
        slope_array.append(slope)

    return np.array(slope_array)

'''
Function returns an array containing the times of peak licks over all days for a single mouse 
'''
def get_peak_licks_heatmap(multi_day_data, bin_num=30):
    multi_day_peak_array = []

    for session_data in multi_day_data:
        lick_data, _ = get_lick_times_per_true_trial(session_data)
        lick_data = np.concatenate(lick_data)
        hist, bin_edges = np.histogram(lick_data, bins=bin_num)
        peak_bin_index = np.argmax(hist)
        peak_bin_center = (bin_edges[peak_bin_index] + bin_edges[peak_bin_index + 1]) / 2

        multi_day_peak_array.append(peak_bin_center)

    return np.array(multi_day_peak_array)



if __name__ == '__main__':
    data = single_day_data(path='/Volumes/MATT_0/MousePi Data/Phase_1 Log Files/05-26/FANNY_SP2_05_26_2024_16_45_51.log')
    #lick_array, trial_times, lick_window_times = get_go_lick_times_per_trial(data)
    #hits, session_s = get_hits_over_time(data)
    #trial_starts, session_s = get_trialstarts_over_time(data)
    #itt_array = get_session_ITTs(data)





