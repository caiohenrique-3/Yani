# For GUI
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import customtkinter

# For handling files and directories
import os

# For playing music
import pygame.mixer

# For handling customtkinter compatible png files
from PIL import Image

# For saving the current playlist and the chosen volume
from saving_settings import on_playlist_change

# For loading the saved playlist and some other values
from on_start import on_program_start
from on_start import get_urls

# For handling song names containing dots in their titles. Ex: "Generic Song - Bob ft. Kevin"
from renaming_files import rename_prompt

# --> CTK variables
customtkinter.set_appearance_mode("Dark")       # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")   # Themes: "blue" (standard), "green", "dark-blue"

# -- > Variables ~ Useful for tracking what is the app state. By doing this we can change label text/color depending on the situation.
is_playing = False
is_paused = False
is_stopped = True
autoplay = True

playlist_URLs = []      # A URL list for the ListBox playlist items - for upgraded ListBox look  
                                                    
# ----------------------------------------------- # FUNCTIONS - Adding and Removing Files # ----------------------------------------------- #
def load_dir():         # Function to add all files inside a folder to the playlist. Checks all of them for bad characters before adding it.
    global playlist
    global playlist_URLs

    os.chdir(filedialog.askdirectory(title="Select a folder",initialdir="~\Music"))
    tracks = os.listdir()

    for track in tracks:
        if track.endswith(".mp3" or ".wav" or ".ogg" or ".xm" or ".mod"):           # All pygame compatible music formats
            temp, ext = os.path.splitext(os.path.basename(os.path.abspath(track)))  # Doing this we get only the name of the song, without the extension
            if temp not in playlist.get(0, END):                    # Need to check the temp variable because we just store the song name inside the playlist ListBox.
                if '.' not in temp:                                 # Files with dots in their names makes the program shit itself
                    playlist_URLs.append(os.path.abspath(track))    # Gets the full path and stores it in our list
                    playlist.insert(END,temp)                       # Adds "temp", which is the song name, to the end of our playlist ListBox.
                    on_playlist_change(playlist_URLs)               # Save all paths to file user_settings.json
                else:
                    track = rename_prompt(track)                    # This function will prompt the user to rename the file, and, if renamed, return the new name          
                    
                    if track != None:                                    # "None" is the return value when the user rejects the rename prompt 
                        track_without_ext, ext = os.path.splitext(track) # The extension dot count as a bad char, so split it from the name
                        playlist_URLs.append(os.path.abspath(track))     # Adds the full song path to our list. 
                        playlist.insert(END, track_without_ext)          # Adds only the song title, without extension, to our ListBox in the GUI. 
                        on_playlist_change(playlist_URLs)                # Saving the paths to user_settings.json
                        

def load_file():        # Function to add a single file to the playlist. Checks the file for bad characters before adding it.
    global playlist
    global playlist_URLs

    track = filedialog.askopenfilename(title="Select a song",filetypes=[("MP3", ".mp3"),   
                                        ("OGG", ".ogg"), ("XM", ".xm"), ("MOD", ".mod"), ("WAV", ".wav")], initialdir="~\Music")

    os.chdir(os.path.dirname(track))  # Gets the name of the folder and changes the current working folder to it. The rename_function needs it to find the song later
    temp, ext = os.path.splitext(os.path.basename(os.path.abspath(track)))  # Getting only the name of the song here, without the extension

    if temp not in playlist.get(0, END):                    # Need to check temp because inside the ListBox there's only the song names, without extensions
        if '.' not in temp:                                 # If there's no characters that break the program
            playlist_URLs.append(os.path.abspath(track))    # Add the full song path to our list
            playlist.insert(END, temp)                      # Adds only the name of the song, without extension.
            on_playlist_change(playlist_URLs)               # Saves all paths to file user_settings.json
        else:
            track = rename_prompt(track)                    # This function will prompt the user to rename the file and return either "None" or the new filename

            if track != None:                                    # "None" is the return value when the user rejects the rename prompt
                track_without_ext, ext = os.path.splitext(os.path.basename(track)) # The extension dot count as a bad char, so split it from the name
                playlist_URLs.append(os.path.abspath(track))     # Adds the full song path to our list. 
                playlist.insert(END,track_without_ext)           # Adds only the song title, without extension, to our ListBox in the GUI. 
                on_playlist_change(playlist_URLs)                # Saving the paths to user_settings.json
                        
