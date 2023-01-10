# For GUI
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
import customtkinter

# For fetching the playlist of songs from the specified directories.
import os

# For playing and loading music.
import pygame.mixer

# For handling png files
from PIL import Image

# --> CTK variables
customtkinter.set_appearance_mode("Dark")       # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")   # Themes: "blue" (standard), "green", "dark-blue"

# -- > Variables ~ Useful for tracking what is the app state. By doing this we can change label text/color depending on the situation.
is_playing = False
is_paused = False
is_stopped = True
autoplay = True

playlist_URLs = [] # A URL list for the ListBox playlist items - for upgrade the ListBox look  

# ------------------------------------------------------------- # FUNCTIONS # -------------------------------------------------------------#
def load_dir():         # Function to add all files inside a folder to the playlist
    global playlist
    global playlist_URLs

    os.chdir(filedialog.askdirectory(title="Select a folder",initialdir="~\Music"))
    tracks = os.listdir()

    for track in tracks:
        if track.endswith(".mp3" or ".wav" or ".ogg" or ".xm" or ".mod"):   # All pygame compatible music formats
            temp, ext = os.path.splitext(os.path.basename(os.path.abspath(track)))
            if temp not in playlist.get(0, END):                # Need to check the temp variable because we just store the song name inside the playlist ListBox.
                playlist_URLs.append(os.path.abspath(track))    # So, using the "track" variable won't work.
                playlist.insert(END,temp)
            

def load_file():        # Function to add a single file to the playlist
    global playlist
    global playlist_URLs

    track = filedialog.askopenfilename(title="Select a song",filetypes=[("MP3", ".mp3"),
                                        ("OGG", ".ogg"), ("XM", ".xm"), ("MOD", ".mod"), ("WAV", ".wav")], initialdir="~\Music")

    temp, ext = os.path.splitext(os.path.basename(os.path.abspath(track)))

    if temp not in playlist.get(0, END):                # Need to check the temp variable because we just store the song name inside the playlist ListBox.
        playlist_URLs.append(os.path.abspath(track))    # So, using the "track" variable won't work.
        playlist.insert(END,temp)

def remove_all():   # Function to delete all items inside the playlist. Also stops whatever song is playing.
    global playlist
    global playlist_URLs

    playlist.delete(0,END)
    playlist_URLs = []

    pygame.mixer.music.stop()   # TODO: Use the stop_event() instead...
    status.set("Stopped")
    boolean_switch("stop")
    status_color_check()
    play_button_check()

def play_event(): 
    global current_song
    global playlist
    global status
    global is_playing
    global is_paused
    global is_stopped
    global autoplay
    global playlist_URLs

    if is_playing == True:  # If the song is playing, clicking the button "Play" (which actually now displays "Pause") again will pause it.
        pause_event()
    elif is_paused == True: # If the song is paused, clicking the button "Play" (which actually now displays "Play") again will resume it.
        resume_event()
    else:
        os.chdir(os.path.dirname(os.path.abspath(playlist.get(ACTIVE))))        # Changes current working directory to the folder where the selected song is at.
                                                                                # So we don't need a full directory path to find it, only the song name.
        name, ext = os.path.splitext(os.path.basename(playlist.get(ACTIVE)))    # Splits the filename between the base and the extension
        current_song.set(name)                                                  # Updates "actual_song_lbl"
        
        pygame.mixer.music.load(playlist_URLs[playlist.curselection()[0]])
        #                                playlist.curselection()[0]
        # This metod return a list of the items selected of playlist so needs choose the index 0
        
        pygame.mixer.music.play()
        status.set("Playing")
        boolean_switch("play")   # Sets - > is_playing = True and everything else to False.
        play_button_check()      # Checks the boolean variables and changes the text of the "Play/Pause" button.
        status_color_check()     # Checks the boolean variables and changes the color of the status label.
        song_end_check_event()   # Checks every second if the song has ended

def play_event_doubleclick(event):  # Function to make the song start playing if the item is double-clicked in the ListBox.
    boolean_switch("stop")       # Sets - > is_stopped = True and everything else to False.
    play_event()                 # So we can easily pass play function first checks 

