import dearpygui.dearpygui as dpg
#from Motor import Motor
from monochromUI import MonochromUI


if __name__ == "__main__":
    monochrom = MonochromUI()
    monochrom.create_page()
    monochrom.run()