def remove_all():   # Function to delete all items inside the playlist. Also stops whatever song is playing.
    global playlist
    global playlist_URLs

    playlist.delete(0,END)                            # Deleting everything in our ListBox in the GUI
    playlist_URLs = []                                # Deleting all full song paths in our list

    stop_song()                       # Does the necessary things to stop the song and update our GUI labels and button texts.                
    on_playlist_change(playlist_URLs) # Saving the paths to user_settings.json

# ----------------------------------------------- # FUNCTIONS - Music Controls # ----------------------------------------------- #
def play_song():            
    global current_song
    global playlist
    global status
    global is_playing
    global is_paused
    global is_stopped
    global autoplay
    global playlist_URLs
    
    if is_playing == True:  # If the song is playing, clicking the button "Play" (which actually now displays "Pause") again will pause it.
        pause_song()
    elif is_paused == True: # If the song is paused, clicking the button "Play" (which actually now displays "Play") again will resume it.
        resume_song()
    else:
        try:
            song_name, ext = os.path.splitext(os.path.basename(playlist.get(ACTIVE)))  # Doing this to only get the name of the song, without the extension

            full_song_path = ""   # We need the full song path here to be able to find it inside playlist_URLs using its index() function, which only accepts
                                  # full song paths.

            for track in playlist_URLs:     # Going through every item in playlist_URLs. Remember here that "track" holds the FULL path - > os.path.abspath
                temp_name, ext = os.path.splitext(os.path.basename(track))     # Sets a temp variable to hold only the name of the song, without extension    
                if temp_name == song_name:  # Comparing the temp variable with our song_name variable, checking if both are the same
                    full_song_path = track  # If true, stores the full path of the song in a variable
                    
            pygame.mixer.music.load(full_song_path) # And finally play it here.
            
        except Exception as e:  
            print(e)
        
        else:                             # This block of code runs if no exceptions has ocurred
            pygame.mixer.music.play()
            current_song.set(song_name)   # Updates "actual_song_lbl"
            status.set("Playing")         # Updates "status_label"
            boolean_switch("play")        # Sets - > is_playing = True and everything else to False.
            play_button_check()           # Checks the boolean variables and changes the text of the "Play/Pause" button.
            status_color_check()          # Checks the boolean variables and changes the color of the status label.
            song_has_ended_check()        # Checks every second if the song has ended

def pause_song():
    global status

    pygame.mixer.music.pause()
    status.set("Paused")        # Updates "status_label"
    boolean_switch("pause")     # Sets - > is_paused = True and everything else to False.
    status_color_check()        # Checks the boolean variables and changes the color of the status label.
    play_button_check()         # Checks the boolean variables and changes the text of the "Play/Pause" button.

def resume_song():
    global status

    pygame.mixer.music.unpause()
    status.set("Playing")       # Updates "status_label"
    boolean_switch("play")      # Sets - > is_playing = True and everything else to False.
    status_color_check()        # Checks the boolean variables and changes the color of the status label.
    play_button_check()         # Checks the boolean variables and changes the text of the "Play/Pause" button.

def stop_song():
    global status
    global current_song

    pygame.mixer.music.stop()
    status.set("Stopped")           # Updates "status_label"
    current_song.set("<unknown>")   # Updates "actual_song_lbl"
    boolean_switch("stop")          # Sets - > is_stopped = True and everything else to False.
    status_color_check()            # Checks the boolean variables and changes the color of the status label.
    play_button_check()             # Checks the boolean variables and changes the text of the "Play/Pause" button.
    
def play_event_doubleclick(event):  # Function to make the song start playing if the item is double-clicked in the ListBox.
    boolean_switch("stop")          # Sets - > is_stopped = True and everything else to False...
    play_song()                     # ...so we can pass this function first checks 

