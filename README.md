# MousePi Data Visualization and Analysis
This repository contains code for visualizing .log and image/video files from the MousePi behavioral rig. 

## Table of Contents
- [Files and Modules](#files-and-modules)
  - [data_loader.py](#data_loaderpy)
  - [log_docu_dict.json](#log_docu_dictjson)
  - [ind_visualize.py](#ind_visualizepy)
  - [multi_visualize.py](#multi_visualizepy)
  - [run.py](#runpy)
  - [utils.py](#utilspy)
  - [video_processing.py](#video_processingpy)
  
## Files and Modules

### log_docu_dict.json
File contains all .log file codes and their respective string meaning.

### data_loader.py
Contains all functions used to load and handle data from a .log file. Functions are also present to convert this data into usable arrays for the individual and multi visualize graphing modules. 

#### Functions:

###### .log --> array 
- `get_log_by_trial`: Loads data from a single .log file and returns an array containing, for each trial, information about the start and stop line number on the OG log file as well as all string lines contained in the trial. 
- `single_day_data`: Loads data from a single .log file (single mouse, single session) and converts each line into a string. A single array of strings is returned. 
- `multi_day_data`: Parses a series of .log files for a single mouse and returns a multidimensional array with one array per session. Each session array is created as in the single_day_data function.
- `get_multiDay_mice_data`: Parses all .log files for all specified mice. Returns a multidimensional array containing one multidimensional array per mouse as specified in the above two functions.
###### Raw data array --> graphing-ready data 
- `get_lick_times_per_true_trial`: Creates lick data ready for rPSTH graphing. Function returns the time difference in seconds between the simulus onset and all licks occurring during GO pass trials (does not include Go miss trials and only includes trials that have been properly started). The lick range is from the start of the cue appearance to the end of the lick window only.   
- `get_go_lick_times_per_trial`: Same as the above function but includes a greater range (from stimulus onset to end of trial).
- `get_noGo_lick_times_per_trial`: Identical to the 'get_go_lick_times_per_trial' function but returns data for all NoGo trials that contain licks. 
- `get_hits_over_time`
- `get_trialstarts_over_time` 
- `get_session_ITTs` 
<br><br>
- `get_hit_heatmap` 
- `get_Itrials_heatmap`
- `get_peak_licks_heatmap`

### utils.py
This module contains helper functions for the data_loader.py and log_analysis.py files.

#### Functions:
- `stime_to_ntime`: From an input time string, returns the float time in seconds.
- `time_dif`
- `get_sameLength_array`: Used for the multi_visualize graphs 

### ind_visualize.py
This module provides functions to visualize data for a single mouse. Graphs included are for single sessions or single mouse-multi-sessions.

#### Functions:
- `graph_session_rPSTH`: For a single mouse and single session: Graphs a raster plot and corresponding PSTH for input licks. The stimulus window is shown in gray and all licks made during the lick window are highlighted in red. 
- `graph_session_hits`
- `graph_trial_starts`
- `graph_all_singleMouse`: For a single mouse and single session: Graphs the rPSTH, session hits, and trial starts graphs on a single image.
- `goNogo_lick_analysis_single_mouse`: For a single mouse and single session: Graphs both the rPSTH for Go and NoGo trials. 

### multi_visualize.py
This module provides functions to visualize data from multiple mice over multiple sessions. 

#### Functions:
- `graph_multiDay_ITTs`
- `graph_mice_peak_licks`
- `graph_hit_slope_heat`
- `graph_Itrials_slope_heat`
- `graph_all_MultiMice`: Graphs all four above graphs in a single image.

### run.py
This script contains and runs the main pipelines for graphing desired mouse and session data.
Important and variable variables are stored in the params dictionary at the top of the script. This dictionary is then used in the differing pipelines.

#### Functions:
- `main()`: The main function calls the desired pipeline and allows the code to run.
- `pipeline_0()`: Runs for all desired mice: the 3 graph summary image for each session and a GoNoGo graph for each session. For all mice and all sessions, a summary multi-graph is made as well. All graphs are saved and the last created/saved image is logged by a printed statement containing the time of completion in order to track progress. 
- `add_new_session()`: Runs all graphing for all mice in a single session (summary session per mouse and GoNoGo graph per mouse). Also creates an updated multimouse_multisession graph.

### log_analysis.py
This script contains all functions used for debugging / further analyzing the .log files.

#### Functions:
- `all_gap_info`: Creates a histogram for all inter-lick gaps contained per trial in a single mouse session. The specific lick gap durations and their occurrence number is also printed. The histogram is not saved.
- `avg_valveLick`: Calculated the average time in seconds between the open valve and next lick of a current trial. 
- `bad_lick_bout_analysis`: Shows a histogram of the gap length between the last pre-trial (bad) lick of the previous trial and the sample start time of the subsequent correct trial.
- `graph_singleMouse_Lick_summary`: TODO: ...In progress...

### video_processing.py
This script contains all the necessary functions, including the main function, for writing subtitles on a mouse lick video image sequence. An option is also available for creating an .mp4 video as well as a folder of subtitled images. 

#### Functions:
- `im_to_vid`
- `add_subtitles`
- `get_capture_time`
- `get_ms_range`
- `get_log_events`
- `get_event`
- `write_subtitle`
- `update_trial_phase`