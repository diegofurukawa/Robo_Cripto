# src/interface/components/crypto_table.py
from tkinter import ttk
import customtkinter as ctk

class CryptoTable(ttk.Treeview):
    """Reusable component for displaying cryptocurrency data"""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            columns=("ID", "Nome", "Código", "Status"),
            show="headings",
            **kwargs
        )
        
        self.setup_columns()
        self.pack(pady=10, padx=10, fill="both", expand=True)
        
    def setup_columns(self):
        """Configure the table columns"""
        columns = {
            "ID": 50,
            "Nome": 200,
            "Código": 150,
            "Status": 100
        }
        
        for col, width in columns.items():
            self.heading(col, text=col)
            self.column(col, width=width)
            
    def refresh_data(self, cryptos):
        """Update the table with new data"""
        self.clear()
        for crypto in cryptos:
            self.insert("", "end", values=(
                crypto[0],
                crypto[1],
                crypto[2],
                "Ativo" if crypto[3] else "Inativo"
            ))
            
    def clear(self):
        """Clear all items from the table"""
        for item in self.get_children():
            self.delete(item)