def autoplay_next_song():        # Basically the play_event function, but built for the song_has_ended_check function
    global current_song          # When a song ends, a new one plays with this, if autoplay is enabled. 
    global status                #TODO: Fix songs added after you press play not triggering the autoplay 
    global playlist              
    global playlist_URLs
    
    keep_going = False          # While the next element of the playlist isn't null, keeps autoplaying.

    try:
        playlist_URLs[playlist.curselection()[0] + 1]   # Checking if the next element exists
    except IndexError:                                  # If it doesn't exist, it will throw an exception
        keep_going = False                              # So, set our boolean to False
        stop_song()                                     # And call stop_song to stop the music and update the GUI labels and buttons
    else:
        keep_going = True                               # If there's no exception, it means that the item exist and we can procede

    if keep_going:
        name, ext = os.path.splitext(os.path.basename(playlist_URLs[playlist.curselection()[0] + 1]))  # First gets the current item selected, insert +1 to get the next item
                                                                                                       # Then get its basename, and splits the name from the extension
        current_song.set(name)      # Updates "actual_song_lbl"
            
        pygame.mixer.music.load(playlist_URLs[playlist.curselection()[0] + 1]) 
        #                                playlist.curselection()[0] + 1 
        # This method returns a list of items selected in the playlist, so it needs to choose the index + 1 (next item) to load the correct thing.
            
        pygame.mixer.music.play()
        status.set("Playing")    # Updates "status_label"
        boolean_switch("play")   # Sets - > is_playing = True and everything else to False.
        play_button_check()      # Checks the boolean variables and changes the text of the "Play/Pause" button.
        status_color_check()     # Checks the boolean variables and changes the color of the status label.
        song_has_ended_check()   # Checks every second if the song has ended

def song_has_ended_check():      # Function that checks if the song has ended, and, if autoplay is true, calls the autoplay function.
    global current_song
    global playlist
    global status

    for event in pygame.event.get():
        if event.type == MUSIC_END and autoplay == False:  # If the music ends,
            stop_song()                                    # Updates our GUI labels and buttons

        elif event.type == MUSIC_END and autoplay == True and is_stopped == False:  # If the music ends, auto starts the next item in the playlist.
            autoplay_next_song()                                                    # Removing "is_stopped == False" will cause a song... 
                                                                                    # ...to start every time the "Stop" button is pressed.
    window.after(1000, song_has_ended_check)                                        # Repeat this function every 1 second

# ----------------------------------------------- # FUNCTIONS - GUI event handlers # ----------------------------------------------- #
def update_volume(event):                               # Function to change the volume according to our volume slider in the GUI
    global volume_slider
    pygame.mixer.music.set_volume(volume_slider.get())  # First gets the current value inside our tkinter slider then pass it to the pygame music volume function

def is_it_playing(event):   # Function that checks if the current selected item in the listbox is the same one that is playing currently. 
    global playlist         # ^^^ Needed to correctly update some GUI elements, like "Play/Pause" button.
    global play_button
    global current_song
    global status
    global MUSIC_END

    name, ext = os.path.splitext(os.path.basename(playlist.get(ACTIVE)))                         # Getting only the name of the song here, without the extension.
    
    if current_song.get() == name and status.get() == "Playing" and event.type != MUSIC_END:     # If our current playing song is the same as the current listbox selection, do nothing
        play_button.configure(text="Pause") # Needed because if we had clicked on a different item on the playlist and changed back to the current song, the label would be "Play"
        window.update()                     # Instead of "pause", which is the intended.
    else:
        play_button.configure(text="Play")  # If the music is not the same one that is playing, changes button from "Pause" to "Play"
        window.update()

