import dearpygui.dearpygui as dpg
import multiprocessing as mp
import yaml
#from motor import Motor
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
        dpg.configure_item("save_model_button", pos=[20, 374])
    else:
        dpg.configure_item("resolution_text", show=False)
        dpg.configure_item("resolution_input", show=False)
        dpg.configure_item("resolution_units", show=False)
        dpg.configure_item("save_model_button", pos=[20, 289])
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
            font_bold_48 = dpg.add_font("fonts/SourceSansPro-Bold.ttf", 35)
            font_bold_40 = dpg.add_font("fonts/SourceSansPro-Bold.ttf", 20)
            font_regular_30 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 19)
            font_regular_32 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 21)
            font_regular_48 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 30)
            font_regular_100 = dpg.add_font("fonts/SourceSansPro-Regular.ttf", 70)

        with dpg.texture_registry():
            width, height, channels, data2 = dpg.load_image("content/logo.png")
            dpg.add_static_texture(width, height, data2, tag="logo")
            width, height, channels, data2 = dpg.load_image("content/left_arrrow.png")
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
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 7, 15, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 10, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (244, 248, 252), category=dpg.mvThemeCat_Core)

        with dpg.theme() as input_button_theme:
            with dpg.theme_component(dpg.mvAll, enabled_state=True):
                dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 255, 255), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
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
                dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 88, 182), category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 20, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)

        with dpg.theme() as arrow_button_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1, category=dpg.mvThemeCat_Core)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 80, 35, category=dpg.mvThemeCat_Core)
                dpg.add_theme_color(dpg.mvThemeCol_Border, (0, 88, 182), category=dpg.mvThemeCat_Core)

        with dpg.window(tag="Monochrom", width=960, height=600) as window:
            with dpg.child_window(autosize_x=True, height=53, border=False) as header:
                dpg.add_image("logo", pos=[8, 8], width=140, height=38)
                dpg.add_text("Monochromator Control Software", pos=[180, 10])
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                with dpg.drawlist(width=960, height=53):
                    dpg.draw_line((164, 9), (164, 39), color=(201, 217, 235), thickness=3)
                    dpg.draw_line((0, 53), (1920, 53), color=(201, 217, 235), thickness=3)

            with dpg.child_window(autosize_x=True, autosize_y=True, show=False, tag="device_page", border=False):
                dpg.add_text("Select a Device", pos=[20, 20])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Model Number", pos=[20, 73])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_combo(self.profile_names, default_value="Model A", pos=[20, 97], width=425)
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="Test", pos=[450, 97], height=60, width=20)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="+ Create a new Model", width=181, height=24, pos=[263, 169],
                               callback=change_view, user_data="create_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), transparent_button_theme)

                dpg.add_text("Current Position", pos=[20, 213])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Current Position", width=425, pos=[20, 237], decimal=True,
                                   no_spaces=True, callback=change_state, user_data="calibrate_button")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("The current position can be found by reading the dial on the front of\n the machine",
                             pos=[20, 309])
                dpg.bind_item_font(dpg.last_item(), font_regular_30)

                dpg.add_button(label="Calibrate", width=425, height=60, pos=[20, 369], enabled=False,
                               tag="calibrate_button", callback=change_view, user_data="motor_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

            with dpg.child_window(autosize_x=True, autosize_y=True, show=False, tag="create_page", border=False):
                dpg.add_text("Create a New Model", pos=[20, 20])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Model", pos=[20, 62])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Model", width=425, pos=[20, 86],
                                   callback=change_state_create, tag="model_input")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("Calibration", pos=[20, 166])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_combo(["25 nm/rev", "50 nm/rev", "100 nm/rev", "200 nm/rev", "Custom"],
                              default_value="25 nm/rev", pos=[20, 190], width=425, callback=calibration_callback)
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("Custom Resolution", pos=[20, 270], show=False, tag="resolution_text")
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(hint="Enter Custom Resolution", width=425, pos=[20, 294], decimal=True,
                                   show=False, no_spaces=True, callback=change_state_create,
                                   user_data="calibrate_button", tag="resolution_input")
                dpg.bind_item_font(dpg.last_item(), font_regular_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_text("nm/rev", pos=[453, 319], tag="resolution_units", show=False)
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_button(label="Save Model", width=425, height=60, pos=[20, 289], tag="save_model_button",
                               callback=self.create_profile, enabled=False)
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

                dpg.add_button(label="Back to Device Page", width=177, height=20, pos=[28, 488],
                               callback=change_view, user_data="device_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), transparent_button_theme)


            with dpg.child_window(autosize_x=True, autosize_y=True, show=True, tag="motor_page",
                                  no_scrollbar=True, border=False):

                #Left Side
                dpg.add_text("Manual Move", pos=[20, 20])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text("Hold down the arrow to move the machine, or specify a new \nposition in the box to move to.",
                             pos=[20, 54])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_image_button("left_arrow", width=50, height=44,
                                     pos=[20, 114], tag="left_button", callback=self.move_monochrom)
                dpg.bind_item_theme(dpg.last_item(), arrow_button_theme)
                dpg.add_image_button("right_arrow", pos=[250, 114], width=50, height=44,
                               tag="right_button", callback=self.move_monochrom)
                dpg.bind_item_theme(dpg.last_item(), arrow_button_theme)

                dpg.add_text("Current Position", pos=[20, 250])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("1245.0", pos=[20, 279])
                dpg.bind_item_font(dpg.last_item(), font_regular_100)

                dpg.add_text("Move to Position", pos=[243, 250])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_input_text(width=217, pos=[243, 274], callback=change_state, user_data="go_to_button")
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="Go To Position", width=439, height=60, pos=[20, 367],
                               enabled=False, tag="go_to_button")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)


                #Right Side
                dpg.add_text("Run a Recipe", pos=[500, 20])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)

                dpg.add_text(
                    "Enter a custom recipe to run the Optometrics software on \ncontinuously or on a cycle",
                    pos=[500, 54])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("From", pos=[502, 139])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[545, 114])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("nm", pos=[653, 139])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("To", pos=[784, 139])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[809, 114])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("nm", pos=[917, 139])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("Delay", pos=[500, 219])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[545, 194])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("sec", pos=[653, 219])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_text("Increment", pos=[732, 219])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[809, 194])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)
                dpg.add_text("nm", pos=[917, 219])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)

                dpg.add_radio_button(["Cycles", "Continuous"], pos=[545, 274])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.bind_item_theme(dpg.last_item(), radio_button_theme)

                dpg.add_text("Cycles", pos=[758, 299])
                dpg.bind_item_font(dpg.last_item(), font_regular_32)
                dpg.add_input_text(width=100, pos=[809, 274])
                dpg.bind_item_font(dpg.last_item(), font_bold_48)
                dpg.bind_item_theme(dpg.last_item(), input_theme)

                dpg.add_button(label="Run Recipe", width=439, height=60, pos=[500, 367])
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

                dpg.add_button(label="Back to Calibration Page", width=182, height=20, pos=[28, 488],
                               callback=change_view, user_data="device_page")
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), transparent_button_theme)

                dpg.add_button(label="Stop", width=247, height=60, pos=[356, 467])
                dpg.bind_item_font(dpg.last_item(), font_bold_40)
                dpg.bind_item_theme(dpg.last_item(), input_button_theme)

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
