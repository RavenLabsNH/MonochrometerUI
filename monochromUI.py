import math

import dearpygui.dearpygui as dpg
import multiprocessing as mp
from threading import Timer
import yaml
import re
import time
from motor import Motor
from DRV8825 import PI
from ctypes import c_bool, c_double
import subprocess

ONE_REV = 12800

def change_view(sender, app_data, user_data):
    dpg.configure_item("home_page", show=False)
    dpg.configure_item("device_page", show=False)
    dpg.configure_item("create_page", show=False)
    dpg.configure_item("motor_page", show=False)
    dpg.configure_item(user_data, show=True)

def is_valid_data(name):
    return len(dpg.get_value(name)) > 0

def change_state(sender, app_data, user_data):
    if is_valid_data(sender):
        dpg.configure_item(user_data, enabled=True)
    else:
        dpg.configure_item(user_data, enabled=False)

def change_state_recipe(sender, app_data):
    if is_valid_data("from_input") and is_valid_data("to_input") and is_valid_data("delay_input")\
            and is_valid_data("increment_input"):
        if dpg.get_value("radio_input") == "Continuous":
            dpg.configure_item("run_recipe_button", enabled=True)
        elif is_valid_data("cycles_input"):
            dpg.configure_item("run_recipe_button", enabled=True)
        else:
            dpg.configure_item("run_recipe_button", enabled=False)

    else:
        dpg.configure_item("run_recipe_button", enabled=False)

def calibration_callback(sender, app_data):
    val = dpg.get_value(sender)
    if val == "Custom":
        dpg.configure_item("resolution_text", show=True)
        dpg.configure_item("resolution_input", show=True)
        dpg.configure_item("resolution_units", show=True)
        dpg.configure_item("save_model_button", enabled=False)
        dpg.set_value("resolution_input", "")
        dpg.configure_item("save_model_button", pos=[20, 374])
    else:
        dpg.configure_item("resolution_text", show=False)
        dpg.configure_item("resolution_input", show=False)
        dpg.configure_item("resolution_units", show=False)
        dpg.configure_item("save_model_button", pos=[20, 289])
        if len(dpg.get_value("model_input")) > 0:
            dpg.configure_item("save_model_button", enabled=True)

def recipe_callback(sender, app_data):
    if dpg.get_value("radio_input") == "Continuous":
        dpg.configure_item("cycles_input", enabled=False)
        dpg.set_value("cycles_input", "")
        change_state_recipe(None, None)
    else:
        dpg.configure_item("cycles_input", enabled=True)
        change_state_recipe(None, None)