def search_songs(event):         # Function to check the entry search bar vs all ListBox items, and show only what matches
    global playlist
    global song_search
    global playlist_URLs

    typed = song_search.get()    # Gets what we typed into the entrybox

    if typed == '':              # If we deleted everything we typed
        playlist.delete(0, END)  # Deletes whole playlist so we can re-add the items in the correct order it was
        for track in playlist_URLs:     # For every full song path
            name, ext = os.path.splitext(os.path.basename(track))   # Gets only the song name, without the extension
            playlist.insert(END, name)  # And inserts it into our ListBox in the GUI
    else:
        playlist.delete(0, END)         # Reseting the playlist so we can display only what matters
        for track in playlist_URLs:     # Going through every song full path
            name, ext = os.path.splitext(os.path.basename(track))   # Getting only the name of the song, without the extension
            if typed.lower() in track.lower():                      # Checks if whats typed matches an item inside the playlist_URLs
                playlist.insert(END, name)                          # If true, display it in our ListBox

def status_color_check():   # Depending on the state of the bool variables, changes the status label color.
    global is_playing
    global is_paused
    global is_stopped
    global status_label
    global window

    if is_playing == True:
        status_label.configure(text_color="green")
        window.update()
    elif is_paused == True:
        status_label.configure(text_color="yellow")
        window.update()
    elif is_stopped == True:
        status_label.configure(text_color="red")
        window.update()
    else:
        status_label.configure(text_color="white")
        window.update()

def play_button_check():    # Depending on the state of the bool variables, changes the play button label text.
    global is_playing
    global is_paused
    global is_stopped
    global window
    global play_button

    if is_playing == True:                  # If a song is playing, 
        play_button.configure(text="Pause") # Changes the button from "Play" to "Pause"
        window.update()
    elif is_paused == True:                 # If a song is paused, 
        play_button.configure(text="Play")  # Changes the button from "Pause" to "Play"
        window.update()
    elif is_stopped == True:                # If a song is stopped, 
        play_button.configure(text="Play")  # Changes the button to "Play"
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

# ------------------------------------------------------------- # SETTING UP VARIABLES # -------------------------------------------------------------#
window = customtkinter.CTk()
window.geometry("1000x260") #260
window.resizable(width=False,height=False)
window.title("Yani")
window.iconbitmap("resources\\images\\mp3playericon.ico")

pygame.init()                                           # Need this in order to be able catch pygame events
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)
MUSIC_END = pygame.USEREVENT+1                          # Thingy for checking the end of a song
pygame.mixer.music.set_endevent(MUSIC_END)

current_song = StringVar(window, value="<unknown>")     # Used by our tkinter gui element named "actual_song_lbl"   > Shows the name of the current song being played.
status = StringVar(window, "<not available>")           # Used by our tkinter gui element named "status_label"      > <not available> | Playing | Paused | Stopped

logo_img = customtkinter.CTkImage(dark_image=Image.open("resources\\images\\yui-hira.png"),size=(30,30))

# ------------------------------------------------------------- # CREATING THE GUI WIDGETS # -------------------------------------------------------------#
frame_1 = customtkinter.CTkFrame(window,width=300,height=240)   # Home for all of our control buttons
frame_2 = customtkinter.CTkFrame(window, width=670,height=240)  # Home for searchbar and playlist

current_song_label = customtkinter.CTkLabel(frame_1, text="CURRENTLY PLAYING:",font=("Rubik",12))
separator_1 = ttk.Separator(frame_1,orient=HORIZONTAL)
actual_song_lbl = customtkinter.CTkLabel(frame_1, textvariable=current_song,font=("Rubik", 10),text_color="orange")

volume_slider = customtkinter.CTkSlider(frame_1, from_=0.0,to=1.0,orientation=HORIZONTAL,state="normal",width=300,command=update_volume)

song_search = customtkinter.CTkEntry(frame_2,placeholder_text="Search for a song",width=365,corner_radius=1,font=("Liberation Serif", 11))
            
playlist = Listbox(frame_2, font=('Liberation Serif', 13),width=50,height=160,background="#2e3038",highlightcolor="#3c3d45",selectbackground="#213c1c",highlightthickness=0.5)
playlist_scroll_bar = customtkinter.CTkScrollbar(playlist,orientation=VERTICAL)
playlist.configure(yscrollcommand=playlist_scroll_bar.set)
playlist_scroll_bar.configure(command=playlist.yview)

