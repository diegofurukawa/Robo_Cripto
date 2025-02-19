# src/interface/crypto_manager.py

import customtkinter as ctk
from tkinter import ttk, messagebox
from typing import Callable
from ..database.crypto_db import CryptoDatabase
from .base_window import BaseWindow

class CryptoManagerWindow(BaseWindow):
    """Window for managing cryptocurrencies"""
    def __init__(self, parent: ctk.CTk, db: CryptoDatabase, callback: Callable):
        super().__init__()
        self.window = ctk.CTkToplevel(parent)
        self.db = db
        self.callback = callback
        self.setup_window()
        self.setup_components()
        
    def setup_window(self):
        """Initialize the window properties"""
        self.window.title("Gerenciar Moedas")
        self.window.geometry("600x400")
        self.window.grab_set()  # Make window modal
        
    def setup_components(self):
        """Setup all UI components"""
        self.create_input_frame()
        self.create_crypto_table()
        self.refresh_table()
        
    def create_input_frame(self):
        """Create the input frame for adding new cryptocurrencies"""
        input_frame = ctk.CTkFrame(self.window)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        # Nome da Moeda
        self.create_label(input_frame, "Nome da Moeda:").pack(pady=5)
        self.name_entry = self.create_entry(input_frame)
        self.name_entry.pack(pady=5)
        
        # Código da Moeda
        self.create_label(input_frame, "Código (ex: SOLBRL):").pack(pady=5)
        self.code_entry = self.create_entry(input_frame)
        self.code_entry.pack(pady=5)
        
        # Checkbox Ativo
        self.active_var = ctk.BooleanVar(value=True)
        self.active_check = ctk.CTkCheckBox(
            input_frame,
            text="Ativo",
            variable=self.active_var,
            font=(self.font_style, self.font_size)
        )
        self.active_check.pack(pady=5)
        
        # Botão Adicionar
        self.create_button(
            input_frame,
            "Adicionar Moeda",
            self.add_crypto
        ).pack(pady=10)
        
    def create_crypto_table(self):
        """Create the table for displaying cryptocurrencies"""
        self.tree = ttk.Treeview(
            self.window,
            columns=("ID", "Nome", "Código", "Status"),
            show="headings"
        )
        
        # Configure columns
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Código", text="Código")
        self.tree.heading("Status", text="Status")
        
        # Configure column widths
        self.tree.column("ID", width=50)
        self.tree.column("Nome", width=200)
        self.tree.column("Código", width=150)
        self.tree.column("Status", width=100)
        
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        
    def add_crypto(self):
        """Add a new cryptocurrency to the database"""
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        is_active = self.active_var.get()
        
        if not name or not code:
            messagebox.showerror(
                "Erro",
                "Por favor, preencha todos os campos!"
            )
            return
            
        if self.db.add_crypto(name, code, is_active):
            self.clear_inputs()
            self.refresh_table()
            self.callback()  # Update main window
            messagebox.showinfo(
                "Sucesso",
                "Moeda adicionada com sucesso!"
            )
        else:
            messagebox.showerror(
                "Erro",
                "Código já existe!"
            )
            
    def clear_inputs(self):
        """Clear all input fields"""
        self.name_entry.delete(0, 'end')
        self.code_entry.delete(0, 'end')
        self.active_var.set(True)
        
    def refresh_table(self):
        """Refresh the cryptocurrency table"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        cryptos = self.db.get_all_cryptos()
        for crypto in cryptos:
            self.tree.insert("", "end", values=(
                crypto[0],  # ID
                crypto[1],  # Nome
                crypto[2],  # Código
                "Ativo" if crypto[3] else "Inativo"  # Status
            ))
            
    def on_close(self):
        """Handle window closing"""
        self.window.grab_release()
        self.window.destroy()
        self.callback()