# For GUI
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import customtkinter

# For handling files and directories
import os

# For playing music, doing music things
import pygame.mixer
from mutagen.mp3 import MP3

# For handling customtkinter compatible png files
from PIL import Image

# For updating the music position slider while playing
import threading

# For saving the current playlist and the chosen volume
from saving_settings import on_playlist_change
from saving_settings import do_things_on_exit

# For loading the saved playlist and some other values
from on_start import on_program_start
from on_start import get_urls
from on_start import get_volume_from_cfg

# For handling song names containing dots in their titles. Ex: "Generic Song - Bob ft. Kevin"
from renaming_files import rename_prompt

# For the exit handler
import atexit

# --> CTK variables
customtkinter.set_appearance_mode("Dark")       # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")   # Themes: "blue" (standard), "green", "dark-blue"

# -- > Variables ~ Useful for tracking what is the app state. By doing this we can change label text/color depending on the situation.
is_playing = False
is_paused = False
is_stopped = True

autoplay = True         # Used by the autoplay function

curr_song_name = ""     # Used by the next_song function

song_length = 0         # Need both of these values to correctly update the song position in the GUI
correct_song_pos = 0    # They are used in the update_song_pos and set_song_pos functions.
                        
playlist_URLs = []      # A URL list for the ListBox playlist items - for upgraded ListBox look  

custom_font = "resources/fonts/Poppins-ExtraLight.ttf"

# ----------------------------------------------- # FUNCTIONS - Adding and Removing Files # ----------------------------------------------- #
def load_dir():         # Function to add all files inside a folder to the playlist. Checks all of them for bad characters before adding it.
    global playlist_URLs

    os.chdir(filedialog.askdirectory(title="Select a folder",initialdir="~/Music"))
    tracks = os.listdir()

    for track in tracks:
        if track.endswith(".mp3" or ".wav" or ".ogg" or ".xm" or ".mod"):           # All pygame compatible music formats
            name, ext = os.path.splitext(os.path.basename(os.path.abspath(track)))  # Doing this we get only the name of the song, without the extension
            if name not in playlist.get(0, END):                    # Here, "playlist" refers to the one that is present in the GUI.
                if '.' not in name:                                 # Files with dots in their names makes the program shit itself
                    playlist_URLs.append(os.path.abspath(track))    # Gets the full path and stores it in our list (this is not the GUI one)
                    playlist.insert(END,name)                       # Adds the song to our playlist ListBox (this is the GUI one).
                    on_playlist_change(playlist_URLs)               # Save every song path to user_settings.json
                else:
                    track = rename_prompt(track)                    # This function will prompt the user to rename the file, and, if renamed, return the new name          
                    
                    if track != None:                                    # "None" is the return value when the user rejects the rename prompt 
                        track_without_ext, ext = os.path.splitext(track) # The extension dot count as a bad char, so split it from the name
                        playlist_URLs.append(os.path.abspath(track))     # Adds the full song path to our list. 
                        playlist.insert(END, track_without_ext)          # Adds only the song title to our ListBox in the GUI. 
                        on_playlist_change(playlist_URLs)                # Saving the song paths to user_settings.json
                        

def load_file():        # Function to add a single file to the playlist. Checks the file for bad characters before adding it.
    global playlist
    global playlist_URLs

    track = filedialog.askopenfilename(title="Select a song",filetypes=[("MP3", ".mp3"),   
                                        ("OGG", ".ogg"), ("XM", ".xm"), ("MOD", ".mod"), ("WAV", ".wav")], initialdir="~/Music")

    os.chdir(os.path.dirname(track))  # Gets the name of the folder and changes the current working folder to it. The rename_function needs it to find the song later
    name, ext = os.path.splitext(os.path.basename(os.path.abspath(track)))  # Getting only the name of the song here, without the extension

    if name not in playlist.get(0, END):                    # If the song isn't a duplicate
        if '.' not in name:                                 # If there's no characters that break the program
            playlist_URLs.append(os.path.abspath(track))    # Add the full song path to our list
            playlist.insert(END, name)                      # Adds only the name of the song to our listbox in the GUI
            on_playlist_change(playlist_URLs)               # Saves all song paths to user_settings.json
        else:
            track = rename_prompt(track)                    # This function will prompt the user to rename the file and return either "None" or the new filename

            if track != None:                                    # "None" is the return value when the user rejects the rename prompt
                track_without_ext, ext = os.path.splitext(os.path.basename(track)) # The extension dot count as a bad char, so split it from the name
                playlist_URLs.append(os.path.abspath(track))     # Adds the full song path to our list. 
                playlist.insert(END,track_without_ext)           # Adds only the song title, without extension, to our ListBox in the GUI. 
                on_playlist_change(playlist_URLs)                # Saving the paths to user_settings.json
                        
