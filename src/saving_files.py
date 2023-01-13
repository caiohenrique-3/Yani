# For saving user settings
import json

# For directory functions
import os   

settings_path = os.path.abspath("config\\user_settings.json")   # Get's the full path of user_settings

def on_playlist_change(playlist):                               # Called by add_folder, add_file and remove_all
    with open(settings_path, "w") as f:                         # Open settings_path with write mode
        playlist_to_dict = {"playlist": []}                     # We need to make a dictionary here with the key "playlist"
        for song in playlist:                                   # So we can go through every full song path in our playlist which was passed by function parameter
            playlist_to_dict["playlist"].append(song)           # And add it to our newly created dictionary, under the "playlist" key
        json.dump(playlist_to_dict, f, indent=2)                # After that, saves the newly created dictionary to user_settings
                                                                # This way, it keeps everything nice and organized.
                                                                # And opens the possibility to add more keys in the future, for easy config expansion