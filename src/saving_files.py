# For saving user settings
import json
import os   # Because for some reason python can't find the settings file without abspath..

settings_path = os.path.abspath("config\\user_settings.json")

def on_playlist_change(playlist):   # Every time there's a song is added or removed on the playlist, changes this
    with open(settings_path, "w") as f:
        json.dump(playlist, f)  # TODO: Add formating to this method, in order 
                                # to make it more readable for the user wanting to directly edit the .json file
