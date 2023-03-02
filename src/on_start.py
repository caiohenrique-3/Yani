# For reading the user_settings file
import json

# For doing path related things
import os

# Our ordered json thingy
from saving_settings import OrderedDict

settings_path = "config/user_settings.json"                    

local_playlist_URLs = []                                        # Creates an additional variable here to pass it to main.py because it wasn't changing it there

def on_program_start(playlist_listbox):                         # This function is executed every time the program starts.
    global local_playlist_URLs                                  # It gets all the saved values inside "user_settings.json" and restores them to the last session.
                                                                # Also, if the settings file doesn't exist, creates it with the needed keys and json formatting.

    if os.path.exists(settings_path):                           # If the file exists,
        with open(settings_path, "r+") as f:                    # Opens the settings file with write and read mode
            try:
                temp_list = json.load(f)                            # Stores everything there in our temporary list file
            except:                                                 # It raises an exception when the file exists but it's all blank
                temp_list = OrderedDict()                           # So we need to create a dict with the necessary keys in it
                json.dump(temp_list, f, indent=2)                   # And then dump everything to user_settings

            for item in temp_list["playlist"]:                  # For every item inside our temp list 
                if not os.path.exists(item):                    # If the path leads to a file that doesn't exist, don't add it to our playlist variable
                    print("\n[DEBUG] Invalid item detected in the song paths:", item) # Previous method used to remove the item from temp_list and dump it to our 
                                                                                      # user_settings.json, but it didn't work. So, now, it just skips the invalid item.
                else:                                               
                    local_playlist_URLs.append(item)                                  # If the file exists, just add it to our playlist variable.
            f.close()                                                                 # When finished appending every valid item, close the file. 
    
    else:                                                       # If the settings file doesn't exist,
        temp_list = {"playlist": [], "volume_value": 50}        # Starts our temp_list as a dictionary containing our needed keys
        with open(settings_path, "w+") as f:                    # Creates the settings file with write and read mode
            json.dump(temp_list, f, indent=2)                   # Then dump the temp_list variable inside our json file, so we can proceede without errors.
            f.close()                                           # We don't need to append to the playlist here because the file didn't even used to exist, so, it's empty.
    
    for item in local_playlist_URLs:                                             # Now that it only holds valid paths, we can use it
        song_name, song_extension = os.path.splitext(os.path.basename(item))     # Getting only the song name here
        playlist_listbox.insert("end", song_name)                                # So we can insert at the end of our playlist, without the extension


def get_urls():                                                                  # Function to pass the correct urls to our main.py -> playlist_URLs variable
    global local_playlist_URLs
    return local_playlist_URLs

def get_volume_from_cfg():                                                       # Returns the volume from user_settings.json
    with open(settings_path, "r") as f:
        data = json.load(f)
        f.close()
    return data["volume_value"]