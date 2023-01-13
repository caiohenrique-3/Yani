# For GUI
from tkinter import messagebox

# For renaming files
import os

# When i was testing i noticed songs titles with dots in their names like 'ft.' or '.ft' breaks everything..
# So i made this function to handle the error

bad_chars = ['.']

def rename_prompt(song_file): # Since the cwd has been changed in the load_dir/load_file function, we don't need the full path to find the song.
    rename = messagebox.askyesno(title=os.path.basename(song_file), 
    message="Unfortunately, this program doesn't run files with dots in their names. Would you like to rename the file in order to run it?")
    
    if rename:
        print("\n[DEBUG] Input:", song_file)          

        song_name, song_extension = os.path.splitext(song_file) # Spliting the file name from it's extension, because the dot will count as a bad char

        for i in bad_chars:
            new_song_file = song_name.replace(i, '')        # Deleting all the bad chars
        
        new_song_file = new_song_file + song_extension      # Adding the extension at the end of our clean song name
        os.rename(song_file, new_song_file)                 # Renaming the old file with the new one. SOURCE / DESTINATION
      
        print("\n[DEBUG] Output:", new_song_file)

        return new_song_file    # Returning the new song name so our function outside can know what is the file name now
    
    else:
        return None             # Returning None so our function outside can handle it
        