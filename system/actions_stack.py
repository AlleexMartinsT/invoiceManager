import customtkinter as ctk
import utils_estoque as utils
import osg
from tkinter import ttk
from system.ui_components import make_label

class ActionsMixin:
    def _build_actions_stack(self):
        self.pages = {}
        
        # --- ÍCONE CONFIG ---
        cfg_icon_path = os.path.join("data", "config.png")
        if os.path.exists(cfg_icon_path):
            from PIL import Image
            pil_cfg = Image.open(cfg_icon_path)
            self.img_cfg = ctk.CTkImage(pil_cfg, size=(22, 22))
            btn_cfg = ctk.CTkButton(
                self.search_frame,
                image=self.img_cfg,
                text="",
                width=30,
                height=30,
                fg_color="transparent",
                command=self.show_settings_page
            )
            btn_cfg.place(relx=1.0, x=0, y=0, anchor="ne") 
        
        img_path = os.path.join("data", "logo.png")
        if os.path.exists(img_path):
            try:
                from PIL import Image
                pil_img = Image.open(img_path)
                self.img_ref = ctk.CTkImage(pil_img, size=(200, 200))
                ctk.CTkLabel(self.actions_frame, image=self.img_ref, text="").pack(pady=8)
            except Exception:
                pass
        else:
            # small title if no image
            make_label(self.actions_frame, "Ações", font=("Segoe UI", 14, "bold")).pack(pady=8)
        
        # Container das páginas abaixo da imagem
        self.page_container = ctk.CTkFrame(self.actions_frame)
        self.page_container.pack(fill="both", expand=True)

        # Agora criamos as páginas dentro do container
        self.pages["home"] = ctk.CTkFrame(self.page_container)
        self.pages["add_form"] = ctk.CTkFrame(self.page_container)
        self.pages["manage_suppliers"] = ctk.CTkFrame(self.page_container)
        self.pages["manage_conferentes"] = ctk.CTkFrame(self.page_container)
        self.pages["settings"] = ctk.CTkFrame(self.page_container)

        # construir conteúdos
        self._build_home(self.pages["home"])
        self._build_add_form(self.pages["add_form"])
        self._build_manage_suppliers(self.pages["manage_suppliers"])
        self._build_manage_conferentes(self.pages["manage_conferentes"])
        self._build_settings_page(self.pages["settings"])

        # Página inicial
        self.show_page("home")

    def _build_home(self, parent):
        self.recent_tree = ttk.Treeview(
            self.pages["home"],
            columns=("nf", "fornecedor", "cnpj", "conferente"),
            show="headings",
            height=6
        )

        # Cabeçalhos
        self.recent_tree.heading("nf", text="NF")
        self.recent_tree.heading("fornecedor", text="Fornecedor")
        self.recent_tree.heading("cnpj", text="CNPJ")
        self.recent_tree.heading("conferente", text="Conferente")

        # Larguras
        self.recent_tree.column("nf", width=80, anchor="center")
        self.recent_tree.column("fornecedor", width=120, anchor="center")
        self.recent_tree.column("cnpj", width=80, anchor="center")
        self.recent_tree.column("conferente", width=120, anchor="center")

        self.recent_tree.pack(fill="both", expand=True, padx=6, pady=6)

        ctk.CTkButton(parent, text="Atualizar tabela", command=self.refresh_table).pack(fill="x", padx=8, pady=6)
        
        # Contador de notas por conferente
        self.label_contador = ctk.CTkLabel(
            parent,
            text="",
            text_color="white",
            anchor="center",
            justify="center",
            font=("Segoe UI", 14)
        )
        self.label_contador.pack(fill="x", padx=8, pady=(0, 10))

    def update_recent_list(self):
        # Limpa antes
        for item in self.recent_tree.get_children():
            self.recent_tree.delete(item)

        notes = utils.load_notes()
        for n in reversed(notes[-5:]):  # mostra as últimas 8
            self.recent_tree.insert(
                "",
                "end",
                values=(
                    n.get("nf_number"),
                    n.get("fornecedor_name"),
                    n.get("cnpj"),
                    n.get("conferente_name")
                )
            )
    
    def show_page(self, page_key):
        for k, p in self.pages.items():
            p.pack_forget()
        self.pages[page_key].pack(fill="both", expand=True)
        # focus first widget for accessibility
        if page_key == "add_form":
            self.entry_nf.focus_set()
 