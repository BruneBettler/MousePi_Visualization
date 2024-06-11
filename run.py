from ind_visualize import *
from multi_visualize import *
from datetime import datetime


'''
Script makes and saves all desired graphs for all desired mice as specified below. 
DO NOT include a last / when indicating a folder in path. ex. ('/Volumes/MATT_1/behavior/Pilot_5_june_10/Phase 1')
'''
params = {
    'path_to_all': '/Volumes/MATT_1/behavior/Pilot_5_june_10/Phase 1',
    'path_to_session': '/Volumes/MATT_1/behavior/Pilot_5_june_10/Phase 1/06-10',
    'session_numbers': [13,13,8,8], # add the session number of the new session you are adding in the order of the mice_to_analyze list below
    'mice_to_analyze': ['OLAF','THOR', 'POPPY', 'FANNY'], # names must be in all caps; inlcude only one name for single mouse analysis
    'phase': 1
        }


'''
Simply click the green arrow and see the chosen graphs in the graph folder once finished running
'''
def pipeline_0():
    # go through all different session folders in the path
    # get all data for every mouse across sessions
    all_data = get_multiDay_mice_data(params['mice_to_analyze'], path=params['path_to_all'])
    mice_data = []
    # run single day analysis for all mice
    for mouse_n, mouse_data in enumerate(all_data):
        data = mouse_data[0]
        mice_data.append(data)
        sessions = mouse_data[1]
        for n, session in enumerate(sessions):
            graph_all_singleMouse(data[n], f"{params['mice_to_analyze'][mouse_n]}_Single_Day_Analysis_{session}", params['phase'], n+1, 15, save_path=params['path_to_all'])
            print(f"{datetime.now()}: graph_all_singleMouse for {params['mice_to_analyze'][mouse_n]}, session: {session} is DONE!")
            goNogo_lick_analysis_single_mouse(data[n], f"{params['mice_to_analyze'][mouse_n]}_Single_Day_Analysis_{session}", params['phase'], n+1, save_path=params['path_to_all'])
            print(f"{datetime.now()}:graph_GOnoGO for {params['mice_to_analyze'][mouse_n]}, session: {session} is DONE!")


    graph_all_MultiMice(mice_data, params['mice_to_analyze'], params['phase'], save_path=params['path_to_all'])
    print(f"{datetime.now()}: graph_all_MultiMouse for {params['mice_to_analyze']} is DONE!")
    print(f"{datetime.now()}: All Done!")
    return 0

def add_new_session():
    all_mice_data = get_multiDay_mice_data(params['mice_to_analyze'], path=params['path_to_all'])
    clean_mice_data = []
    session_date = params['path_to_session'][-5:]
    for mouse_n, mouse in enumerate(params['mice_to_analyze']):
        clean_mice_data.append(all_mice_data[mouse_n][0])
        for _, _, files in os.walk(params['path_to_session']):
            for file_name in files:
                if file_name[-4:] == '.log' and file_name[:len(mouse)] == mouse:
                    file = params['path_to_session'] + '/' + file_name
                    break

        mouse_data = single_day_data(path=file)
        graph_all_singleMouse(mouse_data, f"{params['mice_to_analyze'][mouse_n]}_Single_Day_Analysis_{session_date}", params['phase'], params['session_numbers'][mouse_n], 15, save_path=params['path_to_all'])
        print( f"{datetime.now()}: graph_all_singleMouse for {mouse}, session: {session_date} is DONE!")
        goNogo_lick_analysis_single_mouse(mouse_data, f"{mouse}_Single_Day_Analysis_{session_date}", params['phase'], params['session_numbers'][mouse_n], save_path=params['path_to_all'])
        print(f"{datetime.now()}:graph_GOnoGO for {mouse}, session: {session_date} is DONE!")

    graph_all_MultiMice(clean_mice_data, params['mice_to_analyze'], params['phase'], save_path=params['path_to_all'])
    print(f"{datetime.now()}: graph_all_MultiMouse for {params['mice_to_analyze']} is DONE!")
    print(f"{datetime.now()}: All Done!")
    return 0

if __name__ == "__main__":
    #pipeline_0()
    add_new_session()