def remove_all():    # Function to delete all items inside the playlist. Also stops whatever song is playing.
    global playlist_URLs

    playlist.delete(0,END)                            # Deleting everything in our ListBox in the GUI
    playlist_URLs = []                                # Deleting all full song paths in our list

    stop_song()                                       # Does the necessary things to stop the song and update our GUI labels and button texts.                
    on_playlist_change(playlist_URLs)                 # Updating user_settings.json

def remove_single(): # Function to delete a single item inside the playlist. This one doesn't stop the song playing, unless it's the one that got deleted.
    global playlist_URLs

    for song in playlist_URLs:                                      # For every song in our song paths
        track, ext = os.path.splitext(os.path.basename(song))       # Get's only the name, without extension
        if track == playlist.get(ACTIVE):                           # Compares to see if it's the same as the current selection
            if track == current_song.get():                         # If the song selected is the same one that is playing, 
                stop_song()                                         # Stop it first
                                                               
    playlist.delete(playlist.curselection(), playlist.curselection())   # Then delete it from our GUI
    playlist_URLs.remove(song)                                          # Delete it from our song paths
    on_playlist_change(playlist_URLs)                                   # Save the changes to the json file
    
# ----------------------------------------------- # FUNCTIONS - Music Controls # ----------------------------------------------- #
def play_song():            
    global playlist_URLs
    global curr_song_name
    global song_length
    global correct_song_pos

    if is_playing == True:  # If the song is playing, clicking the button "Play" (which actually now displays "Pause") again will pause it.
        pause_song()
    elif is_paused == True: # If the song is paused, clicking the button "Play" (which actually now displays "Resume") again will resume it.
        resume_song()
    else:
        try:
            song_name, ext = os.path.splitext(os.path.basename(playlist.get(ACTIVE)))  # Doing this to only get the name of the song, without the extension

            full_song_path = ""   # We need the full song path here to be able to find it inside playlist_URLs using its index() function, which only accepts
                                  # full song paths.

            for track in playlist_URLs:     # Going through every item in playlist_URLs. Remember that "track" holds the FULL path - > os.path.abspath
                temp_name, ext = os.path.splitext(os.path.basename(track))     # Sets a temp variable to hold only the name of the song, without extension    
                if temp_name == song_name:  # Comparing the temp variable with our song_name variable, checking if both are the same
                    full_song_path = track  # If true, stores the full path of the song in a variable
                
            pygame.mixer.music.load(full_song_path) # And finally play it here.
            update_song_details(full_song_path)     # Updates both GUI elements and variables related to the song position.

        except Exception as e:  
            print(e)
        
        else:                                       # This block of code runs if no exceptions has ocurred
            correct_song_pos = 0                    # Because this is a new song, we need to set this value to the default state (unchanged)
                                                    # So we can display the correct position in the update_song_pos function.
            pygame.mixer.music.play()               

            current_song.set(song_name)   # Updates "actual_song_lbl"
            curr_song_name = song_name    # I need this in order to the next_song function to work. current_song.get() doesn't return a valid value to it.
            status.set("Playing")         # Updates "status_label"
            boolean_switch("play")        # Sets - > is_playing = True and everything else to False.
            play_button_check()           # Checks the boolean variables and changes the text of the "Play/Pause" button.
            song_has_ended_check()        # Checks every second if the song has ended
            playlist.selection_clear(0, END) # Stops the selection of the song we just started to play
            try:
                x = threading.Thread(target=update_song_pos, daemon=True)   # If it isn't already running,
                x.start()                                                   # Start another thread which will update our slider position.
            except Exception as e:
                print("\n[DEBUG]", e)

