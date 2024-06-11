import matplotlib
import numpy as np

matplotlib.use('TkAgg')  # Set the backend to Agg for non-interactive plotting
import matplotlib.pyplot as plt
from data_loader import *
from datetime import datetime


def graph_session_rPSTH(licks_per_trial, mouse, phase_num, session_num, lick_window_times, axs=None, Go=True):
    save_individual = False
    if axs is None:
        fig, axs = plt.subplots(2,1, figsize=[10,5])
        save_individual = True

    # rasterplot below
    all_in_range = []
    all_out_range = []
    for trial_num, trial_data in enumerate(licks_per_trial): # parsing through each trial
        # check if each lick is in the lick window, if so, color it red
        trial_data = np.array(trial_data)  # Convert to NumPy array for efficient processing

        # Boolean indexing to find ticks within the specified range
        in_range_ticks = trial_data[(trial_data >= lick_window_times[trial_num][0]) & (trial_data <= lick_window_times[trial_num][1])]
        all_in_range.append(in_range_ticks)
        out_range_ticks = trial_data[(trial_data < lick_window_times[trial_num][0]) | (trial_data > lick_window_times[trial_num][1])]
        all_out_range.append(out_range_ticks)

        # Plot ticks within the range
        axs[0].vlines(in_range_ticks, trial_num - 0.5, trial_num + 0.5, color="red")

        # Plot ticks outside the range
        axs[0].vlines(out_range_ticks, trial_num - 0.5, trial_num + 0.5, color="black")

    axs[0].axvspan(0, 0.5, alpha=0.5, color='lightgray')
    axs[0].set_ylabel(f'Trial Number (Total: {len(licks_per_trial)})')
    axs[0].set_xlim([-0.1,2.1]) #[0.49, 0.53]
    if Go:
        axs[0].set_title('Licks during hit "GO" trials | Gray=Stim on, Red=in lick window')
    else:
        axs[0].set_title('Licks during "NO GO" trials | Gray=Stim on, Red=in lick window')

    axs[0].set_xlabel('Time from image onset (s)')

    all_in_range = np.concatenate(all_in_range)
    all_out_range = np.concatenate(all_out_range)
    hist_data = [all_in_range, all_out_range]
    # PSTH below
    axs[1].axvspan(0, 0.5, alpha=0.5, color='lightgray')
    axs[1].hist(hist_data, bins=500, log=True, color=["red", "black"], label=['In lick window', 'Out of lick window'], stacked=True)

    axs[1].set_xlim([-0.1,2.1]) #[0.49, 0.53]
    axs[1].set_title('Peristimulus Time Histogram For Above Licks')
    axs[1].set_xlabel('Time from image onset (s)')
    axs[1].set_ylabel('Log Licks')


    if save_individual:
        fig.suptitle(f'Licks Over Time and Corresponding PSTH \n{mouse}: Phase {phase_num} Session {session_num}')
        plt.tight_layout()
        plt.savefig(f'Graphs/{mouse}_phase {phase_num}_session {session_num}_rPSTH')
        plt.show()

    return 0

"""
Function graphs the number of hit licks over time for a single mouse over a single session  
"""
def graph_session_hits(num_bins, hit_data, session_start_time, mouse, phase_num, session_num, axs=None):
    save_individual = False
    if axs is None:
        fig, axs = plt.subplots(figsize=(10,5))
        save_individual = True

    # divide hit data into different bins
    counts, bin_edges = np.histogram(hit_data, bins=num_bins)
    bin_edges -= session_start_time
    bin_edges /= 60
    axs.bar(bin_edges[:-1], counts, align='edge', width=np.diff(bin_edges), color='darkgray', edgecolor='white', alpha=0.5, label='Time Bins')

    # Adding the scatter plot for hit times
    bin_midpoints = bin_edges[:-1] + np.diff(bin_edges)/2
    axs.scatter(bin_midpoints, counts, color='black', label='Counts at bin midpoints')
    axs.plot(bin_midpoints, counts, color='black')

    axs.set_xlabel('Time from start of session (min)')
    axs.set_ylabel('Hit Count')
    axs.set_title('Hit Lick Distribution')

    if save_individual:
        axs.set_title(f'Hit Distribution \n{mouse}: Phase {phase_num} Session {session_num}')
        plt.savefig(f'Graphs/{mouse}_phase {phase_num}_session {session_num}_HITS OVER TIME')
        plt.show()

    return 0