def autoplay_next_song():        # Basically the play_event function, but built for the song_end_check_event. When a song ends, a new one plays with this.
    global current_song
    global status
    global playlist
    global playlist_URLs
    
    boolean_switch("stop")      # Sets - > is_stopped = True and everything else to False.
    keep_going = True           # While the next element of the playlist isn't null, keeps autoplaying.

    try:
        playlist_URLs[playlist.curselection()[0] + 1]   # Checking if the next element exists
    except IndexError:          # This catches the "out of range" exception.
        keep_going = False
        stop_event()

    if keep_going:
        name, ext = os.path.splitext(os.path.basename(playlist_URLs[playlist.curselection()[0] + 1]))    # Splits the filename between the base and the extension
        current_song.set(name)      # Updates "actual_song_lbl"
            
        pygame.mixer.music.load(playlist_URLs[playlist.curselection()[0] + 1])  # Here, we are trying to load the next item in the playlist. Hence, the + 1 in the end.
        #                                playlist.curselection()[0] + 1 
        # This method returns a list of the items selected of the playlist, so it needs to choose the index 0 (current item) + 1 (next item) to load the correct thing.
            
        pygame.mixer.music.play()
        status.set("Playing")
        boolean_switch("play")   # Sets - > is_playing = True and everything else to False.
        play_button_check()      # Checks the boolean variables and changes the text of the "Play/Pause" button.
        status_color_check()     # Checks the boolean variables and changes the color of the status label.
        song_end_check_event()   # Checks every second if the song has ended
    
def stop_event():
    global status
    pygame.mixer.music.stop()
    status.set("Stopped")
    boolean_switch("stop")      # Sets - > is_stopped = True and everything else to False.
    status_color_check()        # Checks the boolean variables and changes the color of the status label.
    play_button_check()         # Checks the boolean variables and changes the text of the "Play/Pause" button.
    
def pause_event():
    global status

    pygame.mixer.music.pause()
    status.set("Paused")        
    boolean_switch("pause")     # Sets - > is_paused = True and everything else to False.
    status_color_check()        # Checks the boolean variables and changes the color of the status label.
    play_button_check()         # Checks the boolean variables and changes the text of the "Play/Pause" button.

def resume_event():
    global status

    pygame.mixer.music.unpause()
    status.set("Playing")
    boolean_switch("play")      # Sets - > is_playing = True and everything else to False.
    status_color_check()        # Checks the boolean variables and changes the color of the status label.
    play_button_check()         # Checks the boolean variables and changes the text of the "Play/Pause" button.

def volume_slider_event(event):                         # Function of the volume slider
    global volume_slider
    pygame.mixer.music.set_volume(volume_slider.get())  # First gets the current value inside the tkinter slider then set it by using the pygame module

def song_end_check_event(): # Function that Checks if the song has ended.
    global current_song
    global playlist
    global status

    for event in pygame.event.get():
        if event.type == MUSIC_END and autoplay == False:  # If the music ends, updates our GUI labels through our functions and setters.
            boolean_switch("stop")                      # Sets - > is_stopped = True and everything else to False.                  
            status_color_check()                        # Checks the boolean variables and changes the color of the status label.
            play_button_check()                         # Checks the boolean variables and changes the text of the "Play/Pause" button.
            status.set("Stopped")
            current_song.set("<unknown>")
        elif event.type == MUSIC_END and autoplay == True:  # If the music ends, auto starts the next item in the playlist.
            autoplay_next_song()
    window.after(1000, song_end_check_event)             # Repeat this function every 1 second

def new_song_check(event):       # Function that checks if the current selected item is the same one that is playing currently. Needed to correctly update some GUI elements.
    global playlist
    global play_button
    global current_song
    global status
    global MUSIC_END

    name, ext = os.path.splitext(os.path.basename(playlist.get(ACTIVE)))    # This ugly thing splits the filename from the extension and stores it in the variables.
    
    if current_song.get() == name and status.get() == "Playing" and event.type != MUSIC_END:     # If our current playing song is the same as the current listbox selection, do nothing
        play_button.configure(text="Pause") # Needed because if we had clicked on a different item on the playlist and changed back to the current song, the label would be "Play"
        window.update()                     # Instead of "pause", which is the intended.
    else:
        play_button.configure(text="Play")
        window.update()

def check_listbox(event):                       # Function to check the entry search bar vs all ListBox items
    global playlist
    global song_search
    global all_listbox_items
    global playlist_URLs

    all_listbox_items = playlist_URLs

    typed = song_search.get()                   # Gets what we typed into the entrybox

    for i, item in enumerate(all_listbox_items):    # Tried making a function that only displayed the matched items, but the code i wrote for it was too buggy 
        if typed.lower() in item.lower():           # (the playlist was being deleted in the proccess). So i opted for this lesser solution, which only highlights
            playlist.selection_set(i)               # The matching items vs what's typed in the search bar.
        else:
            playlist.selection_clear(i)
        if typed == '':
            playlist.selection_clear(0, END)

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

    if is_playing == True:
        play_button.configure(text="Pause")
        window.update()
    elif is_paused == True:
        play_button.configure(text="Play")
        window.update()
    elif is_stopped == True:
        play_button.configure(text="Play")
        window.update()