def pause_song():
    pygame.mixer.music.pause()
    status.set("Paused")        # Updates "status_label"
    boolean_switch("pause")     # Sets - > is_paused = True and everything else to False.
    play_button_check()         # Checks the boolean variables and changes the text of the "Play/Pause" button.

def resume_song():
    pygame.mixer.music.unpause()    
    status.set("Playing")       # Updates "status_label"
    boolean_switch("play")      # Sets - > is_playing = True and everything else to False.
    play_button_check()         # Checks the boolean variables and changes the text of the "Play/Pause" button.

def stop_song():
    global curr_song_name

    pygame.mixer.music.stop()
    status.set("Stopped")                   # Updates "status_label"
    current_song.set("")                    # Updates "actual_song_lbl"
    curr_song_name = ""                     # Resetting the variable used by next_song() function.
    song_curr_pos.configure(text="0:00:00") # Resetting the GUI
    song_end_pos.configure(text="0:00:00")  # Resetting the GUI
    music_pos_slider.set(0)                 # Resetting the GUI
    boolean_switch("stop")                  # Sets - > is_stopped = True and everything else to False.
    play_button_check()                     # Checks the boolean variables and changes the text of the "Play/Pause" button.

def previous_song():
    global playlist_URLs
    global curr_song_name

    for track in playlist_URLs:                                             # Goes through every song in our song paths
        track_name, ext = os.path.splitext(os.path.basename(track))         # Get's only the name of the song, without the extension
        if track_name == current_song.get():                                # If the song name matches the current one that is playing / active
            prev_song_index = (playlist_URLs.index(track) - 1)              # playlist_URLs only holds the abspaths, that's why we use track variable here
            break

    track_name, ext = os.path.splitext(os.path.basename(playlist_URLs[prev_song_index]))    # Getting only the song name here, without extension
    
    current_song.set(track_name)       # Updates "actual_song_lbl"
    curr_song_name = track_name        # Used by function next_song. Removing this line causes bugs                                                              

    pygame.mixer.music.load(playlist_URLs[prev_song_index])         
    pygame.mixer.music.play()
    
    update_song_details(playlist_URLs[prev_song_index]) # Updates both GUI elements and variables related to the song position slider.
    
    status.set("Playing")          # Updates "status_label"
    boolean_switch("play")         # Sets - > is_playing = True and everything else to False.
    play_button_check()            # Checks the boolean variables and changes the text of the "Play/Pause" button.
    song_has_ended_check()         # Checks every second if the song has ended
    
def next_song():
    global playlist_URLs
    global curr_song_name

    for track in playlist_URLs:                                         # Goes through every song in our song paths
        track_name, ext = os.path.splitext(os.path.basename(track))     # Get's only the name of the song, without the extension
        if track_name == curr_song_name:                                # If the song name matches the current one that is playing / active
            next_song_index = (playlist_URLs.index(track) + 1)          # playlist_URLs only holds the abspaths, that's why we use track variable here
            break
                                                                       
    try:
        playlist_URLs[next_song_index]                          # Checking if the next song exists. If it doesn't that means we are at the end of our playlist.
    except IndexError:
        next_song_index = 0                                     # So we need to go back and play the first song again

    track_name, ext = os.path.splitext(os.path.basename(playlist_URLs[next_song_index]))  # Getting only the song name here, without extension
            
    current_song.set(track_name)                                                          # Updates "actual_song_lbl"
    curr_song_name = track_name 
                
    pygame.mixer.music.load(playlist_URLs[next_song_index])     
    pygame.mixer.music.play()

    update_song_details(playlist_URLs[next_song_index])   # Updates both GUI elements and variables related to the song position slider.
    
    status.set("Playing")            # Updates "status_label"
    boolean_switch("play")           # Sets - > is_playing = True and everything else to False.
    play_button_check()              # Checks the boolean variables and changes the text of the "Play/Pause" button.
    song_has_ended_check()           # Checks every second if the song has ended

def play_event_doubleclick(event):   # Function to make the song start playing if the item is double-clicked in the ListBox.
    boolean_switch("stop")           # Sets - > is_stopped = True and everything else to False...
    play_song()                      # ...so we can pass this function first checks
    playlist.selection_clear(0, END) # Finished doing everything above, unselects the item

