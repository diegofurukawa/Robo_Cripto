# src/interface/base_window.py
import customtkinter as ctk
from typing import Optional

class BaseWindow:
    """Base class for all windows in the application"""
    def __init__(self, title: str = "", geometry: str = "800x600"):
        self.title_font_size = 16
        self.font_size = 14
        self.font_style = "Arial"
        
    def create_label(self, parent, text: str, **kwargs) -> ctk.CTkLabel:
        """Helper method to create labels with consistent styling"""
        return ctk.CTkLabel(
            parent,
            text=text,
            font=(self.font_style, kwargs.get('font_size', self.font_size))
        )
        
    def create_button(self, parent, text: str, command, **kwargs) -> ctk.CTkButton:
        """Helper method to create buttons with consistent styling"""
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            font=(self.font_style, kwargs.get('font_size', self.font_size))
        )
        
    def create_entry(self, parent, textvariable: Optional[ctk.StringVar] = None, **kwargs) -> ctk.CTkEntry:
        """Helper method to create entry fields with consistent styling"""
        return ctk.CTkEntry(
            parent,
            textvariable=textvariable,
            font=(self.font_style, kwargs.get('font_size', self.font_size))
        )