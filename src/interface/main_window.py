# src/interface/main_window.py
import customtkinter as ctk
from typing import List, Optional
from .base_window import BaseWindow
from .components.price_frame import PriceFrame
from .components.balance_frame import BalanceFrame
from .components.metrics_frame import MetricsFrame
from ..database.crypto_db import CryptoDatabase
from ..trading.trading_engine import TradingEngine
from tkinter import ttk
from .crypto_manager import CryptoManagerWindow
from ..utils.config import Config
from ..utils.binance_client import BinanceClient

class MainWindow(BaseWindow):
    """Main application window"""
    def __init__(self):
        super().__init__()
        self.db = CryptoDatabase(db_name="crypto.db")  # Adicionando o nome do banco de dados
        self.config = Config()  # Carrega configurações
        self.client = BinanceClient(self.config.api_key, self.config.api_secret)
        self.setup_window()
        self.setup_components()
        
    def setup_window(self):
        """Initialize the main window"""
        self.root = ctk.CTk()
        self.root.title("Crypto Trading Bot")
        self.root.geometry("800x800")
        
    def setup_components(self):
        """Setup all UI components"""
        # Top frame containing setup and balance
        self.top_frame = ctk.CTkFrame(self.root)
        self.top_frame.pack(pady=10, padx=20, fill="x")
        
        # Setup frame (left side)
        self.setup_frame = self.create_setup_frame()
        
        # Balance frame (right side)
        self.balance_frame = BalanceFrame(
            self.top_frame,
            self.atualizar_saldo,
            font_style=self.font_style,
            font_size=self.font_size
        )
        self.balance_frame.pack(side="right", padx=10, fill="both", expand=True)
        
        # Metrics frame
        self.metrics_frame = MetricsFrame(
            self.root,
            font_style=self.font_style,
            font_size=self.font_size
        )
        self.metrics_frame.pack(pady=10, padx=20, fill="x")
        
        # Status and logs frame
        self.create_status_frame()

    def atualizar_saldo(self):
        """Update balance display"""
        try:
            conta = self.client.get_account()
            saldos = []
            for ativo in conta["balances"]:
                if float(ativo["free"]) > 0 or float(ativo["locked"]) > 0:
                    saldos.append(f"{ativo['asset']}: {float(ativo['free']):.8f}")
            
            self.balance_frame.balance_text.delete("1.0", "end")
            self.balance_frame.balance_text.insert("1.0", "\n".join(saldos))
            
        except Exception as e:
            self.log_message(f"Erro ao atualizar saldo: {str(e)}")
        
    def create_setup_frame(self) -> ctk.CTkFrame:
        """Create and return the setup frame"""
        setup_frame = ctk.CTkFrame(self.top_frame)
        setup_frame.pack(side="left", padx=10, fill="both", expand=True)
        
        # Title
        self.create_label(
            setup_frame,
            text="Configurações",
            font_size=self.title_font_size
        ).pack()
        
        # Crypto management button
        self.create_button(
            setup_frame,
            text="Gerenciar Moedas",
            command=self.open_crypto_window
        ).pack(pady=5)
        
        # Create price frame
        self.price_frame = PriceFrame(
            setup_frame,
            self.calcular_quantidade,
            font_style=self.font_style,
            font_size=self.font_size
        )
        self.price_frame.pack(pady=5, padx=10, fill="x")
        
        return setup_frame
        
    def create_status_frame(self):
        """Create the status and logs frame"""
        self.status_frame = ctk.CTkFrame(self.root)
        self.status_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log_text = ctk.CTkTextbox(
            self.status_frame,
            font=(self.font_style, self.font_size)
        )
        self.log_text.pack(pady=5, padx=10, fill="both", expand=True)

    def open_crypto_window(self):
        """Open the cryptocurrency management window"""
        crypto_window = CryptoManagerWindow(
            parent=self.root,
            db=self.db,
            callback=self.update_crypto_list
        )
        crypto_window.window.grab_set()  # Make window modal
        
        def on_close():
            crypto_window.window.grab_release()
            crypto_window.window.destroy()
            self.update_crypto_list()
            
        crypto_window.window.protocol("WM_DELETE_WINDOW", on_close)


    def calcular_quantidade(self):
        """Calculate the quantity based on current price and investment value"""
        try:
            preco_atual = self.atualizar_preco()
            if preco_atual:
                symbol_info = self.get_symbol_info(self.par_var.get())
                if symbol_info:
                    valor_investir = float(self.valor_var.get())
                    quantidade_bruta = valor_investir / preco_atual
                    
                    # Ajusta a quantidade de acordo com as regras de LOT_SIZE
                    quantidade = self.adjust_quantity(quantidade_bruta, symbol_info['step_size'])
                    
                    # Verifica se está dentro dos limites
                    if quantidade < symbol_info['min_qty']:
                        self.log_message(f"Quantidade muito pequena. Mínimo: {symbol_info['min_qty']}")
                        quantidade = symbol_info['min_qty']
                    elif quantidade > symbol_info['max_qty']:
                        self.log_message(f"Quantidade muito grande. Máximo: {symbol_info['max_qty']}")
                        quantidade = symbol_info['max_qty']
                    
                    self.qtd_var.set(f"{quantidade:.8f}")
                    self.log_message(f"Quantidade ajustada para regras da Binance: {quantidade:.8f}")
                else:
                    self.log_message("Não foi possível obter informações do par de trading")
        except Exception as e:
            self.log_message(f"Erro ao calcular quantidade: {str(e)}")
        


    def get_symbol_info(self, symbol):
        """Get trading rules for a symbol"""
        try:
            info = self.client.get_symbol_info(symbol)
            for filter in info['filters']:
                if filter['filterType'] == 'LOT_SIZE':
                    return {
                        'min_qty': float(filter['minQty']),
                        'max_qty': float(filter['maxQty']),
                        'step_size': float(filter['stepSize'])
                    }
            return None
        except Exception as e:
            self.log_message(f"Erro ao obter informações do símbolo: {str(e)}")
            return None

    def adjust_quantity(self, quantity, step_size):
        """Adjust quantity to match symbol's step size"""
        step_size_decimals = len(str(step_size).split('.')[-1])
        return float(("{:." + str(step_size_decimals) + "f}").format(quantity - (quantity % step_size)))

    def atualizar_preco(self):
        """Update current price display"""
        try:
            ticker = self.client.get_symbol_ticker(symbol=self.par_var.get())
            preco = float(ticker['price'])
            self.preco_label.configure(text=f"Preço Atual: {preco:.8f}")
            return preco
        except Exception as e:
            self.log_message(f"Erro ao atualizar preço: {str(e)}")
            return None
        
        
    def run(self):
        """Start the application"""
        self.root.mainloop()