def boolean_switch(input):  # Function that sets the main booleans to True or False depending on the input parameter.
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
        print("[!] Error in boolean_switch function: Invalid input.")

# ------------------------------------------------------------- # SETTING UP VARIABLES # -------------------------------------------------------------#
window = customtkinter.CTk()
window.geometry("1000x260")
window.resizable(width=False,height=False)
window.title("Yani")
window.iconbitmap("resources\\images\\mp3playericon.ico")

pygame.init()                       # Need this in order to be able catch pygame events
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)
MUSIC_END = pygame.USEREVENT+1      # Thingy for checking the end of a song.
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

volume_slider = customtkinter.CTkSlider(frame_1, from_=0.0,to=1.0,orientation=HORIZONTAL,state="normal",width=300,command=volume_slider_event)

song_search = customtkinter.CTkEntry(frame_2,placeholder_text="Search for a song",width=365,corner_radius=1,font=("Liberation Serif", 11))
song_search.bind("<KeyRelease>",check_listbox)  # When a key is pressed and released, highlights any item that matches the typed words vs items inside the playlist ListBox.

playlist = Listbox(frame_2, font=('Liberation Serif', 13),width=50,height=160,background="#2e3038",highlightcolor="#3c3d45",selectbackground="#213c1c",highlightthickness=0.5)
playlist_scroll_bar = customtkinter.CTkScrollbar(playlist,orientation=VERTICAL)
playlist.configure(yscrollcommand=playlist_scroll_bar.set)
playlist_scroll_bar.configure(command=playlist.yview)

playlist.bind("<<ListboxSelect>>", new_song_check) # Create a binding on listbox with leftclick, used to change GUI labels
playlist.bind("<Double-Button-1>", play_event_doubleclick)  # Double clicking an item in the ListBox will start to play it
all_listbox_items = playlist.get(0, END) # Need this for the searchbar function 

play_button = customtkinter.CTkButton(frame_1,text="Play",width=70,font=("Rubik",12),command=play_event)      # Play changes to "Pause" when state is "playing"
stop_button = customtkinter.CTkButton(frame_1,text="Stop",width=70,font=("Rubik",12),command=stop_event)     # Always shows "stop"
separator_2 = ttk.Separator(frame_1,orient=VERTICAL)
status_label = customtkinter.CTkLabel(frame_1,textvariable=status,font=("Rubik",15),text_color="white")
separator_3 = ttk.Separator(frame_1,orient=HORIZONTAL)

add_folder_button = customtkinter.CTkButton(frame_1,text="Add a directory",width=140,font=("Rubik",12),command=load_dir)
add_file_button = customtkinter.CTkButton(frame_1,text="Add a single file",width=140,font=("Rubik",12),command=load_file)
remove_all_button = customtkinter.CTkButton(frame_1,text="Remove All Songs",width=140,font=("Rubik",12),hover_color="red",command=remove_all)
playback_rate = customtkinter.CTkButton(frame_1,text="1x",width=140,font=("Rubik",12),hover_color="blue")   # Changes with each click, 0.5, 0.75, 1.0, 1.25 - 1.5 - 2.0 ** TODO 
separator_4 = ttk.Separator(frame_1,orient=HORIZONTAL)

yani_label = customtkinter.CTkLabel(frame_1,text="Yani Music Player",font=("Courier New",19),text_color="purple",image=logo_img,compound="left")

# ------------------------------------------------------------- # PACKING EVERYTHING # -------------------------------------------------------------#
frame_1.pack_propagate(False) # Needed so the frame stop changing it's width and height
frame_1.place(x=10,y=10)

current_song_label.pack(anchor=W,padx=5)    # Anchor w == align item to the left.
separator_1.place(x=0,y=30,width=300,height=1,relwidth=1)
actual_song_lbl.place(x=135,y=0)            # This is where the song title is placed.

volume_slider.place(x=0,y=50)
play_button.place(x=5,y=80) 
stop_button.place(x=85,y=80)
separator_2.place(x=165,y=80,width=1,height=30)
status_label.place(x=180,y=80)
separator_3.place(x=0,y=120,width=300,height=1)

add_folder_button.place(x=5,y=130)
add_file_button.place(x=5,y=165)
remove_all_button.place(x=155,y=130)
playback_rate.place(x=155,y=165)
separator_4.place(x=0,y=205,width=300,height=1)

yani_label.place(x=30,y=210)

frame_2.pack_propagate(False)
frame_2.place(x=320,y=10)

song_search.pack(padx=0,fill=BOTH)
playlist.pack(fill=BOTH,pady=0,expand=TRUE)     # Fill and expand makes it take the max space inside the frame, thus making it nice and clean looking.
playlist_scroll_bar.pack(side=RIGHT,fill=BOTH)

# The End
window.update()
window.mainloop()