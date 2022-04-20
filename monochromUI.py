import dearpygui.dearpygui as dpg
import multiprocessing as mp
import yaml
#from motor import Motor
from ctypes import c_bool


def change_view(sender, app_data, user_data):
    dpg.configure_item("selection_page", show=False)
    dpg.configure_item("create_page", show=False)
    dpg.configure_item("calibration_page", show=False)
    dpg.configure_item("motor_page", show=False)
    dpg.configure_item(user_data, show=True)


class MonochromUI():
    def __init__(self):
        dpg.create_context()
        mp.set_start_method('spawn')
        self.running_flag = mp.Value(c_bool, False)
        self.profile_names = []
        with open("config.yaml", "r") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print("Error reading config file")
                exit()
        for profile in self.config["profiles"]:
            self.profile_names.append(profile['name'])


    def create_page(self):

        with dpg.handler_registry():
            dpg.add_mouse_down_handler(callback=self.move_monochrom)
            dpg.add_mouse_release_handler(callback=self.stop_mnonochrom)

        with dpg.font_registry():
            # first argument ids the path to the .ttf or .otf file
            font_bold_48 = dpg.add_font("fonts/SourceSansPro-Bold.ttf", 70)
            font_bold_40 = dpg.add_font("fonts/SourceSansPro-Bold.ttf", 40)
            font_regular_30 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 38)
            font_regular_32 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 48)
            font_regular_48 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 70)


        with dpg.theme() as main_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (244, 248, 252), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0, category=dpg.mvThemeCat_Core)


        with dpg.theme() as header_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core)

        with dpg.theme() as input_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 7, 25, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)

        with dpg.theme() as input_button_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (244, 248, 252), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.5, category=dpg.mvThemeCat_Core)

        with dpg.window(tag="Monochrom", width=1920, height=1200) as window:
            with dpg.child_window(autosize_x=True, height=106, border=False) as header:
                dpg.add_text("Monochromator Control Software", pos=[361, 24])
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
            #dpg.add_separator(pos=[0,106])
            with dpg.child_window(autosize_x=True, height=1094, show=True, tag="selection_page", border=True):
                dpg.add_text("Select a Device", pos=[40, 40])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Model Number", pos=[40, 147])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_combo(self.profile_names, pos=[40, 195], width=850)
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="Test", pos=[900, 195], height=120, width=40)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="+ Create a new Model", width=363, height=48, pos=[527, 339],
                               callback=change_view, user_data="create_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

                dpg.add_text("Current Position", pos=[40, 427])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Current Position", width=850, pos=[40, 475])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("The current position can be found by reading the dial on the front of\n the machine",
                             pos=[40, 619])
                dpg.bind_item_font(dpg.last_item(), font_regular_30)

                dpg.add_button(label="Calibrate", width=850, height=120, pos=[40, 739],
                               callback=change_view, user_data="calibration_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)

            with dpg.child_window(autosize_x=True, height=1094, show=False, tag="create_page", border=False):
                dpg.add_text("Create a New Model", pos=[40, 40])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Current Position", pos=[40, 427])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Current Position", width=850, pos=[40, 475])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_button(label="Done", callback=self.create_profile)

            with dpg.child_window(autosize_x=True, height=1094, show=False, tag="calibration_page", border=False):
                dpg.add_button(label="Done", callback=change_view, user_data="motor_page")

            with dpg.child_window(autosize_x=True, height=1094, show=False, tag="motor_page", border=False):
                dpg.add_button(label="<", width=202, height=40, tag="left_button", callback=self.move_monochrom)
                dpg.add_button(label=">", width=202, height=40, tag="right_button")

        dpg.bind_item_theme(window, main_theme)
        dpg.bind_item_theme(header, header_theme)
        dpg.create_viewport(title='Monochrom', width=1920, height=1248, x_pos=40, y_pos=40)
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

    def create_profile(self):
        name = dpg.get_value("input_name")
        calibration = int(dpg.get_value("input_calibration"))

        dict_data = {'name': name, 'calibration': calibration}
        self.config["profiles"].append(dict_data)

        with open("config.yaml", "w") as stream:
            try:
                yaml.safe_dump(self.config, stream)
            except yaml.YAMLError as exc:
                print("Error reading config file")
                exit()



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
