import customtkinter as ctk

class PriceFrame(ctk.CTkFrame):
    """Frame component for price display and quantity calculation"""
    def __init__(self, parent, calculate_callback, **kwargs):
        super().__init__(parent)
        
        # Remove font_style e font_size dos kwargs antes de passar para super()
        self.font_style = kwargs.pop('font_style', "Arial") if 'font_style' in kwargs else "Arial"
        self.font_size = kwargs.pop('font_size', 14) if 'font_size' in kwargs else 14
        
        # Price Label
        self.price_label = ctk.CTkLabel(
            self,
            text="Preço Atual: 0.00",
            font=(self.font_style, self.font_size)
        )
        self.price_label.pack(pady=5)
        
        # Investment value label
        self.value_label = ctk.CTkLabel(
            self,
            text="Valor a Investir (BRL):",
            font=(self.font_style, self.font_size)
        )
        self.value_label.pack(pady=5)
        
        # Investment value entry
        self.value_var = ctk.StringVar(value="100.00")
        self.value_entry = ctk.CTkEntry(
            self,
            textvariable=self.value_var,
            font=(self.font_style, self.font_size)
        )
        self.value_entry.pack(pady=5)
        
        # Calculate button
        self.calc_button = ctk.CTkButton(
            self,
            text="Calcular Quantidade",
            command=calculate_callback,
            font=(self.font_style, self.font_size)
        )
        self.calc_button.pack(pady=5)
    
    def update_price(self, price: float):
        """Update the displayed price"""
        self.price_label.configure(text=f"Preço Atual: {price:.8f}")
    
    def get_investment_value(self) -> float:
        """Get the current investment value"""
        return float(self.value_var.get())