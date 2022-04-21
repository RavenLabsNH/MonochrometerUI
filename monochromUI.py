import dearpygui.dearpygui as dpg
import multiprocessing as mp
import yaml
from motor import Motor
from ctypes import c_bool


def change_view(sender, app_data, user_data):
    dpg.configure_item("device_page", show=False)
    dpg.configure_item("create_page", show=False)
    dpg.configure_item("motor_page", show=False)
    dpg.configure_item(user_data, show=True)

def change_state(sender, app_data, user_data):
    val = dpg.get_value(sender)
    if len(val) > 0:
        dpg.configure_item(user_data, enabled=True)
    else:
        dpg.configure_item(user_data, enabled=False)

def change_state_create(sender, app_data):
    if len(dpg.get_value("model_input")) > 0:
        state = dpg.get_item_configuration("resolution_input")
        if state['show'] is True:
            if len(dpg.get_value("resolution_input")) > 0:
                dpg.configure_item("save_model_button", enabled=True)
            else:
                dpg.configure_item("save_model_button", enabled=False)
        else:
            dpg.configure_item("save_model_button", enabled=True)
    else:
        dpg.configure_item("save_model_button", enabled=False)


def calibration_callback(sender, app_data):
    val = dpg.get_value(sender)
    if val == "Custom":
        dpg.configure_item("resolution_text", show=True)
        dpg.configure_item("resolution_input", show=True)
        dpg.configure_item("resolution_units", show=True)
        dpg.configure_item("save_model_button", enabled=False)
        dpg.set_value("resolution_input", "")
        dpg.configure_item("save_model_button", pos=[40, 749])
    else:
        dpg.configure_item("resolution_text", show=False)
        dpg.configure_item("resolution_input", show=False)
        dpg.configure_item("resolution_units", show=False)
        dpg.configure_item("save_model_button", pos=[40, 578])
        if len(dpg.get_value("model_input")) > 0:
            dpg.configure_item("save_model_button", enabled=True)

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
            font_regular_32 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 42)
            font_regular_48 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 60)
            font_regular_100 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 140)

        with dpg.texture_registry():
            width, height, channels, data2 = dpg.load_image("content/logo.png")
            dpg.add_static_texture(width, height, data2, tag="logo")


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
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 7, 30, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 10, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (244, 248, 252), category=dpg.mvThemeCat_Core)

        with dpg.theme() as input_button_theme:
            with dpg.theme_component(dpg.mvAll, enabled_state=True):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 3, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 88, 182), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (0, 88, 182), category=dpg.mvThemeCat_Core)
            with dpg.theme_component(dpg.mvAll, enabled_state=False):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (232, 237, 242), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (130, 135, 145), category=dpg.mvThemeCat_Core)

        with dpg.theme() as transparent_button_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (244, 248, 252), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ButtonTextAlign, 0.5, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Text, (11, 129, 255), category=dpg.mvThemeCat_Core)

        with dpg.theme() as radio_button_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 40, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 2, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 88, 182), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 88, 182), category=dpg.mvThemeCat_Core)

        with dpg.window(tag="Monochrom", width=1920, height=1200) as window:
            with dpg.child_window(autosize_x=True, height=107, border=False) as header:
                dpg.add_image("logo", pos=[16, 16], width=281, height=76)
                dpg.add_text("Monochromator Control Software", pos=[361, 20])
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                with dpg.drawlist(width=1920, height=107):
                    dpg.draw_line((329, 16), (329, 77), color=(201, 217, 235), thickness=3)
                    dpg.draw_line((0, 106), (1920, 105), color=(201, 217, 235), thickness=3)

            with dpg.child_window(autosize_x=True, autosize_y=True, show=True, tag="device_page", border=False):
                dpg.add_text("Select a Device", pos=[40, 40])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Model Number", pos=[40, 147])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_combo(self.profile_names, default_value="Model A", pos=[40, 195], width=850)
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="Test", pos=[900, 195], height=120, width=40)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="+ Create a new Model", width=363, height=48, pos=[527, 339],
                               callback=change_view, user_data="create_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), transparent_button_theme)

                dpg.add_text("Current Position", pos=[40, 427])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Current Position", width=850, pos=[40, 475], decimal=True,
                                   no_spaces=True, callback=change_state, user_data="calibrate_button")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("The current position can be found by reading the dial on the front of\n the machine",
                             pos=[40, 619])
                dpg.bind_item_font(dpg.last_item(), font_regular_30)

                dpg.add_button(label="Calibrate", width=850, height=120, pos=[40, 739], enabled=False,
                               tag="calibrate_button", callback=change_view, user_data="motor_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

            with dpg.child_window(autosize_x=True, autosize_y=True, show=False, tag="create_page", border=False):
                dpg.add_text("Create a New Model", pos=[40, 40])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Model", pos=[40, 125])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Model", width=850, pos=[40, 173],
                                   callback=change_state_create, tag="model_input")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("Calibration", pos=[40, 333])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_combo(["25 nm/rev", "50 nm/rev", "100 nm/rev", "200 nm/rev", "Custom"],
                              default_value="25 nm/rev", pos=[40, 381], width=850, callback=calibration_callback)
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("Custom Resolution", pos=[40, 541], show=False, tag="resolution_text")
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Custom Resolution", width=850, pos=[40, 589], decimal=True,
                                   show=False, no_spaces=True, callback=change_state_create,
                                   user_data="calibrate_button", tag="resolution_input")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("nm/rev", pos=[906, 639], tag="resolution_units", show=False)
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_button(label="Save Model", width=850, height=120, pos=[40, 578], tag="save_model_button",
                               callback=self.create_profile, enabled=False)
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

                dpg.add_button(label="Back to Device Page", width=354, height=40, pos=[56, 977],
                               callback=change_view, user_data="device_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), transparent_button_theme)


            with dpg.child_window(autosize_x=True, autosize_y=True, show=False, tag="motor_page",
                                  no_scrollbar=True, border=False):

                #Left Side
                dpg.add_text("Manual Move", pos=[40, 40])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Hold down the arrow to move the machine, or specify a new \nposition in the box to move to.",
                             pos=[40, 109])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_button(width=420, height=228, pos=[40, 229], tag="left_button", callback=self.move_monochrom)
                dpg.add_button(width=420, height=228, pos=[500, 229], tag="right_button", callback=self.move_monochrom)

                dpg.add_text("Current Position", pos=[40, 501])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("1245.0", pos=[40, 559])
                dpg.bind_item_font(dpg.last_item(), font_regular_100)

                dpg.add_text("Move to Position", pos=[486, 501])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text( width=434, pos=[486, 549])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="Go To Position", width=879, height=120, pos=[40, 734])
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)


                #Right Side
                dpg.add_text("Run a Recipe", pos=[1000, 40])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text(
                    "Enter a custom recipe to run the Optometrics software on \ncontinuously or on a cycle",
                    pos=[1000, 109])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("From", pos=[1004, 279])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=201, pos=[1090, 229])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("nm", pos=[1307, 279])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("To", pos=[1569, 279])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=201, pos=[1618, 229])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("nm", pos=[1835, 279])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("Delay", pos=[999, 439])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=201, pos=[1090, 389])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("sec", pos=[1307, 439])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("Increment", pos=[1464, 439])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=201, pos=[1618, 389])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("nm", pos=[1835, 439])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_radio_button(["Cycles", "Continuous"], pos=[1091, 549])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.bind_item_theme(dpg.last_item(), radio_button_theme)

                dpg.add_text("Cycles", pos=[1517, 599])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=201, pos=[1618, 549])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="Run Recipe", width=879, height=120, pos=[1000, 734])
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

                dpg.add_button(label="Back to Calibration Page", width=354, height=40, pos=[56, 977],
                               callback=change_view, user_data="device_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), transparent_button_theme)

                dpg.add_button(label="Stop", width=494, height=120, pos=[713, 934])
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

                with dpg.drawlist(width=1920, height=1094):
                    dpg.draw_line((960, 0), (960, 894), color=(201, 217, 235), thickness=3)
                    dpg.draw_line((0, 894), (1920, 894), color=(201, 217, 235), thickness=3)


                # dpg.add_button(label="<", width=202, height=40, tag="left_button", callback=self.move_monochrom)
                # dpg.add_button(label=">", width=202, height=40, tag="right_button")

        dpg.bind_item_theme(window, main_theme)
        dpg.bind_item_theme(header, header_theme)
        dpg.create_viewport(title='Monochrom', width=1920, height=1200, decorated=True)

        dpg.setup_dearpygui()
        dpg.set_viewport_vsync(True)
        dpg.configure_app(wait_for_input=False)

        #dpg.show_metrics()
        dpg.show_viewport()
        #dpg.toggle_viewport_fullscreen()
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
