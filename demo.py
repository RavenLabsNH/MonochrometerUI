import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=600, height=300, decorated=False)

with dpg.window(label="Example Window", width=600, height=300, tag="demo"):
    dpg.add_button(label="Test" , pos=[100, 20], width=150, height=50)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("demo", True)
dpg.start_dearpygui()