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
# ------------------------------------------------------------- # FUNCTIONS # -------------------------------------------------------------#
def load_dir():
    global playlist
    os.chdir(filedialog.askdirectory(title="Select a folder",initialdir="~\Music"))
    tracks = os.listdir()
    for track in tracks:
        if track.endswith(".mp3" or ".wav" or ".ogg" or ".xm" or ".mod"):   # All pygame compatible music formats
            playlist.insert(END,os.path.abspath(track))     # I tried adding just the song titles but it wouldn't work if we added more items to the playlist later (different cwds)

def load_file():
    global playlist
    track = filedialog.askopenfilename(title="Select a song",filetypes=[("MP3", ".mp3"),
                                        ("OGG", ".ogg"), ("XM", ".xm"), ("MOD", ".mod"), ("WAV", ".wav")], initialdir="~\Music")
    #os.chdir(os.path.dirname(track))
    playlist.insert(END,os.path.abspath(track)) # I use abspath here because without it things weren't uniform in the GUI.
    update_playlist()

def remove_all():   # Function to delete all elements inside the playlist.
    global playlist
    playlist.delete(0,END)

def play_event():
    global current_song
    global playlist
    global status
    global is_playing
    global is_paused
    global is_stopped

    if is_playing == True:
        pause_event()
    elif is_paused == True:
        resume_event()
    else:
        os.chdir(os.path.dirname(os.path.abspath(playlist.get(ACTIVE))))
    
        print("cwd in play_event >>> "+os.getcwd())
        print("this is the path of the song in play_event>>> " + os.path.abspath(playlist.get(ACTIVE)))

        name, ext = os.path.splitext(os.path.basename(playlist.get(ACTIVE)))    # Splits the filename between the base and the extension
        #current_song.set(os.path.basename(playlist.get(ACTIVE)))
        current_song.set(name)
        pygame.mixer.music.load(playlist.get(ACTIVE))
        pygame.mixer.music.play()
        status.set("Playing")
        is_playing = True
        is_paused = False
        is_stopped = False
        play_button_check()
        status_color_check()

def stop_event():
    global is_playing
    global is_paused
    global is_stopped
    global status
    pygame.mixer.music.stop()
    status.set("Stopped")
    is_stopped = True
    is_playing = False
    is_paused = False
    status_color_check()
    play_button_check()
    
def pause_event():
    global status
    global is_playing
    global is_paused
    global is_stopped

    pygame.mixer.music.pause()
    status.set("Paused")
    is_stopped = False
    is_playing = False
    is_paused = True
    status_color_check()
    play_button_check()

def resume_event():
    global is_playing
    global is_paused
    global is_stopped
    global status
    pygame.mixer.music.unpause()
    status.set("Playing")
    is_stopped = False
    is_playing = True
    is_paused = False
    status_color_check()
    play_button_check()

def volume_slider_event(event):                         # Function of the volume slider
    global volume_slider
    pygame.mixer.music.set_volume(volume_slider.get())  # First gets the current value inside the tkinter slider then set it by using the pygame module

def check_listbox(event):                       # Function to check entry vs listbox
    global playlist
    global song_search
    global all_listbox_items

    all_listbox_items = playlist.get(0, END)    # Updates the playlist thingy
    typed = song_search.get()                   # Gets what we typed into the entrybox

    for i, item in enumerate(all_listbox_items):
        if typed.lower() in item.lower():
            playlist.selection_set(i)
        else:
            playlist.selection_clear(i)
        if typed == '':
            playlist.selection_clear(0, END)

    #if typed == '':
    #    for item in original_playlist:
    #        playlist.insert(END, original_playlist)
    #else: 
    #    playlist.delete(0,END)
    #    for item in data:
    #        if typed.lower() in item.lower():
    #            playlist.insert(END, item)

    #clean_song_names, ext = os.path.splitext(playlist.get(0,END))
    #songs = playlist.get(0,END)
    #print(songs)

#def fill_entry_search(event): # Updates the entrybox when a listbox click ocurs
#    global song_search
#    global playlist
#    song_search.delete(0, END) # Deletes whatever it's on the entrybox.
#    clean_name, ext = os.path.splitext(playlist.get(ACTIVE))
#    song_search.insert(0,clean_name)

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

# ------------------------------------------------------------- # SETTING UP VARIABLES # -------------------------------------------------------------#
window = customtkinter.CTk()
window.geometry("1000x260")
window.resizable(width=False,height=False)
window.title("Yani")
window.iconbitmap("resources\\images\\mp3playericon.ico")

pygame.mixer.init()
pygame.mixer.music.set_volume(0.5)

current_song = StringVar(window, value="<unknown>")
status = StringVar(window, "<not available>")

logo_img = customtkinter.CTkImage(dark_image=Image.open("resources\\images\\yui-hira.png"),size=(30,30))

# ------------------------------------------------------------- # CREATING THE GUI WIDGETS # -------------------------------------------------------------#
frame_1 = customtkinter.CTkFrame(window,width=300,height=240)   # home for all of our control buttons
frame_2 = customtkinter.CTkFrame(window, width=670,height=240)  # home for searchbar and playlist

current_song_label = customtkinter.CTkLabel(frame_1, text="CURRENTLY PLAYING:",font=("Rubik",12))
separator_1 = ttk.Separator(frame_1,orient=HORIZONTAL)
actual_song_lbl = customtkinter.CTkLabel(frame_1, textvariable=current_song,font=("Rubik", 10),text_color="orange")

volume_slider = customtkinter.CTkSlider(frame_1, from_=0.0,to=1.0,orientation=HORIZONTAL,state="normal",width=300,command=volume_slider_event)

song_search = customtkinter.CTkEntry(frame_2,placeholder_text="Search for a song",width=365,corner_radius=1,font=("Liberation Serif", 11))
song_search.bind("<KeyRelease>",check_listbox)  # when a key is pressed and released, check_listbox function executes

playlist = Listbox(frame_2, font=('Liberation Serif', 13),width=50,height=160,background="#2e3038",highlightcolor="#3c3d45",selectbackground="#213c1c",highlightthickness=0.5)
playlist_scroll_bar = customtkinter.CTkScrollbar(playlist,orientation=VERTICAL)
playlist.configure(yscrollcommand=playlist_scroll_bar.set)
playlist_scroll_bar.configure(command=playlist.yview)

#playlist.bind("<<ListboxSelect>>", fill_entry_search) # Create a binding on listbox with leftclick 
all_listbox_items = playlist.get(0, END) # need this for the searchbar function 

play_button = customtkinter.CTkButton(frame_1,text="Play",width=70,font=("Rubik",12),command=play_event)      # play changes to "Pause" when state is "playing"
stop_button = customtkinter.CTkButton(frame_1,text="Stop",width=70,font=("Rubik",12),command=stop_event)     # always shows stop
separator_2 = ttk.Separator(frame_1,orient=VERTICAL)
status_label = customtkinter.CTkLabel(frame_1,textvariable=status,font=("Rubik",15),text_color="white")
separator_3 = ttk.Separator(frame_1,orient=HORIZONTAL)

add_folder_button = customtkinter.CTkButton(frame_1,text="Add a directory",width=140,font=("Rubik",12),command=load_dir)
add_file_button = customtkinter.CTkButton(frame_1,text="Add a single file",width=140,font=("Rubik",12),command=load_file)
remove_all_button = customtkinter.CTkButton(frame_1,text="Remove All Songs",width=140,font=("Rubik",12),hover_color="red",command=remove_all)
playback_rate = customtkinter.CTkButton(frame_1,text="1x",width=140,font=("Rubik",12),hover_color="blue")   # changes with each click.
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