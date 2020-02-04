def colorize_text(ui_element, text):
    if ui_element.is_active:
        color = ui_element.theme.active_color
    else:
        color = ui_element.theme.inactive_color

    if color is None:
        return text
    return f"[color={color}]{text}[/color]"
