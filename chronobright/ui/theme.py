import customtkinter as ctk

from chronobright import config


def apply_theme() -> None:
    ctk.set_appearance_mode(config.APPEARANCE_MODE)
    ctk.set_default_color_theme(config.COLOR_THEME)
