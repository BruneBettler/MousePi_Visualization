from ind_visualize import *
from multi_visualize import *
from datetime import datetime


'''
Script makes and saves all desired graphs for all desired mice as 
specified below
'''
params = {
    'path': '/Volumes/MATT_1/behavior/Pilot_5_june_7/Phase 1',
    'mice_to_analyze': ['OLAF','THOR', 'POPPY', 'FANNY'], # names must be in all caps; inlcude only one name for single mouse analysis
    'phase': 1
        }


'''
Simply click the green arrow and see the chosen graphs in the graph folder once finished running
'''
def pipeline_0():
    # go through all different session folders in the path
    # get all data for every mouse across sessions
    all_data = get_multiDay_mice_data(params['mice_to_analyze'], path=params['path'])
    mice_data = []
    # run single day analysis for all mice
    for mouse_n, mouse_data in enumerate(all_data):
        data = mouse_data[0]
        mice_data.append(data)
        sessions = mouse_data[1]
        for n, session in enumerate(sessions):
            graph_all_singleMouse(data[n], f"{params['mice_to_analyze'][mouse_n]}_Single_Day_Analysis_{session}", params['phase'], n+1, 15, save_path=params['path'])
            print(f"{datetime.now()}: graph_all_singleMouse for {params['mice_to_analyze'][mouse_n]}, session: {session} is DONE!")
            goNogo_lick_analysis_single_mouse(data[n], f"{params['mice_to_analyze'][mouse_n]}_Single_Day_Analysis_{session}", params['phase'], n+1, save_path=params['path'])
            print(f"{datetime.now()}:graph_GOnoGO for {params['mice_to_analyze'][mouse_n]}, session: {session} is DONE!")


    graph_all_MultiMice(mice_data, params['mice_to_analyze'], params['phase'], save_path=params['path'])
    print(f"{datetime.now()}: graph_all_MultiMouse for {params['mice_to_analyze']} is DONE!")
    print(f"{datetime.now()}: All Done!")
    return 0

if __name__ == "__main__":
    pipeline_0()