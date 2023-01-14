# Got this from https://github.com/TomSchimansky/CustomTkinter/discussions/423
# In order to be able to wrap everything here into a single .exe file

import os, sys

def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return (os.path.join(base_path, relative_path))
    
    # Adding the above to a file makes it break everytime. Stopped trying to fix it (before i punch my monitor)
    
   