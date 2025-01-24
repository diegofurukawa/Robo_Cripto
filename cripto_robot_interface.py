import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
import pandas as pd
import os
import time
import threading
from datetime import datetime
from binance.client import Client
from binance.enums import *
from dotenv import load_dotenv
from crypto_database import CryptoDatabase

class CryptoWindow(ctk.CTkToplevel):
    def __init__(self, parent, db, callback, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.db = db
        self.callback = callback  # Add callback for updating main window
        self.title("Gerenciar Moedas")
        self.geometry("600x400")
        self.setup_ui()
        
    def setup_ui(self):
        # Input Frame
        input_frame = ctk.CTkFrame(self)
        input_frame.pack(pady=10, padx=10, fill="x")
        
        ctk.CTkLabel(input_frame, text="Nome da Moeda:").pack(pady=5)
        self.name_entry = ctk.CTkEntry(input_frame)
        self.name_entry.pack(pady=5)
        
        ctk.CTkLabel(input_frame, text="Código (ex: SOLBRL):").pack(pady=5)
        self.code_entry = ctk.CTkEntry(input_frame)
        self.code_entry.pack(pady=5)
        
        self.active_var = tk.BooleanVar(value=True)
        self.active_check = ctk.CTkCheckBox(input_frame, text="Ativo", variable=self.active_var)
        self.active_check.pack(pady=5)
        
        ctk.CTkButton(input_frame, text="Adicionar Moeda", command=self.add_crypto).pack(pady=10)
        
        # Table
        self.tree = ttk.Treeview(self, columns=("ID", "Nome", "Código", "Status"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Código", text="Código")
        self.tree.heading("Status", text="Status")
        self.tree.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.refresh_table()
        
    def add_crypto(self):
        name = self.name_entry.get().strip()
        code = self.code_entry.get().strip()
        is_active = self.active_var.get()
        
        if name and code:
            if self.db.add_crypto(name, code, is_active):
                self.name_entry.delete(0, 'end')
                self.code_entry.delete(0, 'end')
                self.active_var.set(True)
                self.refresh_table()
                self.callback()  # Call the callback to update main window
            else:
                messagebox.showerror("Erro", "Código já existe!")
                
    def refresh_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        cryptos = self.db.get_all_cryptos()
        for crypto in cryptos:
            self.tree.insert("", "end", values=(
                crypto[0], 
                crypto[1], 
                crypto[2], 
                "Ativo" if crypto[3] else "Inativo"
            ))

class CryptoTradingBot:
    def __init__(self):
        # Database initialization
        self.db = CryptoDatabase()
        
        # Trading session tracking
        self.current_trading_id = None
        self.trading_active = False
        self.posicao_atual = False
        
        # Configuration and API setup
        self.load_config()
        
        # Logging setup
        self.setup_logging()
        
        # GUI setup
        self.setup_gui()
        
        # Trading parameters
        self.last_trade_price = None
        self.last_trade_quantity = None
        self.last_trade_type = None
        
        # Performance tracking
        self.session_trades = []
        self.total_profit = 0.0
        
    def load_config(self):
        """Load API configuration from environment variables"""
        load_dotenv()
        self.api_key = os.getenv("KEY_BINANCE")
        self.secret_key = os.getenv("SECRET_BINANCE")
        self.cliente_binance = Client(self.api_key, self.secret_key)

    def setup_logging(self):
        """Setup logging files and configurations"""
        self.log_file = "trading_log.csv"
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("timestamp,tipo,par,quantidade,preco,total\n")
    
    def setup_gui(self):
        self.root = ctk.CTk()
        self.root.title("Crypto Trading Bot")
        self.root.geometry("800x800")
        
        self.title_font_size = 16
        self.font_size = 14
        self.font_style = "Arial"
        
        # Frame superior
        self.top_frame = ctk.CTkFrame(self.root)
        self.top_frame.pack(pady=10, padx=20, fill="x")
        
        # Configurações (lado esquerdo)
        self.setup_frame = ctk.CTkFrame(self.top_frame)
        self.setup_frame.pack(side="left", padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(self.setup_frame, text="Configurações", font=(self.font_style, self.title_font_size)).pack()
        
        # Botão Gerenciar Moedas
        self.crypto_button = ctk.CTkButton(
            self.setup_frame,
            text="Gerenciar Moedas",
            font=(self.font_style, self.font_size),
            command=self.open_crypto_window
        )
        self.crypto_button.pack(pady=5)
        
        # Combobox para seleção de moeda
        self.active_cryptos = self.get_active_crypto_codes()
        self.par_var = ctk.StringVar(value=self.active_cryptos[0] if self.active_cryptos else "")
        self.par_combo = ctk.CTkComboBox(
            self.setup_frame,
            values=self.active_cryptos,
            variable=self.par_var,
            font=(self.font_style, self.font_size)
        )
        self.par_combo.pack(pady=5)

        # Frame para preço e valor
        self.price_frame = ctk.CTkFrame(self.setup_frame)
        self.price_frame.pack(pady=5, padx=10, fill="x")

        # Preço atual
        self.preco_label = ctk.CTkLabel(
            self.price_frame, 
            text="Preço Atual: 0.00",
            font=(self.font_style, self.font_size)
        )
        self.preco_label.pack(pady=5)

        # Valor a investir
        ctk.CTkLabel(
            self.price_frame,
            text="Valor a Investir (BRL):",
            font=(self.font_style, self.font_size)
        ).pack()
        
        self.valor_var = ctk.StringVar(value="100.00")
        self.valor_entry = ctk.CTkEntry(
            self.price_frame,
            textvariable=self.valor_var,
            font=(self.font_style, self.font_size)
        )
        self.valor_entry.pack(pady=5)

        # Botão calcular
        self.calc_button = ctk.CTkButton(
            self.price_frame,
            text="Calcular Quantidade",
            font=(self.font_style, self.font_size),
            command=self.calcular_quantidade
        )
        self.calc_button.pack(pady=5)

        # Quantidade calculada
        ctk.CTkLabel(
            self.setup_frame,
            text="Quantidade:",
            font=(self.font_style, self.font_size)
        ).pack()
        
        self.qtd_var = ctk.StringVar(value="0.000000")  # Increased decimal places
        self.qtd_entry = ctk.CTkEntry(
            self.setup_frame,
            textvariable=self.qtd_var,
            font=(self.font_style, self.font_size)
        )
        self.qtd_entry.pack(pady=5)

        # Botões de Trading
        self.start_button = ctk.CTkButton(
            self.setup_frame,
            text="Iniciar Trading",
            font=(self.font_style, self.font_size),
            command=self.start_trading
        )
        self.start_button.pack(pady=5)

        self.stop_button = ctk.CTkButton(
            self.setup_frame,
            text="Parar Trading",
            font=(self.font_style, self.font_size),
            command=self.stop_trading,
            state="disabled"
        )
        self.stop_button.pack(pady=5)
                
        # Saldo Frame
        self.saldo_frame = ctk.CTkFrame(self.top_frame)
        self.saldo_frame.pack(side="right", padx=10, fill="both", expand=True)
        
        ctk.CTkLabel(self.saldo_frame, text="Saldo disponível:", font=(self.font_style, self.title_font_size)).pack()
        self.saldo_text = ctk.CTkTextbox(self.saldo_frame, height=100, font=(self.font_style, self.font_size))
        self.saldo_text.pack(pady=5, padx=10, fill="both", expand=True)
        
        self.atualizar_button = ctk.CTkButton(
            self.saldo_frame,
            text="Atualizar Saldo",
            font=(self.font_style, self.font_size),
            command=self.atualizar_saldo
        )
        self.atualizar_button.pack(pady=5)
        
        # Métricas Frame
        self.metrics_frame = ctk.CTkFrame(self.root)
        self.metrics_frame.pack(pady=10, padx=20, fill="x")
        
        self.media_metrics = ctk.CTkFrame(self.metrics_frame)
        self.media_metrics.pack(pady=5, padx=20, anchor="w")
        
        self.media_rapida_label = ctk.CTkLabel(
            self.media_metrics,
            text="Média Rápida: -",
            font=(self.font_style, self.font_size)
        )
        self.media_rapida_label.pack(pady=2, anchor="w")
        
        self.media_lenta_label = ctk.CTkLabel(
            self.media_metrics,
            text="Média Lenta: -",
            font=(self.font_style, self.font_size)
        )
        self.media_lenta_label.pack(pady=2, anchor="w")
        
        # Status e Logs Frame
        self.status_frame = ctk.CTkFrame(self.root)
        self.status_frame.pack(pady=10, padx=20, fill="both", expand=True)
        
        self.log_text = ctk.CTkTextbox(self.status_frame, font=(self.font_style, self.font_size))
        self.log_text.pack(pady=5, padx=10, fill="both", expand=True)

    def update_crypto_list(self):
        active_cryptos = self.get_active_crypto_codes()
        self.par_combo.configure(values=active_cryptos)
        if active_cryptos and self.par_var.get() not in active_cryptos:
            self.par_var.set(active_cryptos[0])

    def get_active_crypto_codes(self):
        cryptos = self.db.get_active_cryptos()
        return [crypto[2] for crypto in cryptos] if cryptos else ["SOLBRL"]
        
    def open_crypto_window(self):
        crypto_window = CryptoWindow(self.root, self.db, self.update_crypto_list)
        crypto_window.grab_set()
        
        def on_close():
            crypto_window.grab_release()
            crypto_window.destroy()
            self.update_crypto_list()
            
        crypto_window.protocol("WM_DELETE_WINDOW", on_close)
    
    def atualizar_saldo(self):
        try:
            conta = self.cliente_binance.get_account()
            saldos = []
            for ativo in conta["balances"]:
                if float(ativo["free"]) > 0 or float(ativo["locked"]) > 0:
                    saldos.append(f"{ativo['asset']}: {float(ativo['free']):.8f}")
            self.saldo_text.delete("1.0", "end")
            self.saldo_text.insert("1.0", "\n".join(saldos))
        except Exception as e:
            self.log_message(f"Erro ao atualizar saldo: {str(e)}")

    def atualizar_preco(self):
        try:
            ticker = self.cliente_binance.get_symbol_ticker(symbol=self.par_var.get())
            preco = float(ticker['price'])
            self.preco_label.configure(text=f"Preço Atual: {preco:.8f}")  # Increased decimal places
            return preco
        except Exception as e:
            self.log_message(f"Erro ao atualizar preço: {str(e)}")
            return None

    def get_symbol_info(self, symbol):
        try:
            info = self.cliente_binance.get_symbol_info(symbol)
            symbol_info = {}
            
            for filter in info['filters']:
                if filter['filterType'] == 'LOT_SIZE':
                    symbol_info.update({
                        'min_qty': float(filter['minQty']),
                        'max_qty': float(filter['maxQty']),
                        'step_size': float(filter['stepSize'])
                    })
                elif filter['filterType'] == 'MIN_NOTIONAL':
                    symbol_info['min_notional'] = float(filter['minNotional'])
                
            return symbol_info if symbol_info else None
            
        except Exception as e:
            self.log_message(f"Erro ao obter informações do símbolo: {str(e)}")
            return None

    def adjust_quantity(self, quantity, step_size):
        """Ajusta a quantidade para corresponder ao step size"""
        step_size_decimals = len(str(step_size).split('.')[-1])
        return float(("{:." + str(step_size_decimals) + "f}").format(quantity - (quantity % step_size)))

    def calcular_quantidade(self):
        try:
            preco_atual = self.atualizar_preco()
            if preco_atual:
                symbol_info = self.get_symbol_info(self.par_var.get())
                if symbol_info:
                    valor_investir = float(self.valor_var.get())
                    quantidade_bruta = valor_investir / preco_atual
                    
                    # Ajusta a quantidade de acordo com as regras de LOT_SIZE
                    quantidade = self.adjust_quantity(quantidade_bruta, symbol_info['step_size'])
                    
                    # Verifica se está dentro dos limites de quantidade
                    if quantidade < symbol_info['min_qty']:
                        self.log_message(f"Quantidade muito pequena. Mínimo: {symbol_info['min_qty']}")
                        quantidade = symbol_info['min_qty']
                    elif quantidade > symbol_info['max_qty']:
                        self.log_message(f"Quantidade muito grande. Máximo: {symbol_info['max_qty']}")
                        quantidade = symbol_info['max_qty']
                    
                    # Verifica o valor notional mínimo
                    valor_total = quantidade * preco_atual
                    if 'min_notional' in symbol_info and valor_total < symbol_info['min_notional']:
                        quantidade_minima = symbol_info['min_notional'] / preco_atual
                        quantidade = self.adjust_quantity(quantidade_minima, symbol_info['step_size'])
                        self.log_message(f"Valor total muito pequeno. Ajustando para o mínimo notional: {symbol_info['min_notional']} BRL")
                        
                    self.qtd_var.set(f"{quantidade:.8f}")
                    valor_total = quantidade * preco_atual
                    self.log_message(f"Quantidade ajustada: {quantidade:.8f} (Valor total: {valor_total:.2f} BRL)")
                else:
                    self.log_message("Não foi possível obter informações do par de trading")
        except Exception as e:
            self.log_message(f"Erro ao calcular quantidade: {str(e)}")
            
    def log_message(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.log_text.insert("end", f"[{timestamp}] {message}\n")
        self.log_text.see("end")
        
    def pegando_dados(self, codigo, intervalo):
        candles = self.cliente_binance.get_klines(
            symbol=codigo,
            interval=intervalo,
            limit=1000
        )
        precos = pd.DataFrame(candles)
        precos.columns = [
            "tempo_abertura", "abertura", "maxima", "minima",
            "fechamento", "volume", "tempo_fechamento",
            "moedas_negociadas", "numero_trades",
            "volume_ativo_base_compra", "volume_ativo_cotação", "-"
        ]
        precos = precos[["fechamento", "tempo_fechamento"]]
        precos["tempo_fechamento"] = pd.to_datetime(precos["tempo_fechamento"], unit="ms").dt.tz_localize("UTC")
        precos["tempo_fechamento"] = precos["tempo_fechamento"].dt.tz_convert("America/Sao_Paulo")
        precos["fechamento"] = precos["fechamento"].astype(float)
        return precos
        
    def log_trade(self, tipo, par, quantidade, preco):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = float(quantidade) * float(preco)
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp},{tipo},{par},{quantidade:.8f},{preco:.8f},{total:.8f}\n")
    
    def estrategia_trade(self, dados, codigo_ativo, ativo_operado, quantidade, posicao):
        dados["media_rapida"] = dados["fechamento"].rolling(window=7).mean()
        dados["media_devagar"] = dados["fechamento"].rolling(window=40).mean()
        
        ultima_media_rapida = dados["media_rapida"].iloc[-1]
        ultima_media_devagar = dados["media_devagar"].iloc[-1]
        preco_atual = float(dados["fechamento"].iloc[-1])
        
        self.log_message(f"DEBUG - Preço atual: {preco_atual:.8f}")
        self.log_message(f"DEBUG - Média Rápida: {ultima_media_rapida:.8f}")
        self.log_message(f"DEBUG - Média Lenta: {ultima_media_devagar:.8f}")
        self.log_message(f"DEBUG - Posição atual: {posicao}")
        self.log_message(f"DEBUG - Condição compra: {ultima_media_rapida > ultima_media_devagar and not posicao}")
        self.log_message(f"DEBUG - Condição venda: {ultima_media_rapida < ultima_media_devagar and posicao}")
        
        self.media_rapida_label.configure(text=f"Média Rápida: {ultima_media_rapida:.8f}")
        self.media_lenta_label.configure(text=f"Média Lenta: {ultima_media_devagar:.8f}")
        
        try:
            symbol_info = self.get_symbol_info(codigo_ativo)
            if not symbol_info:
                self.log_message("Erro: Não foi possível obter informações do par de trading")
                return posicao

            conta = self.cliente_binance.get_account()
            quantidade_atual = 0
            
            for ativo in conta["balances"]:
                if ativo["asset"] == ativo_operado:
                    quantidade_atual = float(ativo["free"])
            
            if ultima_media_rapida > ultima_media_devagar and not posicao:
                # Ajusta a quantidade de compra de acordo com as regras de LOT_SIZE
                quantidade_ajustada = self.adjust_quantity(quantidade, symbol_info['step_size'])
                if quantidade_ajustada >= symbol_info['min_qty'] and quantidade_ajustada <= symbol_info['max_qty']:
                    order = self.cliente_binance.create_order(
                        symbol=codigo_ativo,
                        side=SIDE_BUY,
                        type=ORDER_TYPE_MARKET,
                        quantity=quantidade_ajustada
                    )
                    self.log_message(f"COMPRA executada - Quantidade: {quantidade_ajustada:.8f}")
                    self.log_trade("COMPRA", codigo_ativo, quantidade_ajustada, preco_atual)
                    posicao = True
                else:
                    self.log_message(f"Quantidade de compra inválida: {quantidade_ajustada:.8f}")
                
            elif ultima_media_rapida < ultima_media_devagar and posicao:
                # Ajusta a quantidade de venda de acordo com as regras de LOT_SIZE
                quantidade_venda = self.adjust_quantity(quantidade_atual, symbol_info['step_size'])
                if quantidade_venda >= symbol_info['min_qty'] and quantidade_venda <= symbol_info['max_qty']:
                    order = self.cliente_binance.create_order(
                        symbol=codigo_ativo,
                        side=SIDE_SELL,
                        type=ORDER_TYPE_MARKET,
                        quantity=quantidade_venda
                    )
                    self.log_message(f"VENDA executada - Quantidade: {quantidade_venda:.8f}")
                    self.log_trade("VENDA", codigo_ativo, quantidade_venda, preco_atual)
                    posicao = False
                else:
                    self.log_message(f"Quantidade de venda inválida: {quantidade_venda:.8f}")
                
        except Exception as e:
            self.log_message(f"Erro na execução: {str(e)}")
            
        return posicao
        
    def trading_loop(self):
        while self.trading_active:
            try:
                self.atualizar_preco()
                dados_atualizados = self.pegando_dados(
                    codigo=self.par_var.get(),
                    intervalo=Client.KLINE_INTERVAL_1HOUR
                )
                
                self.posicao_atual = self.estrategia_trade(
                    dados_atualizados,
                    codigo_ativo=self.par_var.get(),
                    ativo_operado=self.par_var.get().replace("BRL", ""),
                    quantidade=float(self.qtd_var.get()),
                    posicao=self.posicao_atual
                )
                
                for minuto in range(5, 0, -1):
                    if not self.trading_active:
                        break
                    self.log_message(f"Aguardando próxima análise... {minuto} minutos restantes")
                    time.sleep(60)
                    self.atualizar_preco()  # Atualiza o preço durante a espera
                
            except Exception as e:
                self.log_message(f"Erro no loop de trading: {str(e)}")
                time.sleep(60)
    
    # Add these methods to the CryptoTradingBot class

    def start_trading(self):
        """Start trading session with database logging"""
        try:
            valor_investido = float(self.valor_var.get())
            quantidade = float(self.qtd_var.get())
            codigo_ativo = self.par_var.get()
            
            # Start trading session in database
            self.current_trading_id = self.db.start_trading_session(
                codigo_ativo=codigo_ativo,
                value_investido=valor_investido,
                qtde_investida=quantidade
            )
            
            if self.current_trading_id:
                self.trading_active = True
                self.start_button.configure(state="disabled")
                self.stop_button.configure(state="normal")
                self.log_message(f"Trading iniciado - Sessão ID: {self.current_trading_id}")
                
                self.trading_thread = threading.Thread(target=self.trading_loop)
                self.trading_thread.daemon = True
                self.trading_thread.start()
            else:
                self.log_message("Erro ao iniciar sessão de trading")
                
        except Exception as e:
            self.log_message(f"Erro ao iniciar trading: {str(e)}")

    def stop_trading(self):
        """Stop trading session with database logging"""
        if hasattr(self, 'current_trading_id'):
            if self.db.stop_trading_session(self.current_trading_id):
                self.log_message(f"Sessão de trading {self.current_trading_id} finalizada")
            else:
                self.log_message("Erro ao finalizar sessão no banco de dados")
        
        self.trading_active = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.log_message("Trading parado")

    def log_trade(self, tipo, par, quantidade, preco):
        """Log trade to both CSV and database"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        total = float(quantidade) * float(preco)
        
        # Log to CSV (maintaining original functionality)
        with open(self.log_file, "a") as f:
            f.write(f"{timestamp},{tipo},{par},{quantidade:.8f},{preco:.8f},{total:.8f}\n")
        
        # Log to database
        if hasattr(self, 'current_trading_id'):
            self.db.add_entrada(
                trading_id=self.current_trading_id,
                type=tipo,
                codigo_ativo=par,
                value=total,
                quantidade=quantidade
            )    


if __name__ == "__main__":
    bot = CryptoTradingBot()
    bot.root.mainloop()