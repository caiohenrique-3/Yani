# For reading the user_settings file
import json

# For doing path related things
import os

settings_path = os.path.abspath("config\\user_settings.json")   # Abspath so python can stop being annoying

local_playlist_URLs = []    # Needed to create an additional variable to pass it to the main file because it wasn't updating when
                            # we exited this file function.

# This function is executed every time the program starts.
# It gets all the saved values from the file "user_settings.json" and sets them on start.

def on_program_start(playlist):
    global local_playlist_URLs

    with open(settings_path, "r") as f:             # Opens the settings file and saves all of it on our playlist_URLs variable
        local_playlist_URLs = json.load(f)               

        for item in local_playlist_URLs: 
            if not os.path.exists(item):            # For every item in our playlist urls, checks if it exists.
                local_playlist_URLs.remove(item)    # If it doesn't, remove it and send a message to the console
                print("[DEBUG] Removed invalid item from the urls:", item)

    for track in local_playlist_URLs:
        if os.path.exists(track): # So, for some reason, the check above didn't really remove the things.. so we need to do it again..
            temp, ext = os.path.splitext(os.path.basename(os.path.abspath(track)))  # Getting just the name of the song here, so we can add it to the listbox in the GUI
            playlist.insert('end', temp)   # Inserts it at the end of the playlist ListBox GUI, using only the name of the song
            
def get_urls(): # Function to pass the correct urls to our main.py - playlist_URLs variable
    global local_playlist_URLs
    return local_playlist_URLs