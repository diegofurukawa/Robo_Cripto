# src/interface/components/metrics_frame.py
import customtkinter as ctk

class MetricsFrame(ctk.CTkFrame):
    """Frame component for trading metrics display"""
    def __init__(self, parent, **kwargs):
        # Extraia os argumentos específicos e remova-os de kwargs
        self.font_style = kwargs.pop('font_style', "Arial")
        self.font_size = kwargs.pop('font_size', 14)

        # Inicialize o frame
        super().__init__(parent, **kwargs)
        
        self.media_metrics = ctk.CTkFrame(self)
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
        
    def update_metrics(self, media_rapida: float, media_lenta: float):
        """Update the moving averages display"""
        self.media_rapida_label.configure(text=f"Média Rápida: {media_rapida:.8f}")
        self.media_lenta_label.configure(text=f"Média Lenta: {media_lenta:.8f}")