def song_has_ended_check():      # Function that checks if the song has ended, and, if autoplay is true, plays the next song.
    for event in pygame.event.get():
        if event.type == MUSIC_END and autoplay == False:  # If the music ends,
            stop_song()                                    # Updates our GUI labels and buttons

        elif event.type == MUSIC_END and autoplay == True and is_stopped == False:  # If the music ends, auto starts the next item in the playlist.
            next_song()                                                             # Removing "is_stopped == False" will cause a song 
                                                                                    # to start every time the "Stop" button is pressed.
    window.after(1000, song_has_ended_check)                                        # Repeat this function every 1 second

# ----------------------------------------------- # FUNCTIONS - GUI event handlers # ----------------------------------------------- #
def update_volume(event):                               # Function to change the volume according to our volume slider in the GUI                                                   
    pygame.mixer.music.set_volume(volume_slider.get())  # First gets the current value inside our tkinter slider then pass it to the pygame music volume function
    
    if volume_slider.get() == 0:                        # If the volume slider value is 0
        volume_image.configure(image=volume_muted_png)  # Changes the volume image to the muted version
    else:
        volume_image.configure(image=volume_png)        # Resetting it to the default image
    
def update_song_pos():        # Function to  update the slider position in the GUI according to our current song position.
    global correct_song_pos   # Had to do a workaround because pygame get_pos() only represents how long the music has been playing; 
                              # it does not take into account any starting position offsets. So, if the user changes it, get_pos stops working.
    
    if is_paused or is_stopped:     # If the music is paused or stopped, doesn't update the slider.
        pass
    else:
        if correct_song_pos == 0:   # If the correct song pos value isn't 0, this means the user changed the song position in the slider
                                    
            music_pos_slider.set(pygame.mixer.music.get_pos() / 1000)           # Updating the slider according to the music current position

            converted_to_time = convert(pygame.mixer.music.get_pos() / 1000)    # Converting this other thing to "hours : minutes : seconds"
            
            song_curr_pos.configure(text=converted_to_time)                     # Updating the GUI
            
        else:
            music_pos_slider.set(correct_song_pos)                # Setting the slider position according to correct_song_pos (it holds a value in seconds)
            
            converted_to_time = convert(correct_song_pos)         # Converting seconds to "hours : minutes : seconds"
            
            song_curr_pos.configure(text=converted_to_time)       # Updating our GUI  
            
            correct_song_pos += 1.0     # Still trying to figure out this thing here... very broken still.           

    window.after(1000, update_song_pos)          # Repeating everything above every 1 second.

def set_song_pos(event):                         # Function to handle the event when the user clicks the slider
    global music_pos_slider                      # Changes the music position to the slider position that was clicked by the user
    global song_curr_pos                         # WARNING: This will desync the slider, making it go either faster or slower than the actual music.
    global correct_song_pos                    

    correct_song_pos = music_pos_slider.get()           # correct_song_pos is the global variable, needed for the update_song_pos function.

    pygame.mixer.music.set_pos(correct_song_pos)        # Changes the music position to the one we just got from the slider
    
    converted_to_time = convert(correct_song_pos)       # Converting the seconds to "hours : minutes : seconds"
    
    song_curr_pos.configure(text=converted_to_time)     # Updating our GUI

def update_song_details(song_path):  # Calls this function every time a new song comes in, updates some GUI elements and other variables too.
    global correct_song_pos
    global song_length

    correct_song_pos = 0                                   # Since this is a new song, resets the song position
    song = MP3(song_path)                                  # Starts a mutagen thingy with our song
    song_length = song.info.length                         # Get's the song length using mutagen
    song_end_pos.configure(text=convert(song_length))      # Convert the value to "hours : minutes : seconds" and update our GUI with it
    music_pos_slider.configure(from_= 0, to=song_length, number_of_steps = song_length)
    music_pos_slider.set(0)

