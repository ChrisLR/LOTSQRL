def colorize_text(ui_element, text):
    if ui_element.is_active:
        color = ui_element.theme.active_color
        bg_color = ui_element.theme.active_bg_color
    else:
        color = ui_element.theme.inactive_color
        bg_color = ui_element.theme.inactive_bg_color

    colorized_text = text
    if color is not None:
        colorized_text = f"[color={color}]{colorized_text}[/color]"

    if bg_color is not None:
        colorized_text = f"[bkcolor={bg_color}]{colorized_text}[/bkcolor]"

    return colorized_text