"""
Function graphs the number of trial over time for a single mouse over a single session  
"""
def graph_trial_starts(num_bins, ts_data, session_start_time, mouse, phase_num, session_num, axs=None):
    save_individual = False
    if axs is None:
        fig, axs = plt.subplots(figsize=(10,5))
        save_individual = True

    # divide hit data into different bins
    counts, bin_edges = np.histogram(ts_data, bins=num_bins)
    bin_edges -= session_start_time
    bin_edges /= 60
    axs.bar(bin_edges[:-1], counts, color='darkgray', align='edge', width=np.diff(bin_edges), edgecolor='white', alpha=0.5, label='Time Bins')

    # Adding the scatter plot for hit times
    bin_midpoints = bin_edges[:-1] + np.diff(bin_edges)/2
    axs.scatter(bin_midpoints, counts, color='black', label='Counts at bin midpoints')
    axs.plot(bin_midpoints, counts, color='black')
    axs.set_xlabel('Time from start of session (min)')
    axs.set_ylabel('Trial Start Count')
    axs.set_title('Trial Start Distribution')

    if save_individual:
        axs.set_title(f'Trial Start Distribution \n{mouse}: Phase {phase_num} Session {session_num}')
        plt.savefig(f'Graphs/{mouse}_phase {phase_num}_session {session_num}_TRIAL STARTS OVER TIME')
        plt.show()

    return 0


'''
Function allows all graphs to be run at once for a single mouse
'''
def graph_all_singleMouse(mouse_data, mouse_name, phase_num, session_num, bin_num, save_path=None):
    total_licks, trial_times, lick_window_times = get_go_lick_times_per_trial(mouse_data)
    hits, hits_session_s = get_hits_over_time(mouse_data)
    ts, ts_session_s = get_trialstarts_over_time(mouse_data)

    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.4)

    # Plot each of the three graphs on one figure
    ax_rPSTH1 = fig.add_subplot(gs[0, 0])
    ax_rPSTH2 = fig.add_subplot(gs[1, 0])
    graph_session_rPSTH(licks_per_trial=total_licks, mouse=mouse_name, phase_num=phase_num, session_num=session_num, lick_window_times=lick_window_times, axs=[ax_rPSTH1, ax_rPSTH2])

    ax_hits = fig.add_subplot(gs[0, 1])
    graph_session_hits(num_bins=bin_num, hit_data=hits, session_start_time=hits_session_s, mouse=mouse_name, phase_num=phase_num, session_num=session_num, axs=ax_hits)

    ax_trial_starts = fig.add_subplot(gs[1, 1])
    graph_trial_starts(num_bins=bin_num, ts_data=ts, session_start_time=ts_session_s, mouse=mouse_name, phase_num=phase_num, session_num=session_num, axs=ax_trial_starts)

    fig.suptitle(f'{mouse_name}: Phase {phase_num} Session {session_num}')

    if save_path != None:
        if save_path[-1] != "/":
            save_path += "/"
        save_path += f'Graphs: {datetime.now().date()}/'
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory): # Create the directory if it does not exist
            os.makedirs(directory)

        plt.savefig(f'{save_path}{mouse_name}_phase {phase_num}_session {session_num}_ALL SINGLE SESSION GRAPHS')

    #plt.show()
    plt.close()

    return 0

'''
Function graphs the raster plot and PSTH for both "go" and "no go" trials with licks 
'''
def goNogo_lick_analysis_single_mouse(mouse_data, mouse_name, phase_num, session_num, save_path=None):
    total_go_licks, go_trial_times, go_lick_window_times = get_go_lick_times_per_trial(mouse_data)
    total_Nogo_licks, Nogo_trial_times, Nogo_lick_window_times = get_noGo_lick_times_per_trial(mouse_data)

    fig = plt.figure(figsize=(15, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.4)

    ax_rPSTH1 = fig.add_subplot(gs[0, 0])
    ax_rPSTH2 = fig.add_subplot(gs[1, 0])
    graph_session_rPSTH(licks_per_trial=total_go_licks, mouse=mouse_name, phase_num=phase_num, session_num=session_num,
                        lick_window_times=go_lick_window_times, axs=[ax_rPSTH1, ax_rPSTH2], Go=True)

    ax_rPSTH3 = fig.add_subplot(gs[0, 1])
    ax_rPSTH4 = fig.add_subplot(gs[1, 1])
    graph_session_rPSTH(licks_per_trial=total_Nogo_licks, mouse=mouse_name, phase_num=phase_num, session_num=session_num,
                        lick_window_times=Nogo_lick_window_times, axs=[ax_rPSTH3, ax_rPSTH4], Go=False)


    fig.suptitle(f'{mouse_name}: Phase {phase_num} Session {session_num}')

    if save_path != None:
        if save_path[-1] != "/":
            save_path += "/"
        save_path += f'Graphs: {datetime.now().date()}/'
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory):  # Create the directory if it does not exist
            os.makedirs(directory)

        plt.savefig(f'{save_path}{mouse_name}_phase {phase_num}_session {session_num}_ Go and No Go PSTH View')

    # plt.show()
    plt.close()

    return 0

if __name__ == '__main__':
    data = single_day_data(path='/Volumes/MATT_0/MousePi Data/Phase_1 Log Files/05-26/FANNY_SP2_05_26_2024_16_45_51.log')
    graph_all_singleMouse(data, "FANNY Phase 1 test", 1, 0, 15, save_path='/Volumes/MATT_0/MousePi Data/Phase_1 Log Files')
    goNogo_lick_analysis_single_mouse(data, "FANNY", 1, 0, save_path='/Volumes/MATT_0/MousePi Data/Phase_1 Log Files')


