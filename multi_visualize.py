import matplotlib
matplotlib.use('TkAgg')  # Set the backend to Agg for non-interactive plotting
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime

from data_loader import *



'''
Function Graphs the Average Inter-trial firing over multiple days for all given mice 
'''
def graph_multiDay_ITTs(multiDay_data, mouse_name_array, phase_num, ax=None):
    save_individual = False
    if ax is None:
        fig, ax = plt.subplots()
        save_individual = True

    for n, mouse in enumerate(mouse_name_array):
        multiDay_itt = []
        for session_data in multiDay_data[n]:
            itts_array = get_session_ITTs(session_data)
            mean_itt = np.mean(itts_array)
            multiDay_itt.append(mean_itt)

        x = np.array(range(len(multiDay_itt))) + 1
        y = multiDay_itt
        ax.plot(x, y, label=mouse)

    ax.set_title("Average Inter-Trial Times Over Days")
    ax.set_xlabel("Session Number")
    ax.set_ylabel("Inter-Trial Time (sec)")
    ax.legend()

    if save_individual:
        ax.set_title(f"Average Inter-Trial Times Over Days \n Phase {int(phase_num)}, Mice: {mouse_name_array}")
        plt.savefig(f'Graphs/{mouse_name_array}_phase {phase_num}_ITT Over Days')
        plt.show()



    return 0


'''
Function graphs the time value after stimulus onset where the majority of licks occur in each listed mouse over all days
'''
def graph_mice_peak_licks(multiday_data, mouse_name_array, phase_num, ax=None):
    save_individual = False
    all_peak_licks = []
    for n, mouse_data in enumerate(multiday_data):
        # get an array of times with peak licks over days
        peak_lick_array = get_peak_licks_heatmap(mouse_data)
        all_peak_licks.append((peak_lick_array))

    padded_data = get_sameLength_array(all_peak_licks)

    if ax is None:
        fig, ax = plt.subplots()
        save_individual = True

    sns.heatmap(padded_data, annot=True, fmt=".2f", cmap="viridis", cbar_kws={'label': 'Seconds after Image Onset'}, ax=ax)

    ax.set_title('Peak Lick Times Over Training Days')
    ax.set_xlabel('Training Days')
    ax.set_ylabel('Mice')
    ax.set_yticklabels(mouse_name_array)
    day_x_labels = np.array(range(len(padded_data[1]))) + 1
    ax.set_xticklabels(day_x_labels)

    if save_individual:
        ax.set_title(f'Peak Lick Times Over Training Days \n Phase: {phase_num}')
        plt.savefig(f'Graphs/{mouse_name_array}_phase {phase_num}_Peak Licks After Onset')
        plt.show()

    return 0

'''
Function graphs heatmap of slope (of hits over time) per day for all mice
'''
def graph_hit_slope_heat(multiday_data, mouse_name_array, phase_num, ax=None):
    save_individual = False
    all_hit_slopes = []
    for n, mouse_data in enumerate(multiday_data):
        mouse_slope_array = get_hit_heatmap(mouse_data)
        all_hit_slopes.append(mouse_slope_array)

    padded_data = get_sameLength_array(all_hit_slopes)

    if ax is None:
        fig, ax = plt.subplots()
        save_individual = True

    sns.heatmap(padded_data, annot=True, fmt=".2f", cmap="viridis", cbar_kws={'label': 'Session Hit Slope'}, ax=ax)

    ax.set_title('Session Hit Slopes Over Days')
    ax.set_xlabel('Training Days')
    ax.set_ylabel('Mice')
    ax.set_yticklabels(mouse_name_array)
    day_x_labels = np.array(range(len(padded_data[1]))) + 1
    ax.set_xticklabels(day_x_labels)

    if save_individual:
        ax.set_title(f'Session Hit Slopes Over Days \n Phase: {phase_num}')
        plt.savefig(f'Graphs/{mouse_name_array}_phase {phase_num}_Hit Slope Over Days')
        plt.show()

    return 0

'''
Function graphs heatmap of slope (of trial initiations over time) per day for all mice
'''
def graph_Itrials_slope_heat(multiday_data, mouse_name_array, phase_num, ax=None):
    save_individual = False
    all_Itrial_slopes = []
    for n, mouse_data in enumerate(multiday_data):
        mouse_slope_array = get_Itrials_heatmap(mouse_data)
        all_Itrial_slopes.append(mouse_slope_array)

    padded_data = get_sameLength_array(all_Itrial_slopes)

    if ax is None:
        fig, ax = plt.subplots()
        save_individual = True

    sns.heatmap(padded_data, annot=True, fmt=".2f", cmap="viridis", cbar_kws={'label': 'Slope of Initiated Trials Over Sessions'}, ax=ax)
    ax.set_title('Session Initiated Trials Slopes Over Days')
    ax.set_xlabel('Training Days')
    ax.set_ylabel('Mice')
    ax.set_yticklabels(mouse_name_array)
    day_x_labels = np.array(range(len(padded_data[1]))) + 1
    ax.set_xticklabels(day_x_labels)

    if save_individual:
        ax.set_title(f'Session Initiated Trials Slopes Over Days \n Phase: {phase_num}')
        plt.savefig(f'Graphs/{mouse_name_array}_phase {phase_num}_Initiated Trials Slopes Over Days')
        plt.show()

    return 0

'''
Function allows all multi-day graphs to be run at once for given mouse names 
'''
def graph_all_MultiMice(multiday_data, mouse_name_array, phase_num, save_path=None):
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))  # Create a 2x2 subplot grid

    # Plot 1: Inter-Trial Times
    graph_multiDay_ITTs(multiday_data, mouse_name_array, phase_num, ax=axs[0, 0])

    # Plot 2: Peak Lick Times
    graph_mice_peak_licks(multiday_data, mouse_name_array, phase_num, ax=axs[0, 1])

    # Plot 3: Hit Slopes
    graph_hit_slope_heat(multiday_data, mouse_name_array, phase_num, ax=axs[1, 0])

    # Plot 4: Initiated Trials Slopes
    graph_Itrials_slope_heat(multiday_data, mouse_name_array, phase_num, ax=axs[1, 1])

    fig.suptitle(f'{mouse_name_array}: Phase {phase_num}')
    fig.tight_layout()

    if save_path != None:
        if save_path[-1] != "/":
            save_path += "/"
        save_path += f'Graphs: {datetime.now().date()}/'
        directory = os.path.dirname(save_path)
        if not os.path.exists(directory):  # Create the directory if it does not exist
            os.makedirs(directory)

        plt.savefig(f'{save_path}{mouse_name_array}_phase {phase_num}_ALL MULTIDAY GRAPHS')

    # plt.show()
    plt.close()

    return 0

if __name__ == '__main__':
    data = get_multiDay_mice_data(["ODELIA", "TAMMY", "THEO", "FREDA"], phase=1)
    graph_all_MultiMice(data, ["Odelia", "Tammy", "Theo", "Freda"], 1)
