# src/interface/components/balance_frame.py
import customtkinter as ctk
from typing import Callable

class BalanceFrame(ctk.CTkFrame):
    """Frame component for balance display"""
    def __init__(self, parent, update_callback: Callable, font_style="Arial", font_size=14, **kwargs):
        super().__init__(parent, **kwargs)
        self.font_style = font_style
        self.font_size = font_size
        self.title_font_size = font_size + 2  # Caso você esteja usando isso para o título
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Saldo disponível:",
            font=(self.font_style, self.title_font_size)
        )
        self.title_label.pack(pady=5)
        
        # Balance text box
        self.balance_text = ctk.CTkTextbox(
            self,
            height=100,
            font=(self.font_style, self.font_size)
        )
        self.balance_text.pack(pady=5, padx=10, fill="both", expand=True)
        
        # Update button
        self.update_button = ctk.CTkButton(
            self,
            text="Atualizar Saldo",
            command=update_callback,
            font=(self.font_style, self.font_size)
        )
        self.update_button.pack(pady=5)
        
    def update_balance(self, balance_text: str):
        """Update the balance display"""
        self.balance_text.delete("1.0", "end")
        self.balance_text.insert("1.0", balance_text)
