import customtkinter

# Classes auxiliares de interface (Toast, make_label, pad_values)

def make_label(master, text, **kw):
    return customtkinter.CTkLabel(master, text=text, anchor="w", **kw)

def pad_values(valores, largura=22):
            return [v.ljust(largura) for v in valores]
        
class Toast(customtkinter.CTkToplevel):
    active_toasts = []

    def __init__(self, master, text, **kwargs):
        super().__init__(master, **kwargs)
        self.overrideredirect(True)
        self.attributes("-topmost", True)

        # frame fundo (não deixa expandir)
        frame = customtkinter.CTkFrame(self, fg_color="#333333", corner_radius=8)
        frame.pack(padx=1, pady=1)  # sem expand

        # texto
        label = customtkinter.CTkLabel(
            frame, text=text,
            text_color="white",
            anchor="w",
            padx=10, pady=5
        )
        label.pack(side="left")

        # botão X
        close_btn = customtkinter.CTkButton(
            frame, text="✕",
            width=20, height=20,
            fg_color="transparent",
            hover_color="#555555",
            text_color="white",
            command=self._close
        )
        close_btn.pack(side="right", padx=5, pady=5)

        # força janela no tamanho mínimo possível
        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()  # usa tamanho requerido
        x = sw - w - 20
        y = sh - h - 60 - sum(t.winfo_height() + 10 for t in Toast.active_toasts)
        self.geometry(f"{w}x{h}+{x}+{y}")

        Toast.active_toasts.append(self)

    def _close(self):
        if self in Toast.active_toasts:
            Toast.active_toasts.remove(self)
        self.destroy()
