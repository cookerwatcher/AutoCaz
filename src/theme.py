'''
Filename: /src/twitch/faceover/src/theme.py
Path: /src/twitch/faceover/src
Created Date: Thursday, May 18th 2023, 1:45:23 am
Author: hippy

Copyright (c) 2023 WTFPL
'''

import imgui

def load_default_style():
    style = imgui.get_style()

    style.window_padding = 5.0, 5.0
    style.window_rounding = 0.0
    style.frame_padding = 5.0, 5.0
    style.frame_rounding = 3.0
    style.item_spacing = 12.0, 5.0
    style.item_inner_spacing = 5.0, 5.0
    style.indent_spacing = 25.0
    style.scrollbar_size = 15.0
    style.scrollbar_rounding = 9.0
    style.grab_min_size = 5.0
    style.grab_rounding = 3.0

    style.colors[imgui.COLOR_TEXT] = 0.91, 0.91, 0.91, 1.00
    style.colors[imgui.COLOR_TEXT_DISABLED] = 0.40, 0.40, 0.40, 1.00
    style.colors[imgui.COLOR_WINDOW_BACKGROUND] = 0.10, 0.10, 0.10, 1.00
    style.colors[imgui.COLOR_CHILD_BACKGROUND] = 0.00, 0.00, 0.00, 0.00
    style.colors[imgui.COLOR_BORDER] = 0.00, 0.00, 0.00, 0.39
    style.colors[imgui.COLOR_BORDER_SHADOW] = 1.00, 1.00, 1.00, 0.10
    style.colors[imgui.COLOR_FRAME_BACKGROUND] = 0.06, 0.06, 0.06, 1.00
    style.colors[imgui.COLOR_FRAME_BACKGROUND_HOVERED] = 0.75, 0.42, 0.02, 0.40
    style.colors[imgui.COLOR_FRAME_BACKGROUND_ACTIVE] = 0.75, 0.42, 0.02, 0.67
    style.colors[imgui.COLOR_TITLE_BACKGROUND] = 0.04, 0.04, 0.04, 1.00
    style.colors[imgui.COLOR_TITLE_BACKGROUND_COLLAPSED] = 0.00, 0.00, 0.00, 0.51
    style.colors[imgui.COLOR_TITLE_BACKGROUND_ACTIVE] = 0.18, 0.18, 0.18, 1.00
    style.colors[imgui.COLOR_SCROLLBAR_BACKGROUND] = 0.02, 0.02, 0.02, 0.53
    style.colors[imgui.COLOR_SCROLLBAR_GRAB] = 0.31, 0.31, 0.31, 0.80
    style.colors[imgui.COLOR_SCROLLBAR_GRAB_HOVERED] = 0.49, 0.49, 0.49, 0.80
    style.colors[imgui.COLOR_SCROLLBAR_GRAB_ACTIVE] = 0.49, 0.49, 0.49, 1.00
    style.colors[imgui.COLOR_CHECK_MARK] = 0.75, 0.42, 0.02, 1.00
    style.colors[imgui.COLOR_SLIDER_GRAB] = 0.75, 0.42, 0.02, 0.78
    style.colors[imgui.COLOR_SLIDER_GRAB_ACTIVE] = 0.75, 0.42, 0.02, 1.00
    style.colors[imgui.COLOR_BUTTON] = 0.75, 0.42, 0.02, 0.40
    style.colors[imgui.COLOR_BUTTON_HOVERED] = 0.75, 0.42, 0.02, 1.00
    style.colors[imgui.COLOR_BUTTON_ACTIVE] = 0.94, 0.47, 0.02, 1.00
    style.colors[imgui.COLOR_HEADER] = 0.75, 0.42, 0.02, 0.31
    style.colors[imgui.COLOR_HEADER_HOVERED] = 0.75, 0.42, 0.02, 0.80
    style.colors[imgui.COLOR_HEADER_ACTIVE] = 0.75, 0.42, 0.02, 1.00
    style.colors[imgui.COLOR_SEPARATOR] = 0.61, 0.61, 0.61, 1.00
    style.colors[imgui.COLOR_SEPARATOR_HOVERED] = 0.75, 0.42, 0.02, 0.78
    style.colors[imgui.COLOR_SEPARATOR_ACTIVE] = 0.75, 0.42, 0.02, 1.00
    style.colors[imgui.COLOR_RESIZE_GRIP] = 0.22, 0.22, 0.22, 1.00
    style.colors[imgui.COLOR_RESIZE_GRIP_HOVERED] = 0.75, 0.42, 0.02, 0.67
    style.colors[imgui.COLOR_RESIZE_GRIP_ACTIVE] = 0.75, 0.42, 0.02, 0.95
    style.colors[imgui.COLOR_PLOT_LINES] = 0.61, 0.61, 0.61, 1.00
    style.colors[imgui.COLOR_PLOT_LINES_HOVERED] = 0.00, 0.57, 0.65, 1.00
    style.colors[imgui.COLOR_PLOT_HISTOGRAM] = 0.10, 0.30, 1.00, 1.00
    style.colors[imgui.COLOR_PLOT_HISTOGRAM_HOVERED] = 0.00, 0.40, 1.00, 1.00
    style.colors[imgui.COLOR_TEXT_SELECTED_BACKGROUND] = 0.75, 0.42, 0.02, 0.35
    style.colors[imgui.COLOR_POPUP_BACKGROUND] = 0.00, 0.00, 0.00, 0.94
    style.colors[imgui.COLOR_MODAL_WINDOW_DIM_BACKGROUND] = 0.06, 0.06, 0.06, 0.35
