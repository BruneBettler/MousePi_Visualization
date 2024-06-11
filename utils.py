import numpy as np

"""
Function takes as input a string time in the following format: '17:43:42.290'
and returns the time as a single value in seconds (float)
"""
def stime_to_ntime(string_time):
    tsplit = string_time.split(':')
    sec_time = float(tsplit[0])*60.0*60.0 + float(tsplit[1])*60.0 + float(tsplit[2])
    return sec_time


"""
Function returns the amount of seconds that have occured between the sampling start and the lick 
"""
def time_dif(trial_start, lick_time):
    ts = stime_to_ntime(trial_start) # in seconds
    lt = stime_to_ntime(lick_time)   # in seconds
    return lt - ts


'''
Function returns an array where each row is the same length 
(shorter input rows are padded with np.nan)
'''
def get_sameLength_array(input_array):
    # Find the length of the longest row
    max_length = max(len(row) for row in input_array)
    # Pad the rows with NaN values to make all rows the same length
    padded_data = []
    for row in input_array:
        if len(row) != max_length:
            fill_length = max_length - len(row)
            to_add = np.full(fill_length, np.nan)
            n_row = np.concatenate((row, to_add))
            padded_data.append(n_row)
        else:
            padded_data.append(row)

    return np.array(padded_data)