def search_songs(event):         # Function to check the entry search bar vs all ListBox items, and show only what matches
    global playlist_URLs

    typed = song_search.get()    # Gets what we typed into the entrybox

    if typed == '':                     # If we deleted everything we typed
        playlist.delete(0, END)         # Deletes whole playlist so we can re-add the items in the correct order it was
        for track in playlist_URLs:     # For every full song path
            name, ext = os.path.splitext(os.path.basename(track))   # Gets only the song name, without the extension
            playlist.insert(END, name)                              # And inserts it into our ListBox in the GUI
    else:
        playlist.delete(0, END)                                     # Reseting the playlist so we can display only what matters
        for track in playlist_URLs:                                 # Going through every song full path
            name, ext = os.path.splitext(os.path.basename(track))   # Getting only the name of the song, without the extension
            if typed.lower() in track.lower():                      # Checks if whats typed matches an item inside the playlist_URLs
                playlist.insert(END, name)                          # If true, display it in our ListBox

def play_button_check():    # Depending on the state of the bool variables, changes the play button label text.
    if is_playing == True:                          # If a song is playing, 
        play_button.configure(text="Pause")         # Changes the button from "Play" to "Pause"
        status_label.configure(text_color="#6dd867")
        window.update()
    elif is_paused == True:                         # If a song is paused, 
        play_button.configure(text="Resume")        # Changes the button from "Pause" to "Resume"
        status_label.configure(text_color="yellow")
        window.update()
    elif is_stopped == True:                        # If a song is stopped, 
        play_button.configure(text="Play")          # Changes the button to "Play"
        status_label.configure(text_color="red")
        window.update()

def boolean_switch(input):                  # Function that sets the main booleans to True or False depending on the input parameter.
    global is_playing
    global is_paused
    global is_stopped

    if input == "play":
        is_paused = False
        is_stopped = False
        is_playing = True

    elif input == "pause":
        is_playing = False
        is_stopped = False
        is_paused = True

    elif input == "stop":
        is_playing = False
        is_paused = False
        is_stopped = True
    
    else: 
        print("[DEBUG] Error in boolean_switch function: Invalid input.")

def convert(seconds):                       # Function that converts an input (in seconds) to "hours : minutes : seconds"
    seconds = seconds % (24 * 3600)
    hour = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60
    
    return "%d:%02d:%02d" % (hour, minutes, seconds)

# ------------------------------------------------------------- # SETTING UP VARIABLES # -------------------------------------------------------------#
window = customtkinter.CTk()
window.geometry("1100x540") 
window.resizable(width=False,height=False)
window.title("Yani")
window.iconphoto(False, PhotoImage(file="resources/images/yani-logo.png"))

pygame.init()                                           # Need this in order to be able catch pygame events
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)
MUSIC_END = pygame.USEREVENT+1                          # Thingy for checking the end of a song
pygame.mixer.music.set_endevent(MUSIC_END)

current_song = StringVar(window, value="")     # Used by our tkinter gui element named "actual_song_lbl"   > Shows the name of the current song being played.
status = StringVar(window, "Stopped")          # Used by our tkinter gui element named "status_label"      > Playing | Paused | Stopped

logo_img = customtkinter.CTkImage(dark_image=Image.open("resources/images/yani-logo.png"),size=(40,40))
volume_png = customtkinter.CTkImage(dark_image=Image.open("resources/images/volume.png"), size=(30,30))
volume_muted_png = customtkinter.CTkImage(dark_image=Image.open("resources/images/volume-mute.png"), size=(30,30))

# ------------------------------------------------------------- # CREATING THE GUI WIDGETS # -------------------------------------------------------------#
frame_1 = customtkinter.CTkFrame(window, width=300,height=485)                      # Home for all of our music control buttons
frame_2 = customtkinter.CTkFrame(window, width=770,height=440,fg_color="#282828")   # Home for searchbar and playlist
frame_3 = customtkinter.CTkFrame(window, width=770, height=30)                      # Home for our "Currently PLaying" label
frame_4 = customtkinter.CTkFrame(window, width=300,height=30)                       # Home for our "State" label
frame_5 = customtkinter.CTkFrame(window, width=770,height=40)                       # Home for the song pos sliders

# FROM FRAME 1 --->
play_button = customtkinter.CTkButton(frame_1,text="Play",width=65,font=(custom_font,12),command=play_song, 
fg_color="#2b23af", hover_color="#2b23af")     
stop_button = customtkinter.CTkButton(frame_1,text="Stop",width=65,font=(custom_font,12),command=stop_song, 
fg_color="#2b23af", hover_color="#2b23af")
separator_1 = ttk.Separator(frame_1,orient=VERTICAL)

