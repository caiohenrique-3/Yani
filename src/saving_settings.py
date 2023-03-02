# For saving user settings
import json

# For directory functions
import os   

settings_path = os.path.abspath("config/user_settings.json")   # Get's the full path of user_settings

def on_playlist_change(playlist):                               # Called by add_folder, add_file and remove_all
   
        with open(settings_path, "w") as f:                     # Open settings_path with write mode
            playlist_to_dict = OrderedDict()                    # We need to make a dictionary here with the necessary keys 
            for song in playlist:                               # So we can go through every full song path
                playlist_to_dict["playlist"].append(song)       # And add it to our created dictionary, inside the "playlist" key
            
            json.dump(playlist_to_dict, f, indent=2)            # After that, dumps the dictionary to user_settings
                                                                # This way, it keeps everything nice and organized.
                                                                # And opens the possibility to add more keys in the future, for easy config expansion
                                                                                                                           
def do_things_on_exit(value):                   # This function receives a reference to volume_slider as parameter
    with open(settings_path, "r") as f:         # Get's the value inside it and stores in user_settings
        data = json.load(f)                     # So this value can be restored next time the program starts
        data["volume_value"] = value.get()
    f.close()

    with open(settings_path, "w") as f:
        json.dump(data, f, indent=2)
    f.close()

def OrderedDict():                                                           
    my_dict = {"playlist":[], "volume_value": 50}
    return my_dict