def render_window_center(sender, app_data, user_data):
    if dpg.does_item_exist(user_data):
        main_width = dpg.get_viewport_width()
        main_height = dpg.get_viewport_height()
        login_width = dpg.get_item_width(user_data)
        login_height = dpg.get_item_height(user_data)
        dpg.set_item_pos(user_data, [int((main_width // 2 - login_width // 2)),
                                     int((main_height / 2 - login_height / 2))])

class PopupFactory:
    def __init__(self, item_id, width, height, title=None, no_background=False, title_bar=False):
        self.item_id = item_id
        self.width = width
        self.height = height
        self.autosize = self.width <= 0
        self.label = title
        self.background = no_background
        self.title_bar = title_bar

    def create_popup(self):
        dpg.add_window(modal=True, no_close=True, no_move=True, width=self.width, height=self.height,
                       tag=self.item_id, autosize=self.autosize,
                       label=self.label, no_open_over_existing_popup=False,
                       no_title_bar=self.title_bar, no_background=self.background, no_resize=True,
                       pos=[int((dpg.get_viewport_width() // 2 - 500 // 2)),
                            int((dpg.get_viewport_height() // 2 - 500 // 2))])
        with dpg.item_handler_registry(tag=dpg.generate_uuid()) as handler:
            dpg.add_item_visible_handler(callback=render_window_center, parent=handler, user_data=self.item_id)
        dpg.bind_item_handler_registry(item=self.item_id, handler_registry=handler)
        with dpg.theme() as window_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, (244, 248, 252), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 88, 182), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 0, 0), category=dpg.mvThemeCat_Core)
        dpg.bind_item_theme(item=self.item_id, theme=window_theme)

class MonochromUI():
    def __init__(self):
        dpg.create_context()
        mp.set_start_method('spawn')
        self.running_flag = mp.Value(c_bool, False)
        self.profile_names = []
        self.current_nm = mp.Value(c_double, 0.0)
        self.device_steps_per_nm = 0
        self.command_queue = mp.Queue()
        self.running_processes = []
        self.free_motor()
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
            dpg.add_mouse_release_handler(callback=self.stop_continous_move)

        with dpg.font_registry():
            # first argument ids the path to the .ttf or .otf file
            font_bold_48 = dpg.add_font("fonts/SourceSansPro-Bold.ttf", 35)
            font_bold_40 = dpg.add_font("fonts/SourceSansPro-Bold.ttf", 22)
            font_regular_30 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 19)
            font_regular_32 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 21)
            font_regular_40 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 26)
            font_regular_48 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 30)
            font_regular_100 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 70)

        with dpg.texture_registry():
            width, height, channels, data2 = dpg.load_image("content/logo.png")
            dpg.add_static_texture(width, height, data2, tag="logo")
            width, height, channels, data2 = dpg.load_image("content/left_arrow.png")
            dpg.add_static_texture(width, height, data2, tag="left_arrow")
            width, height, channels, data2 = dpg.load_image("content/right_arrow.png")
            dpg.add_static_texture(width, height, data2, tag="right_arrow")

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
                dpg.add_theme_style(dpg.mvStyleVar_WindowBorderSize, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8, category=dpg.mvThemeCat_Core)

        with dpg.theme() as header_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 88, 182), category=dpg.mvThemeCat_Core)

        with dpg.theme() as input_theme:
            with dpg.theme_component(dpg.mvAll, enabled_state=True):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 7, 15, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 10, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (255, 255, 255), category=dpg.mvThemeCat_Core)
            with dpg.theme_component(dpg.mvAll, enabled_state=False):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 7, 15, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (237, 237, 242), category=dpg.mvThemeCat_Core)

        with dpg.theme() as bad_input_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 7, 15, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (255, 0, 0), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)

        with dpg.theme() as input_button_theme:
            with dpg.theme_component(dpg.mvAll, enabled_state=True):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 88, 182), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 88, 182), category=dpg.mvThemeCat_Core)
            with dpg.theme_component(dpg.mvAll, enabled_state=False):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (232, 237, 242), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (232, 237, 242), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (130, 135, 145), category=dpg.mvThemeCat_Core)

        with dpg.theme() as yes_button_theme:
            with dpg.theme_component(dpg.mvAll, enabled_state=True):
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (0, 88, 182), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 88, 182), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)


        with dpg.theme() as stop_button_theme:
            with dpg.theme_component(dpg.mvAll, enabled_state=True):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (220, 46, 7), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (220, 46, 7), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)
            with dpg.theme_component(dpg.mvAll, enabled_state=False):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (232, 237, 242), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (232, 237, 242), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (130, 135, 145), category=dpg.mvThemeCat_Core)

        with dpg.theme() as transparent_button_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (244, 248, 252), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (244, 248, 252), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.5, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (11, 129, 255), category=dpg.mvThemeCat_Core)

        with dpg.theme() as power_off_button_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.5, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (11, 129, 255), category=dpg.mvThemeCat_Core)

        with dpg.theme() as radio_button_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 88, 182), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 20, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)

        with dpg.theme() as arrow_button_theme:
            with dpg.theme_component(dpg.mvAll, enabled_state=True):
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 80, 35, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 88, 182), category=dpg.mvThemeCat_Core)
            with dpg.theme_component(dpg.mvAll, enabled_state=False):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (232, 237, 242), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (232, 237, 242), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 80, 35, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 88, 182), category=dpg.mvThemeCat_Core)

        def change_state_create(sender, app_data, user_data):

            if is_valid_data("model_input"):
                state = dpg.get_item_configuration("resolution_input")
                if state['show'] is True:
                    if is_valid_data("resolution_input"):
                        dpg.configure_item("save_model_button", enabled=True)
                    else:
                        dpg.configure_item("save_model_button", enabled=False)
                else:
                    dpg.configure_item("save_model_button", enabled=True)
            else:
                dpg.configure_item("save_model_button", enabled=False)

            if str(dpg.get_value("model_input")) in user_data:
                dpg.configure_item("save_model_button", enabled=False)
                dpg.bind_item_theme("model_input", bad_input_theme)
            else:
                dpg.configure_item("save_model_button", enabled=True)
                dpg.bind_item_theme("model_input", input_theme)

        def create_msg_popup():
            if dpg.does_item_exist("test_popup"):
                dpg.delete_item("test_popup")
            popup = PopupFactory("test_popup", 471, 234, "Test Message", False, True)
            popup.create_popup()
            with dpg.group(parent="test_popup"):
                dpg.add_text(default_value="Shutdown", pos=[45, 45])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.add_text(default_value="Are you sure you want to shutdown the device?", pos=[48, 89])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_button(label="No", width=180, height=60, user_data=("test_popup", True), pos=[45, 129],
                               callback=lambda sender, app_data, user_data: dpg.delete_item("test_popup"))
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)
                dpg.add_button(label="Yes", width=180, height=60, pos=[245, 129],
                               callback=lambda: subprocess.Popen(['shutdown', '-h', 'now']))
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.bind_item_theme(dpg.last_item(), yes_button_theme)


        with dpg.window(tag="Monochrom", width=960, height=600) as window:

            with dpg.child_window(autosize_x=True, height=53, border=False) as header:
                dpg.add_image("logo", pos=[8, 8], width=140, height=38)
                dpg.add_text("Monochromator Control Software", pos=[180, 10])
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.add_button(label="Power Off", width=85, height=22, pos=[848, 17],
                               callback=create_msg_popup)
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.bind_item_theme(dpg.last_item(), power_off_button_theme)
                with dpg.drawlist(width=960, height=53):
                    dpg.draw_line((164, 9), (164, 39), color=(201, 217, 235), thickness=3)
                    dpg.draw_line((0, 52), (1920, 52), color=(201, 217, 235), thickness=3)

            with dpg.child_window(autosize_x=True, autosize_y=True, show=True, tag="home_page", border=False):
                dpg.add_image("logo", pos=[310, 180], width=280, height=76)
                dpg.add_text("Software Version: 1.0.0", pos=[330, 276])
                dpg.bind_item_font(dpg.last_item(), font_regular_48)

            with dpg.child_window(autosize_x=True, autosize_y=True, show=False, tag="device_page", border=False):
                dpg.add_text("Select a Device", pos=[20, 20])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Model Number", pos=[20, 73])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_combo(self.profile_names, default_value="Model A", pos=[20, 97], width=425, tag="model_combo")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="+ Create a new Model", width=181, height=24, pos=[263, 169],
                               callback=change_view, user_data="create_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), transparent_button_theme)

                dpg.add_text("Current Position", pos=[20, 213])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Current Position", width=425, pos=[20, 237],
                                   decimal=True, tag="current_position_input", no_spaces=True,
                                   callback=change_state, user_data="calibrate_button")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("nm", pos=[452, 262])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("The current position can be found by reading the dial on the front of\n the machine",
                             pos=[20, 309])
                dpg.bind_item_font(dpg.last_item(), font_regular_30)

                dpg.add_button(label="Set Position", width=425, height=60, pos=[20, 369], enabled=False,
                               tag="calibrate_button", callback=self.calibrate)
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

            with dpg.child_window(autosize_x=True, autosize_y=True, show=False, tag="create_page", border=False):
                dpg.add_text("Create a New Model", pos=[20, 20])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Model", pos=[20, 62])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Model", width=425, pos=[20, 86],
                                   callback=change_state_create, user_data=self.profile_names, tag="model_input")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("Wavelength drive resolution", pos=[20, 166])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_combo(["25 nm/rev", "50 nm/rev", "100 nm/rev", "200 nm/rev", "Custom"], tag="combo_input",
                              default_value="Custom", pos=[20, 190], width=425, callback=calibration_callback)
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("Custom Resolution", pos=[20, 270], show=True, tag="resolution_text")
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Custom Resolution", width=425, pos=[20, 294], decimal=True,
                                   show=True, no_spaces=True, callback=change_state_create,
                                   user_data=self.profile_names, tag="resolution_input")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("nm/rev", pos=[453, 319], tag="resolution_units", show=True)
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_button(label="Save Model", width=425, height=60, pos=[20, 374], tag="save_model_button",
                               callback=self.create_profile, enabled=False)
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

                dpg.add_button(label="Back to Device Page", width=177, height=23, pos=[28, 488],
                               callback=change_view, user_data="device_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), transparent_button_theme)

            with dpg.child_window(autosize_x=True, autosize_y=True, show=False, tag="motor_page",
                                  no_scrollbar=True, border=False):
                #Left Side
                dpg.add_text("Manual Move", pos=[20, 20])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Hold down the arrow to change the wavelength, or specify a \nnew position in the box to move to.",
                             pos=[20, 54])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_image_button("left_arrow", width=50, height=44,
                                     pos=[20, 114], tag="left_button")
                dpg.bind_item_theme(dpg.last_item(), arrow_button_theme)
                dpg.add_image_button("right_arrow", pos=[250, 114], width=50, height=44,
                               tag="right_button")
                dpg.bind_item_theme(dpg.last_item(), arrow_button_theme)


                #dpg.bind_item_handler_registry("left_button", dpg.last_container())

                dpg.add_text("Current Wavelength", pos=[20, 250])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text(pos=[20, 279], tag="current_position_display")
                dpg.bind_item_font(dpg.last_item(), font_regular_100)

                dpg.add_text("Move to Wavelength", pos=[243, 250])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(width=200, pos=[243, 274], decimal=True, tag="move_to_input",
                                   callback=change_state, user_data="go_to_button")
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("nm", pos=[450, 299])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_button(label="Go", width=439, height=60, pos=[20, 367], callback=self.move_to,
                               enabled=False, tag="go_to_button")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)


                #Right Side
                dpg.add_text("Run a Routine", pos=[500, 20])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text(
                    "Enter a custom routine to run the Optometrics software \ncontinuously or on a cycle",
                    pos=[500, 54])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("From", pos=[502, 139])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[545, 114], tag="from_input", decimal=True,
                                   callback=change_state_recipe)
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("nm", pos=[653, 139])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("To", pos=[784, 139])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[809, 114], tag="to_input", decimal=True,
                                   callback=change_state_recipe)
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("nm", pos=[917, 139])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("Delay", pos=[500, 219])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[545, 194], tag="delay_input", decimal=True,
                                   callback=change_state_recipe)
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("sec", pos=[653, 219])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("Increment", pos=[731, 219])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[809, 194], tag="increment_input", decimal=True,
                                   callback=change_state_recipe)
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("nm", pos=[917, 219])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_radio_button(["Cycles", "Continuous"], pos=[545, 274],
                                     tag="radio_input", callback=recipe_callback)
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.bind_item_theme(dpg.last_item(), radio_button_theme)

                dpg.add_text("Cycles", pos=[758, 299])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[809, 274], tag="cycles_input", decimal=True,
                                   callback=change_state_recipe)
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="Run", width=439, height=60, pos=[500, 367], callback=self.run_recipe,
                               enabled=False, tag="run_recipe_button")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

                dpg.add_button(label="Back to Calibration Page", width=209, height=25, pos=[28, 488],
                               callback=change_view, user_data="device_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), transparent_button_theme)

                dpg.add_button(label="Stop", width=247, height=60, pos=[356, 467], enabled=False,
                               tag="stop_button", callback=self.stop_monochrom)
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), stop_button_theme)

                with dpg.drawlist(width=960, height=547):
                    dpg.draw_line((480, 0), (480, 447), color=(201, 217, 235), thickness=3)
                    dpg.draw_line((0, 447), (960, 447), color=(201, 217, 235), thickness=3)

        dpg.bind_item_theme(window, main_theme)
        dpg.bind_item_theme(header, header_theme)

        dpg.create_viewport(title='Monochrom', width=960, height=600, decorated=True)

        dpg.setup_dearpygui()
        dpg.set_viewport_vsync(True)
        dpg.configure_app(wait_for_input=False)

        #dpg.show_metrics()
        dpg.show_viewport()
        if PI:
            dpg.toggle_viewport_fullscreen()
        dpg.set_primary_window("Monochrom", True)

        timer = Timer(1, change_view, (None, None, "device_page"))
        timer.start()



    def run(self):
        """
        Run the main DearPyGui render thread
        """
        while dpg.is_dearpygui_running():
            if self.command_queue.qsize() > 0:
               self.process_queue()
            dpg.set_value("current_position_display", "{:06.1F}".format(round(self.current_nm.value, 1)))
            dpg.render_dearpygui_frame()

    def calibrate(self):
        selected = list(filter(lambda item: item['name'] == dpg.get_value("model_combo"), self.config["profiles"]))
        self.device_steps_per_nm = ONE_REV / selected[0]['calibration']
        self.current_nm.value = float(dpg.get_value("current_position_input"))
        change_view(None, None, user_data="motor_page")

    def create_profile(self):
        name = dpg.get_value("model_input")
        combo_input = dpg.get_value("combo_input")
        if combo_input == "Custom":
            calibration = int(dpg.get_value("input_calibration"))
        else:
            calibration = int(re.search(r'\d+', combo_input).group())

        dict_data = {'name': name, 'calibration': calibration}
        self.config["profiles"].append(dict_data)

        with open("config.yaml", "w") as stream:
            try:
                yaml.safe_dump(self.config, stream)
                self.profile_names.clear()
                for profile in self.config["profiles"]:
                    self.profile_names.append(profile['name'])
            except yaml.YAMLError as exc:
                print("Error reading config file")

        dpg.configure_item("model_combo", items=self.profile_names)
        change_view(None, None, "device_page")

    def move_to(self):
        move_to = float(dpg.get_value("move_to_input"))

        if self.running_flag.value:
            return

        self.command_queue.put("Start")
        self.running_flag.value = True

        run_process = mp.Process(target=self.move_to_process, args=(move_to,))
        self.running_processes.append(run_process)
        run_process.start()

    def move_to_process(self, move_to):
        distance = self.current_nm.value - move_to
        motor = Motor(self.running_flag, self.current_nm, self.device_steps_per_nm)

        if distance > 0:
            motor.move_monochrom_backward_steps(abs(distance) * self.device_steps_per_nm)

        elif distance < 0:
            motor.move_monochrom_forward_steps(abs(distance) * self.device_steps_per_nm)
        self.command_queue.put("Stop")
        self.running_flag.value = False

    def run_recipe(self):
        if self.running_flag.value:
            return

        _from = float(dpg.get_value("from_input"))
        _to = float(dpg.get_value("to_input"))
        _delay_input = abs(float(dpg.get_value("delay_input")))
        _increment_input = abs(float(dpg.get_value("increment_input")))

        is_continuous = dpg.get_value("radio_input") == "Continuous"
        if not is_continuous:
            _cycle_input = math.floor(float(dpg.get_value("cycles_input")))
        else:
            _cycle_input = 0

        if not is_continuous and _cycle_input < 1:
            return

        self.running_flag.value = True
        self.command_queue.put("Start")

        run_process = mp.Process(target=self.run_recipe_process, args=(_from, _to, _delay_input, _increment_input,
                                                                       _cycle_input, is_continuous,))
        self.running_processes.append(run_process)
        run_process.start()

    def run_recipe_process(self, _from, _to, _delay_input, _increment_input, _cycle_input, is_continuous):
        completed_cycles = 0
        motor = Motor(self.running_flag, self.current_nm, self.device_steps_per_nm)

        while self.running_flag.value:
            travel_to_start_distance = self.current_nm.value - _from

            if travel_to_start_distance > 0:
                motor.move_monochrom_backward_steps(abs(travel_to_start_distance) * self.device_steps_per_nm)
                time.sleep(_delay_input)

            elif travel_to_start_distance < 0:
                motor.move_monochrom_forward_steps(abs(travel_to_start_distance) * self.device_steps_per_nm)
                time.sleep(_delay_input)

            total_distance = _to - _from
            if total_distance == 0:
                self.running_flag.value = False
                break

            rounds = abs(int(total_distance / _increment_input))

            print("Rounds: " + rounds)

            for x in range(0, rounds):
                if self.running_flag.value is not True:
                    break
                if total_distance > 0:
                    motor.move_monochrom_forward_steps(_increment_input * self.device_steps_per_nm)
                else:
                    motor.move_monochrom_backward_steps(_increment_input * self.device_steps_per_nm)

                time.sleep(_delay_input)

            if self.running_flag.value is not True:
                break
            remaining = _to - (_from + (rounds * _increment_input))
            print("remaining: " + remaining)

            if total_distance > 0:
                motor.move_monochrom_forward_steps(remaining * self.device_steps_per_nm)
                time.sleep(_delay_input)
            else:
                motor.move_monochrom_backward_steps(remaining * self.device_steps_per_nm)
                time.sleep(_delay_input)

            if not is_continuous:
                completed_cycles = completed_cycles + 1
                if completed_cycles >= _cycle_input:
                    self.running_flag.value = False
        self.command_queue.put("Stop")
        self.running_flag.value = False

    def move_monochrom(self):
        if self.running_flag.value:
            return

        if dpg.is_item_active("left_button") and self.running_flag.value is False:
            self.running_flag.value = True
            self.command_queue.put("Start")
            backward_process = mp.Process(target=self.move_process_backward)
            self.running_processes.append(backward_process)
            backward_process.start()
        elif dpg.is_item_active("right_button") and self.running_flag.value is False:
            self.running_flag.value = True
            self.command_queue.put("Start")
            forward_process = mp.Process(target=self.move_process_forward)
            self.running_processes.append(forward_process)
            forward_process.start()

    def move_process_forward(self):
        motor = Motor(self.running_flag, self.current_nm, self.device_steps_per_nm)
        motor.move_monochrom_forward_continuous()

    def move_process_backward(self):
        motor = Motor(self.running_flag, self.current_nm, self.device_steps_per_nm)
        motor.move_monochrom_backward_continuous()

    def stop_continous_move(self):
        if dpg.is_item_hovered("left_button") or dpg.is_item_hovered("right_button"):
            self.stop_monochrom()

    def stop_monochrom(self):
        self.command_queue.put("Stop")
        self.running_flag.value = False

    def free_motor(self):
        motor = Motor(self.running_flag, self.current_nm, self.device_steps_per_nm)
        motor.stop_motor()

    def process_queue(self):
        command = self.command_queue.get()
        if command == "Start":
            dpg.configure_item("run_recipe_button", enabled=False)
            dpg.configure_item("go_to_button", enabled=False)
            dpg.configure_item("left_button", enabled=False)
            dpg.configure_item("right_button", enabled=False)
            dpg.configure_item("stop_button", enabled=True)
        elif command == "Stop":
            12323
            change_state_recipe(None, None)
            change_state("move_to_input", None, "go_to_button")
            dpg.configure_item("left_button", enabled=True)
            dpg.configure_item("right_button", enabled=True)
            dpg.configure_item("stop_button", enabled=False)