play_button = customtkinter.CTkButton(frame_1,text="Play",width=70,font=("Rubik",12),command=play_song)     
stop_button = customtkinter.CTkButton(frame_1,text="Stop",width=70,font=("Rubik",12),command=stop_song)     
separator_2 = ttk.Separator(frame_1,orient=VERTICAL)
status_label = customtkinter.CTkLabel(frame_1,textvariable=status,font=("Rubik",15),text_color="white")
separator_3 = ttk.Separator(frame_1,orient=HORIZONTAL)

add_folder_button = customtkinter.CTkButton(frame_1,text="Add a directory",width=140,font=("Rubik",12),command=load_dir)
add_file_button = customtkinter.CTkButton(frame_1,text="Add a single file",width=140,font=("Rubik",12),command=load_file)
remove_all_button = customtkinter.CTkButton(frame_1,text="Remove All Songs",width=140,font=("Rubik",12),hover_color="red",command=remove_all)
playback_rate = customtkinter.CTkButton(frame_1,text="1x",width=140,font=("Rubik",12),hover_color="blue") # WILL BE REMOVED IN THE NEXT GUI UPDATE, ONLY A PLACEHOLDER  
separator_4 = ttk.Separator(frame_1,orient=HORIZONTAL)

yani_label = customtkinter.CTkLabel(frame_1,text="Yani Music Player",font=("Courier New",19),text_color="purple",image=logo_img,compound="left")

# ----------------------------------------------- # FUNCTIONS - GUI event handlers part 2 # ----------------------------------------------- #
song_search.bind("<KeyRelease>",search_songs)               # When a key is pressed and released, search the song that matches what's been typed
playlist.bind("<<ListboxSelect>>", is_it_playing)           # Selecting an item in the ListBox will trigger matching updates to the GUI labels
playlist.bind("<Double-Button-1>", play_event_doubleclick)  # Double clicking an item in the ListBox will start to play it

# ------------------------------------------------------------- # PACKING EVERYTHING # -------------------------------------------------------------#
frame_1.pack_propagate(False)                   # Needed so the frame stop changing it's width and height if we add items to it
frame_1.place(x=10,y=10)

current_song_label.pack(anchor=W,padx=5)        # displays - > "CURRENTLY PLAYING:"
separator_1.place(x=0,y=30,width=300,height=1,relwidth=1)
actual_song_lbl.place(x=135,y=0)                # displays - > "Generic Song - Bob ft Kevin"

volume_slider.place(x=0,y=50)
play_button.place(x=5,y=80)                     # displays - > "Play", "Pause" 
stop_button.place(x=85,y=80)
separator_2.place(x=165,y=80,width=1,height=30)
status_label.place(x=180,y=80)                  # displays - > "<not available>", "Playing", "Paused", "Stopped" 
separator_3.place(x=0,y=120,width=300,height=1)

add_folder_button.place(x=5,y=130)              # displays - > "Add a directory"
add_file_button.place(x=5,y=165)                # displays - > "Add a single file"
remove_all_button.place(x=155,y=130)
playback_rate.place(x=155,y=165)                # WILL BE REMOVED IN THE NEXT GUI UPDATE, ONLY A PLACEHOLDER
separator_4.place(x=0,y=205,width=300,height=1)

yani_label.place(x=30,y=210)                    # displays - > "Yani Music Player"

frame_2.pack_propagate(False)                   # Needed so the frame stop changing it's width and height if we add items to it
frame_2.place(x=320,y=10)

song_search.pack(padx=0,fill=BOTH)              # displays - > "Search for a song"
playlist.pack(fill=BOTH,pady=0,expand=TRUE)     # Fill and expand makes it take the max space inside the frame, thus making it nice and clean looking.
playlist_scroll_bar.pack(side=RIGHT,fill=BOTH)

# ----------------------------------------------- # FUNCTIONS - Setting up things on the start # ----------------------------------------------- #
on_program_start(playlist)  # This function will update ONLY the "playlist" variable - the one who holds control over the ListBox.
playlist_URLs = get_urls()  # This one will get the updated paths from the other file to this one. Couldn't manage to do it in the above function

# The End
window.update()
window.mainloop()