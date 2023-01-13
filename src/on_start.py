# For reading the user_settings file
import json

# For doing path related things
import os

settings_path = os.path.abspath("config\\user_settings.json")   # Python can't find it without abspath.

local_playlist_URLs = []                            # Needed to create an additional variable to pass it to the main file because it wasn't changing it there

def on_program_start(playlist_listbox):             # This function is executed every time the program starts.
    global local_playlist_URLs                      # It gets all the saved values inside "user_settings.json" and restores them to the last session.

    with open(settings_path, "r+") as f:                        # Opens the settings file with read and write mode
        temp_list = json.load(f)                                # Store everything there in our temporary list file
    
        for item in temp_list["playlist"]:                      # For every item inside our temp list 
            if not os.path.exists(item):                        # If the path leads to a file that doesn't exist, do the proceeding:
                item_index = temp_list["playlist"].index(item)  # Gets the index of the invalid file inside settings and store it in a variable
                del temp_list["playlist"][item_index]           # Goes in our playlist key and search for it's index, and then delete it 
                #TODO: Fix above, it's not deleting the thing actually...
            else:                                               # If the file exists,
                local_playlist_URLs.append(item)                # just add it to the playlist variable.

        f.close()                                               # Closing the file after finished checking everything above
                
        for item in local_playlist_URLs:                                         # Now that it only holds valid paths, we can use it
            song_name, song_extension = os.path.splitext(os.path.basename(item)) # Getting only the song name here
            playlist_listbox.insert("end", song_name)                            # So we can insert at the end of our playlist, without the extension


def get_urls(): # Function to pass the correct urls to our main.py -> playlist_URLs variable
    global local_playlist_URLs
    return local_playlist_URLs