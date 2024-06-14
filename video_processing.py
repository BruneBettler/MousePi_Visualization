import cv2
from data_loader import *
import json
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
from tqdm import tqdm

with open('log_docu_dict.json', 'r') as file:
    log_docu_dict = json.load(file)

'''
Function converts a folder of images into a video 
The video is saved and the images are kept
'''
def im_to_vid(imFolder_path, vid_path):
    if vid_path[-4:] != '.avi':
        vid_path += '.avi'

    if imFolder_path[-1] == '/':
        imFolder_path = imFolder_path[:-1]

    images = [img for img in os.listdir(imFolder_path) if img.endswith(".jpg")]
    images.sort()
    frame = cv2.imread(os.path.join(imFolder_path, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(vid_path, 0, 7, (width, height))

    for i,image in tqdm(enumerate(images)):
        video.write(cv2.imread(os.path.join(imFolder_path, image)))

    cv2.destroyAllWindows()
    video.release()

    return 0


'''
Function adds subtitles to all images within a video frame 
as detailed in the Video_Processing_README.md file
'''
def add_subtitles(imFolder_path, log_file_data, rewrite=False, save_vid=False, vid_name=None): # TODO: set save_vid to True after debugging is done
    if imFolder_path[-1] == '/':
        imFolder_path = imFolder_path[:-1]

    images = [img for img in os.listdir(imFolder_path) if img.endswith(".jpg")]
    images.sort()
    im_num = len(images)
    prev_run = [0, None, None]  # [next_start_n, prev_GNG, prev_trial_phase]
    next_start_lower_range = np.inf
    GNG_text = ' '

    for n, im in tqdm(enumerate(images)):
        # retrieve the time the im was captured (in ms)
        snap_time_ms = get_capture_time(im)
        # identify the 142 ms range in which it is contained (71ms in either direction)
        ms_range = get_ms_range(snap_time_ms)

        # identify the start range for the next image in order to
        if n != len(images) - 1:  # if it's the last image, it does not have a next image
            next_im = images[n+1]
            next_snap_t = get_capture_time(next_im)
            next_ms_range = get_ms_range(next_snap_t)
            next_start_lower_range = next_ms_range[0]

        # given this time range, identify all events from the log file that happen during the range
        events_in_range, GNG_text, color, prev_run = get_log_events(log_file_data, ms_range, prev_run, next_start_lower_range, GNG_text)

        if len(events_in_range) == 0:
            subtitle = "N/A"
            # continue
        else: subtitle = '; '.join(events_in_range)

        im_path = f'{imFolder_path}/{im}'
        sub_image = write_subtitle(im_path, subtitle, color, GNG_text)

        # either rewrite over the images or create new images with subtitles
        if not rewrite:
            image_path = f'{imFolder_path}_MODIFIED/SUBTITLED_{im}'
            directory = os.path.dirname(image_path)
            if not os.path.exists(directory):
                # Create the directory if it does not exist
                os.makedirs(directory)
        else: image_path = im_path

        sub_image.save(image_path, 'JPEG')  # Save as JPEG

        if n % 1000 == 0:
            print(f'{datetime.now()}: {n + 1} / {im_num} images have been saved...')

    # save video if desired
    if save_vid:
        if vid_name[-4:] != '.avi':
            vid_name += '.avi'
        im_to_vid(imFolder_path, vid_name)

    return 0

'''
Function returns the time at which an image was captured given the time in it's fileName 
time is in ms
'''
def get_capture_time(image):
    str_time = image[11:26] # time from the im file name in the format "15-25-52-156290" for hour min sec ms
    tsplit = str_time.split('-')
    s_time = float(tsplit[0])*3600 + float(tsplit[1])*60 + float(tsplit[2]) + float('.'+ tsplit[3])
    ms_time = s_time * 1000

    return ms_time


'''
Function returns the start and stop times of the 142 ms range in which the capture time is contained 
The capture time is in the middle of this 142ms range. 
formatted as an array: ex) [156290, 156432]
'''
def get_ms_range(capture_ms_time):
    start = capture_ms_time - 72  # 71
    end = capture_ms_time + 72  # 71

    return [start, end]


'''
Function returns a list of all events that happen in the log file during the given time range
'''
def get_log_events(log_file_data, ms_range, prev_run, next_start_lower_range, GNG_text): # prev_run = [next_start_n, GNG, trial_phase]
    all_events_in_range = []
    colors = [(204, 85, 0),  (139, 0, 0), (155, 135, 12), (50, 100, 200)] # burnt orange, deep red, dark yellow, light navy blue (in RBG)
    next_start_n = prev_run[0]


    if prev_run[1] is not None:
        start_index, GNG, trial_phase = prev_run
        log_file_data = log_file_data[start_index:] # skip already "seen" file lines
    else:
        trial_phase = np.array([1, 0, 0, 0])  # [ITT, pre_trial_period, sample_period, lick_window]
        GNG = False
        start_index = 0 # Start from the first line

    for n, line in enumerate(log_file_data, start=start_index):  # Adjust start index in enumerate
        split_data = line.split(',')

        current_event = split_data[2][:5]
        curr_log_time = stime_to_ntime(split_data[1]) * 1000 # stime_to_ntime returns seconds (we want ms)

        # check to see when the next starting point will be
        if curr_log_time <= next_start_lower_range:
            next_start_n = n

        # update the trial_phase and color if necessary
        trial_phase, GNG = update_trial_phase(trial_phase, current_event,GNG)
        background_color = colors[np.argmax(trial_phase)]
        # update the GNG if necessary
        if GNG and current_event == '00010': # update GNG info
            GNG_str = split_data[4]
            if GNG_str[-4:] == '90.0': # Go / Horizontal
                GNG_text = 'Go'
            else:  # No Go / vertical / 0.0
                GNG_text = 'No Go'
        elif GNG:
            GNG_text = GNG_text # GNG_text remains the same
        else:
            GNG_text = ' '


        if ms_range[0] <= curr_log_time <= ms_range[1]:
            binary_str_code = split_data[2][:5]
            event = get_event(binary_str_code, split_data)
            all_events_in_range.append(event)
        if curr_log_time > ms_range[1]:
            break

    all_events_in_range = np.array(all_events_in_range)
    unique_events = np.unique(all_events_in_range)

    return unique_events, GNG_text, background_color, [next_start_n, GNG, trial_phase]  # background_color represents the trial phase


'''
Function returns a string containing the "type" of event happening based on a particular 5 number code
code is translated based on the JSON file called 
'''
def get_event(binary_str_code, split_data):
    event_str = log_docu_dict[binary_str_code]
    if event_str == "Stimulus Information":
        event_str = "Stimulus Information: " + split_data[3] + ', ' + split_data[4] + ', ' + split_data[5][:-1]

    return event_str


'''
Function writes subtitle on bottom left corner of a given image
rewrite is True to overwrite the original image and False to make a new set of images and 
conserve the previous images 
'''
def write_subtitle(im_path, subtitle, background_color, GNG_text):
    image = Image.open(im_path)
    draw = ImageDraw.Draw(image)
    width, height = image.size
    font = ImageFont.truetype(r'C:\Users\mlouki1\Downloads\Arial-Unicode-Regular.ttf', 26)
    text_color = (255,255,255)

    # Calculate the bounding box of the text and the subtitle bar height
    text_bbox = draw.textbbox((0, 0), 'MAKE THE SUBTITLE BAR THIS WIDE', font=font)
    subtitle_box = draw.textbbox((0, 0), subtitle, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    subtitle_bar_height = (text_height + 20) * 2 # since we want the bar to be two subtitle lines thick  # Adding padding

    # Draw the subtitle bar
    draw.rectangle([(0, height - subtitle_bar_height), (width, height)], fill=background_color)

    if subtitle_box[2] - subtitle_box[0] + 20 >= width: # subtitle and padding (left + right) is longer than the image
        # Find the midpoint of the subtitle for splitting
        mid_point = len(subtitle) // 2
        # Find the nearest space to split the subtitle
        split_point = mid_point + subtitle[mid_point:].find(' ')
        if split_point == mid_point:  # No space found in the second half, search in the first half
            split_point = subtitle[:mid_point].rfind(' ')
        # Split the subtitle into two lines
        first_line = subtitle[:split_point]
        second_line = subtitle[split_point + 1:]  # Skip the space

        text_x_0 = 10  # Padding from the left
        text_y_0 = height - subtitle_bar_height + 10  # Padding from the top of the subtitle bar
        draw.text((text_x_0, text_y_0), first_line, fill=text_color, font=font)

        text_x_1 = 10  # Padding from the left
        text_y_1 = height - (subtitle_bar_height)/2 - 5  # Padding from the top of the subtitle bar
        draw.text((text_x_1, text_y_1), second_line, fill=text_color, font=font)
    elif subtitle == "N/A":
        text_x = 10  # Padding from the left
        text_y = height - subtitle_bar_height + 10  # Padding from the top of the subtitle bar
        draw.text((text_x, text_y), subtitle, fill=background_color, font=font) # does not show
    else:
        text_x = 10  # Padding from the left
        text_y = height - subtitle_bar_height + 10  # Padding from the top of the subtitle bar
        draw.text((text_x, text_y), subtitle, fill=text_color, font=font)

    # add label indicating which phase of the experiment we are at
    # Calculate the bounding box of the text and the subtitle bar height
    TP_bbox = draw.textbbox((0, 0), ' Pre Trial Period ', font=font)  # use the longest text as bounding box
    TP_width = TP_bbox[2] - TP_bbox[0]
    TP_height = TP_bbox[3] - TP_bbox[1]
    TP_bar_height = (TP_height + 20)  # add padding
    TP_bar_width = (TP_width + 20)

    # draw background box
    draw.rectangle([(0, height - subtitle_bar_height - TP_bar_height), (TP_bar_width, height - subtitle_bar_height)],fill=background_color)

    # add corresponding text
    if background_color == (204, 85, 0):
        TP_text = ' ITT '
    elif background_color == (139, 0, 0):
        TP_text = ' Pre Trial Period '
    elif background_color == (155, 135, 12):
        TP_text = ' Sampling Period '
    else:
        TP_text = ' Lick Window '

    draw.text((5, height - subtitle_bar_height - TP_bar_height + 2.5), TP_text, fill=(255, 255, 255), font=font)

    # add go or no go in the top right corner (black if not sample period and lick window and then green or red otherwise
    # add rectangle of __ color (black red or green) right above the subtitle line
    # Calculate the bounding box of the text and the subtitle bar height
    GNG_bbox = draw.textbbox((0, 0), 'No Go', font=font) # "No Go" is longer then "Go" or " "
    GNG_width = GNG_bbox[2] - GNG_bbox[0]
    GNG_height = GNG_bbox[3] - GNG_bbox[1]
    GNG_bar_height = (GNG_height + 20)  # add padding
    GNG_bar_width = (GNG_width + 20)

    # Draw the GNG bar
    if background_color == (155, 135, 12) or background_color == (50, 100, 200): # dark yellow - sample period / blue - lick window
        if GNG_text == 'No Go': # red box
            draw.rectangle([(TP_bar_width, height - subtitle_bar_height - TP_bar_height), (TP_bar_width + GNG_bar_width, height - subtitle_bar_height)],fill=(255, 0, 0)) # RGB
            draw.text((10+TP_bar_width, height - subtitle_bar_height - TP_bar_height + 2.5), GNG_text, fill=(0,0,0), font=font)
        elif GNG_text == 'Go': # go / green box
            draw.rectangle([(TP_bar_width, height - subtitle_bar_height - TP_bar_height), (TP_bar_width + GNG_bar_width, height - subtitle_bar_height)],fill=(0, 255, 0)) # RGB
            draw.text((10+TP_bar_width, height - subtitle_bar_height - TP_bar_height + 2.5), GNG_text, fill=(0,0,0), font=font)
        else:
            draw.rectangle([(TP_bar_width, height - subtitle_bar_height - TP_bar_height), (TP_bar_width + GNG_bar_width, height - subtitle_bar_height)],fill=(0, 0, 0))

    return image

'''
Function returns the updated experiment phase in order to color the subtitle correctly 
'''
def update_trial_phase(curr_phase, current_event, GNG):

    # trial_phase has format (1-hot) [1,0,0,0] # [ITT, pre_trial_period, sample_period, lick_window]

    if current_event == '00111': # end of ITT
        updated_phase = [0,1,0,0]
        GNG = False
    elif current_event == '11001': # start of image display
        updated_phase = [0,0,1,0]
        GNG = True
    elif current_event == '01001': # end of image display / beginning of lick window
        updated_phase = [0,0,0,1]
        GNG = True
    elif current_event == '11101': # end of lick window
        updated_phase = [1,0,0,0]
        GNG = False

    else:
        updated_phase = curr_phase

    return updated_phase, GNG

if __name__ == '__main__':
    #imFolder_path = 'Data/Video/05-22/BVTEST_SP2_05_22_2024_15_25_29_05_22_2024_15_25_29'
    imFolder_path = r"D:\MousePi Data\Mouse Videos\Image Folders\Phase_1\FANNY_SP2_06_13_2024_16_06_25_06_13_2024_16_06_25"
    #video_path = 'Data/Video/05-22/BVTEST_MAY_22_0_Subtitled'
    #log_data = single_day_data([1,'05-22','BVTEST'])
    log_data = single_day_data(path=r"C:\Users\mlouki1\Desktop\DATA (D)\Lab Work\Trenholm Lab\Graphs\Pilot_5\Phase 1\06-13\FANNY_SP2_06_13_2024_16_06_25.log")

    #im_to_vid(imFolder_path, video_path)
    add_subtitles(imFolder_path, log_data)

    # im_to_vid(imFolder_path=imFolder_path,vid_path=imFolder_path+'\video')
    #subtitle = 'Here is a very long string of text in order to test how the subtitle is working out. I want to make sure that the line properly splits in two.'
    #write_subtitle('/Users/brune/PycharmProjects/Trenholm_Mice/behavior/Data/Video/05-22/BVTEST_SP2_05_22_2024_15_25_29_05_22_2024_15_25_29_MODIFIED/SUBTITLED_2024-05-22-15-25-52-156290_Frame_1.jpg', subtitle, (155, 135, 12), "No Go")