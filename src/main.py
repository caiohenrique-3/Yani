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

# -- > Variables
global folder_path
folder_path = ""    # Folder where the playlist is

global file_path
file_path = ""      # Folder where the single filer is

global status
status = None       # playing/paused

# --> Functions
def load_dir(listbox):
    os.chdir(filedialog.askdirectory(title="Select a folder",initialdir="~\Music"))
    tracks = os.listdir()
    for track in tracks:
        listbox.insert(END,track)

def load_file(listbox):
    os.chdir(filedialog.askopenfilename(title="Select a song",filetypes=[("MP3", ".mp3"),
                                        ("OGG", ".ogg"), ("XM", ".xm"), ("MOD", ".mod")], initialdir="~\Music"))

def play_event(song_name: StringVar, songs_list: Listbox, status: StringVar):
    song_name.set(songs_list.get(ACTIVE))
    pygame.mixer.music.load(songs_list.get(ACTIVE))
    pygame.mixer.music.play()
    status.set("Playing")

def stop_event(status: StringVar):
    pygame.mixer.music.stop()
    status.set("Stopped")

def pause_event(status: StringVar):
    pygame.mixer.music.pause()
    status.set("Paused")

def resume_song(status: StringVar):
    pygame.mixer.music.unpause()
    status.set("Playing")

# --> Setting up the window and the mixer
window = customtkinter.CTk()
window.geometry("700x260")
window.resizable(width=False,height=False)
window.title("Yani")
window.iconbitmap("resources\\images\\mp3playericon.ico")

pygame.mixer.init()

# --> Setting up some variables
current_song = StringVar(window, value="<unknown>")
status = StringVar(window, "<not available>")

logo_img = customtkinter.CTkImage(dark_image=Image.open("resources\\images\\guitar.png"),size=(30,30))

# -- > Creating the GUI widgets
frame_1 = customtkinter.CTkFrame(window,width=300,height=240)
frame_2 = customtkinter.CTkFrame(window, width=370,height=240)

current_song_label = customtkinter.CTkLabel(frame_1, text="CURRENTLY PLAYING:",font=("Rubik",12))
separator_1 = ttk.Separator(frame_1,orient=HORIZONTAL)
actual_song_lbl = customtkinter.CTkLabel(frame_1, textvariable=current_song,font=("Rubik", 12))

song_duration = customtkinter.CTkSlider(frame_1, from_=0,to=100,orientation=HORIZONTAL,state="normal",width=300)

song_search = customtkinter.CTkEntry(frame_2,placeholder_text="Search for a song",width=365,corner_radius=1,font=("Liberation Serif", 11))
playlist = Listbox(frame_2, font=('Liberation Serif', 12),width=50,height=160,background="#2e3038",highlightcolor="#3c3d45",selectbackground="#3c3d45",highlightthickness=0.5)
playlist_scroll_bar = customtkinter.CTkScrollbar(playlist,orientation=VERTICAL)
playlist.configure(yscrollcommand=playlist_scroll_bar.set)
playlist_scroll_bar.configure(command=playlist.yview)

play_button = customtkinter.CTkButton(frame_1,text="Play",width=70,font=("Rubik",12))      # play changes to "Pause" when state is "playing"
stop_button = customtkinter.CTkButton(frame_1,text="Stop",width=70,font=("Rubik",12))     # always shows stop
separator_2 = ttk.Separator(frame_1,orient=VERTICAL)
status_label = customtkinter.CTkLabel(frame_1,text="None",font=("Rubik",12))
separator_3 = ttk.Separator(frame_1,orient=HORIZONTAL)

add_folder_button = customtkinter.CTkButton(frame_1,text="Add a directory",width=140,font=("Rubik",12))
add_file_button = customtkinter.CTkButton(frame_1,text="Add a single file",width=140,font=("Rubik",12))
remove_all_button = customtkinter.CTkButton(frame_1,text="Remove All Songs",width=140,font=("Rubik",12),hover_color="red")
playback_rate = customtkinter.CTkButton(frame_1,text="1x",width=140,font=("Rubik",12),hover_color="blue")   # changes with each click.
separator_4 = ttk.Separator(frame_1,orient=HORIZONTAL)

yani_label = customtkinter.CTkLabel(frame_1,text="Yani Music Player",font=("Courier New",19),text_color="purple",image=logo_img,compound="left")
# -- > Packing everything
frame_1.pack_propagate(False) 
frame_1.place(x=10,y=10)

current_song_label.pack(anchor=W,padx=5)
separator_1.place(x=0,y=30,width=300,height=1,relwidth=1)
actual_song_lbl.place(x=180,y=0)

song_duration.place(x=0,y=50)
play_button.place(x=5,y=80) 
stop_button.place(x=85,y=80)
separator_2.place(x=165,y=80,width=1,height=30)
status_label.place(x=220,y=80)
separator_3.place(x=0,y=120,width=300,height=1)

add_folder_button.place(x=5,y=130)
add_file_button.place(x=5,y=165)
remove_all_button.place(x=155,y=130)
playback_rate.place(x=155,y=165)
separator_4.place(x=0,y=205,width=300,height=1)

yani_label.place(x=40,y=210)

frame_2.pack_propagate(False)
frame_2.place(x=320,y=10)

song_search.pack(padx=0,fill=BOTH)
playlist.pack(fill=BOTH,pady=0,expand=TRUE)
playlist_scroll_bar.pack(side=RIGHT,fill=BOTH)

# The End
window.update()
window.mainloop()