previous_button = customtkinter.CTkButton(frame_1,text="Previous", width=65,font=(custom_font, 12),command=previous_song, 
fg_color="#2b23af", hover_color="#2b23af")
next_button = customtkinter.CTkButton(frame_1,text="Next",width=65, font=(custom_font, 12), command=next_song, 
fg_color="#2b23af", hover_color="#2b23af")     
separator_2 = ttk.Separator(frame_1,orient=HORIZONTAL)

volume_image = customtkinter.CTkLabel(frame_1,image=volume_png,text="")
volume_slider = customtkinter.CTkSlider(frame_1, from_=0.0,to=1.0,orientation=HORIZONTAL,state="normal",width=250,command=update_volume,
fg_color="#9e9db0", progress_color="#e3e1f5", button_color="#2b23af", button_hover_color="#2b23af")
separator_3 = ttk.Separator(frame_1,orient=HORIZONTAL)

add_folder_button = customtkinter.CTkButton(frame_1,text="Add a directory",width=140,font=(custom_font,12),command=load_dir, 
fg_color="#2b23af", hover_color="#2b23af")
add_file_button = customtkinter.CTkButton(frame_1,text="Add a single file",width=140,font=(custom_font,12),command=load_file, 
fg_color="#2b23af", hover_color="#2b23af")
remove_all_button = customtkinter.CTkButton(frame_1,text="Remove All Songs",width=140,font=(custom_font,12),hover_color="red",command=remove_all, 
fg_color="#2b23af")
remove_single_button = customtkinter.CTkButton(frame_1,text="Remove A Single Song",width=140,font=(custom_font,12),hover_color="red",command=remove_single, 
fg_color="#2b23af") 
separator_4 = ttk.Separator(frame_1,orient=HORIZONTAL)

separator_5 = ttk.Separator(frame_1,orient=HORIZONTAL)
app_logo = customtkinter.CTkLabel(frame_1,text="",image=logo_img)
yani_label = customtkinter.CTkLabel(frame_1,text="Yani Music Player",font=("Courier New",19),text_color="#6dd867",compound="left")

# FROM FRAME 2 --->
song_search = customtkinter.CTkEntry(frame_2,placeholder_text="Search for a song",width=365,corner_radius=1,font=(custom_font, 11))

playlist = Listbox(frame_2, font=(custom_font, 13),width=300,height=400,background="#282828",highlightcolor="#3c3d45",selectbackground="#026345",
highlightthickness=0, borderwidth=0, selectborderwidth=0, activestyle="none", relief="sunken", fg="white")
playlist_scroll_bar = customtkinter.CTkScrollbar(playlist,orientation=VERTICAL)
playlist.configure(yscrollcommand=playlist_scroll_bar.set)
playlist_scroll_bar.configure(command=playlist.yview)

# FROM FRAME 3 --->            
current_song_label = customtkinter.CTkLabel(frame_3, text="CURRENTLY PLAYING:",font=("Rubik",12))
actual_song_lbl = customtkinter.CTkLabel(frame_3, textvariable=current_song,font=("Rubik", 12),text_color="#6dd867")

# FROM FRAME 4 --->
status_label = customtkinter.CTkLabel(frame_4,textvariable=status,font=(custom_font,15),text_color="red")

# FROM FRAME 5 --->
song_curr_pos = customtkinter.CTkLabel(frame_5, text="0:00:00",font=("Rubik", 12))
separator_6 = customtkinter.CTkLabel(frame_5, text="/", font=("Rubik", 12))
song_end_pos = customtkinter.CTkLabel(frame_5, text="0:00:00", font=("Rubik", 12))
music_pos_slider = customtkinter.CTkSlider(frame_5, from_=0, to=1000, orientation=HORIZONTAL,state="normal",width=620,height=15,command=set_song_pos,
fg_color="#e3e1f5", progress_color="#9e9db0", button_color="#2b23af", button_hover_color="#2b23af")

# ----------------------------------------------- # FUNCTIONS - GUI event handlers part 2 # ----------------------------------------------- #
song_search.bind("<KeyRelease>",search_songs)               # When a key is pressed and released, search the song that matches what's been typed
playlist.bind("<Double-Button-1>", play_event_doubleclick)  # Double clicking an item in the ListBox will start to play it

