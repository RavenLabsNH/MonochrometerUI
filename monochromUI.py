import dearpygui.dearpygui as dpg
import multiprocessing as mp
from motor import Motor
from ctypes import c_bool

class MonochromUI():
    def __init__(self):
        dpg.create_context()
        mp.set_start_method('spawn')
        self.running_flag = mp.Value(c_bool, False)
        self.motor = Motor(self.running_flag)
        self.index = 0

    def create_page(self):
        with dpg.handler_registry():
            dpg.add_mouse_down_handler(callback=self.move_monochrom)
            dpg.add_mouse_release_handler(callback=self.stop_mnonochrom)

        with dpg.window(tag="Monochrom", width=800, height=400) as window:
            dpg.add_button(label="<", width=202, height=40, tag="left_button", callback=self.move_monochrom)
            dpg.add_button(label=">", width=202, height=40, tag="right_button")
            dpg.add_button(label="Stop", width=202, height=40, tag="stop_button", callback=self.stop_mnonochrom)

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
            self.index = self.index+1
            if self.index%4 == 0:
                dpg.render_dearpygui_frame()

    def move_monochrom(self):
        if dpg.is_item_active("left_button") and self.running_flag.value is False:
            self.running_flag.value = True
            backward_process = mp.Process(target=self.move_process_backward)
            backward_process.start()
        elif dpg.is_item_active("right_button") and self.running_flag.value is False:
            self.running_flag.value = True
            forward_process = mp.Process(target=self.move_process_forward)
            forward_process.start()

    def move_process_forward(self):
        motor = Motor(self.running_flag)
        motor.move_monochrom_forward_continuous()

    def move_process_backward(self):
        motor = Motor(self.running_flag)
        motor.move_monochrom_backward_continuous()

    def stop_mnonochrom(self):
        self.running_flag.value = False
