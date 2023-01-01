# For GUI
from tkinter import *
from tkinter import filedialog
import customtkinter

# For fetching the playlist of songs from the specified directories.
import os

# For playing and loading music.
import pygame.mixer

# For handling image files
from PIL import Image

# --> CTK variables
customtkinter.set_appearance_mode("Dark")       # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("green")   # Themes: "blue" (standard), "green", "dark-blue"

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

pygame.mixer.init()

# --> Setting up some variables
current_song = StringVar(window, value="<unknown>")
status = StringVar(window, "<not available>")

# -- > Creating the GUI widgets
frame_1 = customtkinter.CTkFrame(window,width=300,height=240)
frame_2 = customtkinter.CTkFrame(window, width=370,height=240)
label_1 = customtkinter.CTkLabel(frame_1,text="Hello! This is a text test",font=("Liberation Serif",11))
label_2 = customtkinter.CTkLabel(frame_1,text="Hello! This is a text test")
button = customtkinter.CTkButton(window,text="Click me",command=load_dir)

song_search = customtkinter.CTkEntry(frame_2,placeholder_text="Search for a song",width=365,corner_radius=1)

playlist = Listbox(frame_2, font=('Liberation Serif', 11),width=50,height=50,background="#2e3038",highlightcolor="#3c3d45")

# -- > Packing everything
frame_1.pack_propagate(False) 
frame_1.place(x=10,y=10)
#label_1.pack()
#label_2.pack()

frame_2.pack_propagate(False)
frame_2.place(x=320,y=10)
song_search.pack(padx=5)
playlist.pack(pady=10)


#button.pack()

# The End
window.update()
window.mainloop()