# ------------------------------------------------------------- # PACKING EVERYTHING # -------------------------------------------------------------#
# FROM FRAME 1 --->                               # Home for all of our music control buttons
frame_1.pack_propagate(False)                 
frame_1.place(x=10,y=50)                        
play_button.place(x=5,y=5)                        # displays - > "Play", "Pause" and "Resume" 
stop_button.place(x=75,y=5)                       # displays - > "Stop"
separator_1.place(x=150,y=5,width=1,height=30)    # displays - > A vertical line that separates elements

previous_button.place(x=160,y=5)                  # displays - > "Previous"
next_button.place(x=230,y=5)                      # displays - > "Next"
separator_2.place(x=0,y=40,width=300,height=1)    # displays - > A horizontal line that separates elements

volume_image.place(x=10,y=65)                     # displays - > An image for the volume slider
volume_slider.place(x=45,y=70)                    # displays - > A slider for changing the music volume
separator_3.place(x=0,y=120,width=300,height=1)

add_folder_button.place(x=5,y=130)                # displays - > "Add a directory"
add_file_button.place(x=5,y=165)                  # displays - > "Add a single file"
remove_all_button.place(x=155,y=130)              # displays - > "Remove All Songs"
remove_single_button.place(x=155,y=165)           # displays - > "Remove A Single Song"
separator_4.place(x=0,y=205,width=300,height=1)   # displays - > A horizontal line that separates elements

separator_5.place(x=0,y=430,width=300,height=1)   # displays - > A horizontal line that separates elements
app_logo.place(x=20,y=440)                        # displays - > An image of the app's logo
yani_label.place(x=80,y=450)                      # displays - > "Yani Music Player"

# FROM FRAME 2 --->                               # Home for searchbar and playlist
frame_2.pack_propagate(False)                                            
frame_2.place(x=320,y=95)                                                                                                                                 
song_search.pack(padx=0,fill=BOTH)                # displays - > "Search for a song"                                                                        
playlist.pack(fill=BOTH,expand=TRUE, padx=10,     # displays - > A ListBox which shows all our added songs 
pady=10) 
playlist_scroll_bar.pack(side=RIGHT,fill=BOTH)    # displays - > The scroll bar on the right of our ListBox                                                                                                         

# FROM FRAME 3 --->                               # Home for our "Currently PLaying" label                                                                                   
frame_3.pack_propagate(False)                                                             
frame_3.place(x=320,y=10)                                                                         
current_song_label.pack(anchor=W,padx=5)          # displays - > "CURRENTLY PLAYING:"             
actual_song_lbl.place(x=135,y=0)                  # displays - > "ex: Generic Song - Bob ft Kevin"

# FROM FRAME 4 --->                               # Home for our "State" label                                                                                                                                                                                                                                                                              
frame_4.pack_propagate(False)                                                                                    
frame_4.place(x=10,y=10)                                                                                         
status_label.place(x=120)                         # displays - > "Playing", "Paused", "Stopped"        

# FROM FRAME 5 --->                               # Home for the song pos sliders                                                                               
frame_5.pack_propagate(False)
frame_5.place(x=320,y=50)
song_curr_pos.place(x=10,y=5)                     # displays - > 0:00:00
separator_6.place(x=60,y=5)                       # displays - > A char "/" to separate elements.
song_end_pos.place(x=70,y=5)                      # displays - > 0:00:00
music_pos_slider.place(x=140, y=12)               # displays - > A slider for changing the music position
music_pos_slider.set(0)                        

# ----------------------------------------------- # FUNCTIONS - Setting up things on the start # ----------------------------------------------- #
on_program_start(playlist)  # This function will update ONLY the "playlist" variable - the one who holds control over the ListBox.
playlist_URLs = get_urls()  # This one will get the updated paths from the other file to this one. Couldn't manage to do it in the above function
pygame.mixer.music.set_volume(get_volume_from_cfg())    # Getting the user stored volume from the json file
volume_slider.set(pygame.mixer.music.get_volume())      # Syncing the volume slider with this volume

# Doing things when the program exits the normal way
atexit.register(do_things_on_exit, volume_slider)

# The End
window.update()
window.mainloop()