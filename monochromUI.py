import dearpygui.dearpygui as dpg
import multiprocessing as mp
from motor import Motor
from ctypes import c_bool

class MonochromUI():
    def __init__(self):
        dpg.create_context()
        self.running_flag = mp.Value(c_bool, False)
        self.motor = Motor(self.running_flag)

    def create_page(self):
        with dpg.handler_registry():
            #dpg.add_mouse_down_handler(callback=self.move_monochrom)
            dpg.add_mouse_release_handler(callback=self.stop_mnonochrom)

        with dpg.window(tag="Monochrom", width=800, height=400) as window:
            dpg.add_button(label="<", width=202, height=40, tag="left_button", callback=self.move_monochrom)
            dpg.add_button(label=">", width=202, height=40, tag="right_button", callback=self.move_monochrom)

        dpg.create_viewport(title='Monochrom', width=800, height=400, x_pos=40, y_pos=40)
        dpg.setup_dearpygui()
        dpg.set_viewport_vsync(True)
        dpg.configure_app(wait_for_input=True)

        #dpg.show_metrics()
        dpg.show_viewport()

        dpg.set_primary_window("Monochrom", True)

    def run(self):
        """
        Run the main DearPyGui render thread
        """
        while dpg.is_dearpygui_running():
            dpg.render_dearpygui_frame()

    def move_monochrom(self):
        if dpg.is_item_active("left_button") and self.running_flag.value is False:
            self.running_flag.value = True
            forward_process = mp.Process(target=self.motor.move_monochrom_backward_continuous)
            forward_process.start()
        elif dpg.is_item_active("right_button") and self.running_flag.value is False:
            self.running_flag.value = True
            backward_process = mp.Process(target=self.motor.move_monochrom_forward_continuous)
            backward_process.start()

    def stop_mnonochrom(self):
        self.running_flag.value = False
