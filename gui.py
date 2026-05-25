import queue
import threading
from pathlib import Path

import customtkinter as ctk
import requests
from PIL import Image, ImageEnhance, ImageFilter, ImageOps

API_BASE_URL = "http://localhost:5000/api"
DEFAULT_REQUEST_TIMEOUT = 8
CHAT_REQUEST_TIMEOUT = 10
LOGIN_USERNAME = "admin"
LOGIN_PASSWORD = "admin123"
BACKEND_UNAVAILABLE_MESSAGE = "API indisponible. Lancez d'abord le backend avec : python run.py"
BASE_DIR = Path(__file__).resolve().parent
BACKGROUND_IMAGE_PATH = BASE_DIR / "assets" / "pngtree-an-old-bookcase-in-a-library-picture-image_2760144.jpg"

COLORS = {
    "fallback_bg": "#0f1724",
    "night": "#122033",
    "night_soft": "#1c2e45",
    "ink": "#f5efe6",
    "ink_dark": "#1f2937",
    "muted": "#c7c0b5",
    "muted_dark": "#6b7280",
    "card": "#f7f2ea",
    "card_alt": "#efe5d5",
    "glass": "#f8f3ec",
    "glass_alt": "#f4ede3",
    "border": "#dcc9ac",
    "gold": "#c9a96b",
    "gold_hover": "#b89354",
    "primary": "#1d4f91",
    "primary_hover": "#163d72",
    "success": "#2f7d57",
    "success_hover": "#256447",
    "danger": "#a03b33",
    "danger_hover": "#7d2d28",
    "warning": "#b8860b",
    "warning_hover": "#916b07",
    "overlay_dark": "#101826",
    "chat_user": "#e7dcc8",
    "chat_assistant": "#f7f2ea",
    "badge": "#e9d9b6",
}

STATUS_COLORS = {
    "info": COLORS["gold"],
    "success": COLORS["success"],
    "error": COLORS["danger"],
    "neutral": COLORS["muted_dark"],
}

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Chatbot AI")
        self.geometry("1280x780")
        self.minsize(1180, 720)
        self.configure(fg_color=COLORS["fallback_bg"])

        self.is_authenticated = False
        self.current_session = 0
        self.selected_id = None
        self.current_books = []
        self.catalog_busy = False
        self.chat_busy = False
        self.async_queue = queue.Queue()
        self.current_view = "login"
        self.background_source = self._load_background_source()
        self.background_cache = {}
        self.background_refresh_job = None
        self.catalog_loader_job = None
        self.chat_loader_job = None
        self.window_fade_job = None

        self.background_label = ctk.CTkLabel(self, text="", fg_color=COLORS["fallback_bg"])
        self.background_label.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.login_screen = ctk.CTkFrame(self, fg_color="transparent")
        self.transition_screen = ctk.CTkFrame(self, fg_color="transparent")
        self.app_shell = ctk.CTkFrame(self, fg_color="transparent")

        self._build_login_screen()
        self._build_transition_screen()
        self._build_app_shell()

        self.bind("<Configure>", self._schedule_background_refresh)
        self._show_login_screen(initial=True)
        self.after(80, self._drain_async_queue)
        self.after(120, self._refresh_background)

    def _load_background_source(self):
        if not BACKGROUND_IMAGE_PATH.exists():
            return None
        try:
            return Image.open(BACKGROUND_IMAGE_PATH).convert("RGB")
        except Exception:
            return None

    def _schedule_background_refresh(self, event=None):
        if event is not None and event.widget is not self:
            return
        if self.background_refresh_job:
            self.after_cancel(self.background_refresh_job)
        self.background_refresh_job = self.after(120, self._refresh_background)

    def _refresh_background(self):
        self.background_refresh_job = None
        width = max(self.winfo_width(), 1180)
        height = max(self.winfo_height(), 720)
        mode = self.current_view if self.current_view in {"login", "transition", "app"} else "login"

        if self.background_source is None:
            self.background_label.configure(image=None, fg_color=COLORS["fallback_bg"])
            return

        cache_key = (mode, width, height)
        if cache_key not in self.background_cache:
            base = ImageOps.fit(self.background_source, (width, height), method=Image.Resampling.LANCZOS)
            base = base.convert("RGBA")

            if mode == "login":
                styled = ImageEnhance.Contrast(base).enhance(1.08)
                styled = ImageEnhance.Brightness(styled).enhance(0.68)
                overlay = Image.new("RGBA", styled.size, (16, 24, 38, 150))
            elif mode == "transition":
                styled = base.filter(ImageFilter.GaussianBlur(2.5))
                styled = ImageEnhance.Brightness(styled).enhance(0.62)
                overlay = Image.new("RGBA", styled.size, (18, 29, 45, 165))
            else:
                styled = base.filter(ImageFilter.GaussianBlur(5.5))
                styled = ImageEnhance.Brightness(styled).enhance(0.72)
                styled = ImageEnhance.Color(styled).enhance(0.82)
                overlay = Image.new("RGBA", styled.size, (22, 30, 42, 132))

            composed = Image.alpha_composite(styled, overlay).convert("RGB")
            self.background_cache[cache_key] = ctk.CTkImage(light_image=composed, dark_image=composed, size=(width, height))

        self.active_background = self.background_cache[cache_key]
        self.background_label.configure(image=self.active_background, text="")
        self.background_label.lower()

    def _animate_window_alpha(self, start=0.94, end=1.0, steps=8, delay=32):
        if self.window_fade_job:
            self.after_cancel(self.window_fade_job)
            self.window_fade_job = None

        delta = (end - start) / max(steps, 1)
        self.attributes("-alpha", start)

        def step(index=0):
            value = min(end, start + delta * index) if end >= start else max(end, start + delta * index)
            self.attributes("-alpha", value)
            if index >= steps:
                return
            self.window_fade_job = self.after(delay, lambda: step(index + 1))

        step(0)

    def _build_login_screen(self):
        self.login_background_overlay = ctk.CTkFrame(self.login_screen, fg_color="transparent")
        self.login_background_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.login_quote = ctk.CTkLabel(
            self.login_screen,
            text="Votre bibliotheque intelligente alimentee par l'IA",
            font=("Segoe UI", 22, "bold"),
            text_color="#f7efe2",
        )
        self.login_quote.place(relx=0.04, rely=0.9, anchor="w")

        self.login_quote_subtitle = ctk.CTkLabel(
            self.login_screen,
            text="Un espace premium pour piloter vos livres, vos recherches et vos conversations IA.",
            font=("Segoe UI", 12),
            text_color="#dbcdb7",
        )
        self.login_quote_subtitle.place(relx=0.04, rely=0.94, anchor="w")

        shadow = ctk.CTkFrame(self.login_screen, fg_color="#0b1220", corner_radius=30, width=470, height=540)
        shadow.place(relx=0.5, rely=0.505, anchor="center")

        self.login_card = ctk.CTkFrame(
            self.login_screen,
            fg_color=COLORS["glass"],
            corner_radius=28,
            border_width=1,
            border_color=COLORS["border"],
            width=460,
            height=530,
        )
        self.login_card.place(relx=0.5, rely=0.5, anchor="center")
        self.login_card.pack_propagate(False)

        icon_badge = ctk.CTkLabel(
            self.login_card,
            text="📚",
            width=68,
            height=68,
            corner_radius=34,
            fg_color=COLORS["badge"],
            text_color=COLORS["night"],
            font=("Segoe UI Emoji", 30, "bold"),
        )
        icon_badge.pack(pady=(34, 14))

        ctk.CTkLabel(
            self.login_card,
            text="Library Chatbot AI",
            font=("Segoe UI", 30, "bold"),
            text_color=COLORS["night"],
        ).pack()

        ctk.CTkLabel(
            self.login_card,
            text="Entrez dans une bibliotheque premium, elegante et assistee par l'IA.",
            font=("Segoe UI", 13),
            text_color=COLORS["muted_dark"],
            wraplength=330,
            justify="center",
        ).pack(pady=(8, 18))

        self.login_chip = ctk.CTkLabel(
            self.login_card,
            text="Connexion securisee pour la demonstration",
            fg_color=COLORS["card_alt"],
            corner_radius=14,
            text_color=COLORS["night_soft"],
            font=("Segoe UI", 11, "bold"),
            padx=16,
            pady=8,
        )
        self.login_chip.pack(pady=(0, 18))

        self.login_username = self._styled_entry(self.login_card, "Nom d'utilisateur", dark=False)
        self.login_password = self._styled_entry(self.login_card, "Mot de passe", show="*", dark=False)

        credentials_card = ctk.CTkFrame(
            self.login_card,
            fg_color=COLORS["card_alt"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["border"],
        )
        credentials_card.pack(fill="x", padx=34, pady=(10, 18))
        ctk.CTkLabel(
            credentials_card,
            text="Acces demo",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["night"],
        ).pack(anchor="w", padx=16, pady=(14, 3))
        ctk.CTkLabel(
            credentials_card,
            text="username : admin\npassword : admin123",
            justify="left",
            font=("Consolas", 12),
            text_color=COLORS["muted_dark"],
        ).pack(anchor="w", padx=16, pady=(0, 14))

        self.login_feedback = ctk.CTkLabel(
            self.login_card,
            text="",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["danger"],
        )
        self.login_feedback.pack(anchor="w", padx=34, pady=(0, 8))

        self.login_button = ctk.CTkButton(
            self.login_card,
            text="Entrer dans la bibliotheque",
            command=self.login,
            height=48,
            corner_radius=16,
            fg_color=COLORS["gold"],
            hover_color=COLORS["gold_hover"],
            text_color=COLORS["night"],
            font=("Segoe UI", 14, "bold"),
        )
        self.login_button.pack(fill="x", padx=34, pady=(4, 10))

        self.login_hint = ctk.CTkLabel(
            self.login_card,
            text="Acces local stable, sans JWT ni base utilisateurs.",
            font=("Segoe UI", 11),
            text_color=COLORS["muted_dark"],
        )
        self.login_hint.pack(pady=(0, 16))

        self.login_username.bind("<Return>", lambda _: self.login())
        self.login_password.bind("<Return>", lambda _: self.login())

    def _build_transition_screen(self):
        self.transition_overlay = ctk.CTkFrame(self.transition_screen, fg_color="transparent")
        self.transition_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

        card = ctk.CTkFrame(
            self.transition_screen,
            fg_color=COLORS["glass"],
            corner_radius=28,
            border_width=1,
            border_color=COLORS["border"],
            width=470,
            height=280,
        )
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        self.transition_title = ctk.CTkLabel(
            card,
            text="Bienvenue dans votre bibliotheque",
            font=("Segoe UI", 27, "bold"),
            text_color=COLORS["night"],
        )
        self.transition_title.pack(pady=(42, 10))

        self.transition_label = ctk.CTkLabel(
            card,
            text="Preparation d'une experience de lecture premium...",
            font=("Segoe UI", 13),
            text_color=COLORS["muted_dark"],
        )
        self.transition_label.pack()

        self.transition_bar = ctk.CTkProgressBar(
            card,
            width=300,
            height=12,
            corner_radius=20,
            progress_color=COLORS["gold"],
            fg_color="#d8d0c5",
        )
        self.transition_bar.pack(pady=(28, 0))
        self.transition_bar.set(0)

        self.transition_badge = ctk.CTkLabel(
            card,
            text="📚 IA activee",
            fg_color=COLORS["card_alt"],
            corner_radius=16,
            text_color=COLORS["night_soft"],
            font=("Segoe UI", 11, "bold"),
            padx=14,
            pady=8,
        )
        self.transition_badge.pack(pady=(18, 0))

    def _build_app_shell(self):
        self.app_scrim = ctk.CTkFrame(self.app_shell, fg_color="transparent")
        self.app_scrim.place(relx=0, rely=0, relwidth=1, relheight=1)

        self._build_header()
        self._build_tabs()
        self._build_livres_tab()
        self._build_chat_tab()

    def _build_header(self):
        header_shadow = ctk.CTkFrame(self.app_shell, fg_color="#0d1320", corner_radius=26, height=96)
        header_shadow.place(relx=0.5, rely=0.065, anchor="n", relwidth=0.965)

        header = ctk.CTkFrame(
            self.app_shell,
            fg_color=COLORS["glass"],
            corner_radius=24,
            border_width=1,
            border_color=COLORS["border"],
        )
        header.pack(fill="x", padx=18, pady=(18, 10))

        left = ctk.CTkFrame(header, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True, padx=22, pady=18)

        title_row = ctk.CTkFrame(left, fg_color="transparent")
        title_row.pack(anchor="w")

        ctk.CTkLabel(
            title_row,
            text="📚",
            font=("Segoe UI Emoji", 24),
            text_color=COLORS["gold"],
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            title_row,
            text="Library Chatbot AI",
            font=("Segoe UI", 28, "bold"),
            text_color=COLORS["night"],
        ).pack(side="left")

        ctk.CTkLabel(
            left,
            text="Votre bibliotheque intelligente alimentee par l'IA, dans une ambiance premium et immersive.",
            font=("Segoe UI", 13),
            text_color=COLORS["muted_dark"],
            justify="left",
            wraplength=760,
        ).pack(anchor="w", pady=(4, 0))

        right = ctk.CTkFrame(header, fg_color="transparent")
        right.pack(side="right", padx=22, pady=18)

        self.user_badge = ctk.CTkLabel(
            right,
            text="Connecte : admin",
            fg_color=COLORS["card_alt"],
            corner_radius=16,
            text_color=COLORS["night"],
            font=("Segoe UI", 12, "bold"),
            padx=18,
            pady=10,
        )
        self.user_badge.pack(side="left", padx=(0, 10))

        self.logout_button = ctk.CTkButton(
            right,
            text="Deconnexion",
            command=self.logout,
            width=132,
            height=42,
            corner_radius=16,
            fg_color=COLORS["danger"],
            hover_color=COLORS["danger_hover"],
            text_color="#fff8ef",
            font=("Segoe UI", 13, "bold"),
        )
        self.logout_button.pack(side="left")

    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(
            self.app_shell,
            fg_color=COLORS["glass"],
            corner_radius=24,
            border_width=1,
            border_color=COLORS["border"],
            segmented_button_fg_color=COLORS["card_alt"],
            segmented_button_selected_color=COLORS["gold"],
            segmented_button_selected_hover_color=COLORS["gold_hover"],
            segmented_button_unselected_color=COLORS["card_alt"],
            segmented_button_unselected_hover_color="#e7dac4",
            text_color=COLORS["night"],
        )
        self.tabview.pack(fill="both", expand=True, padx=18, pady=(0, 18))

        self.tab_livres = self.tabview.add("Catalogue")
        self.tab_chat = self.tabview.add("Assistant")

    def _build_livres_tab(self):
        root = ctk.CTkFrame(self.tab_livres, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=14, pady=14)

        form = ctk.CTkFrame(
            root,
            fg_color=COLORS["glass_alt"],
            corner_radius=22,
            border_width=1,
            border_color=COLORS["border"],
            width=372,
        )
        form.pack(side="left", fill="y", padx=(0, 12))
        form.pack_propagate(False)

        ctk.CTkLabel(
            form,
            text="Gestion des livres",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["night"],
        ).pack(anchor="w", padx=20, pady=(20, 4))

        ctk.CTkLabel(
            form,
            text="Ajoutez, mettez a jour ou supprimez vos references dans une interface plus premium.",
            font=("Segoe UI", 12),
            text_color=COLORS["muted_dark"],
            wraplength=320,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 14))

        self.e_titre = self._styled_entry(form, "Titre")
        self.e_auteur = self._styled_entry(form, "Auteur")
        self.e_categorie = self._styled_entry(form, "Categorie")
        self.e_annee = self._styled_entry(form, "Annee")
        self.e_quantite = self._styled_entry(form, "Quantite")

        self.e_statut = ctk.CTkComboBox(
            form,
            values=["disponible", "emprunte", "reserve"],
            width=308,
            height=44,
            corner_radius=15,
            fg_color=COLORS["card"],
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color=COLORS["card"],
            border_color=COLORS["border"],
            text_color=COLORS["night"],
            font=("Segoe UI", 13),
        )
        self.e_statut.set("disponible")
        self.e_statut.pack(padx=20, pady=8)

        self.add_button = self._action_button(form, "Ajouter", self.add_livre, COLORS["success"], COLORS["success_hover"], "#f7efe7")
        self.update_button = self._action_button(form, "Modifier", self.update_livre, COLORS["primary"], COLORS["primary_hover"], "#f7efe7")
        self.delete_button = self._action_button(form, "Supprimer", self.delete_livre, COLORS["danger"], COLORS["danger_hover"], "#f7efe7")
        self.refresh_button = self._action_button(form, "Rafraichir", self.load_livres, "#72839a", "#5e6f86", "#f7efe7")

        search = ctk.CTkFrame(form, fg_color=COLORS["card"], corner_radius=18, border_width=1, border_color=COLORS["border"])
        search.pack(fill="x", padx=20, pady=(12, 12))
        self.e_search = ctk.CTkEntry(
            search,
            placeholder_text="Rechercher titre ou auteur...",
            height=42,
            fg_color="#fbf8f2",
            text_color=COLORS["night"],
            border_color=COLORS["border"],
            corner_radius=13,
            font=("Segoe UI", 13),
        )
        self.e_search.pack(side="left", fill="x", expand=True, padx=(10, 6), pady=10)
        self.search_button = ctk.CTkButton(
            search,
            text="Go",
            width=58,
            height=42,
            corner_radius=13,
            command=self.search_livre,
            fg_color=COLORS["gold"],
            hover_color=COLORS["gold_hover"],
            text_color=COLORS["night"],
            font=("Segoe UI", 13, "bold"),
        )
        self.search_button.pack(side="left", padx=(0, 10), pady=10)

        self.status_label = ctk.CTkLabel(
            form,
            text="Connectez-vous pour charger le catalogue.",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["muted_dark"],
            justify="left",
            wraplength=320,
        )
        self.status_label.pack(anchor="w", padx=20, pady=(0, 10))

        self.catalog_loader_label = ctk.CTkLabel(
            form,
            text="",
            font=("Segoe UI", 11),
            text_color=COLORS["gold"],
        )
        self.catalog_loader_label.pack(anchor="w", padx=20, pady=(0, 6))

        self.catalog_loader = ctk.CTkProgressBar(
            form,
            mode="indeterminate",
            height=10,
            corner_radius=20,
            progress_color=COLORS["gold"],
            fg_color="#d7d0c6",
        )
        self.catalog_loader.pack(fill="x", padx=20, pady=(0, 18))
        self.catalog_loader.pack_forget()

        table_panel = ctk.CTkFrame(
            root,
            fg_color=COLORS["glass"],
            corner_radius=22,
            border_width=1,
            border_color=COLORS["border"],
        )
        table_panel.pack(side="right", fill="both", expand=True)

        table_header = ctk.CTkFrame(table_panel, fg_color="transparent")
        table_header.pack(fill="x", padx=16, pady=(16, 10))

        left = ctk.CTkFrame(table_header, fg_color="transparent")
        left.pack(side="left")
        ctk.CTkLabel(
            left,
            text="Catalogue en direct",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["night"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            left,
            text="Selectionnez une ligne pour injecter ses valeurs dans le formulaire.",
            font=("Segoe UI", 12),
            text_color=COLORS["muted_dark"],
        ).pack(anchor="w", pady=(4, 0))

        self.table_summary = ctk.CTkLabel(
            table_header,
            text="Aucune donnee chargee",
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["card_alt"],
            corner_radius=14,
            text_color=COLORS["night_soft"],
            padx=14,
            pady=8,
        )
        self.table_summary.pack(side="right")

        headers = ["ID", "Titre", "Auteur", "Categorie", "Annee", "Qte", "Statut"]
        head_row = ctk.CTkFrame(table_panel, fg_color="transparent")
        head_row.pack(fill="x", padx=16)
        for column, header in enumerate(headers):
            ctk.CTkLabel(
                head_row,
                text=header,
                font=("Segoe UI", 12, "bold"),
                fg_color=COLORS["card_alt"],
                text_color=COLORS["night"],
                corner_radius=14,
                padx=10,
                pady=8,
            ).grid(row=0, column=column, padx=4, pady=(0, 8), sticky="ew")

        self.rows_frame = ctk.CTkScrollableFrame(
            table_panel,
            fg_color="#faf6f0",
            corner_radius=18,
            scrollbar_button_color=COLORS["gold"],
            scrollbar_button_hover_color=COLORS["gold_hover"],
        )
        self.rows_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        for column in range(7):
            head_row.grid_columnconfigure(column, weight=1)
            self.rows_frame.grid_columnconfigure(column, weight=1)

        self._show_empty("Connectez-vous pour afficher le catalogue.")

    def _build_chat_tab(self):
        root = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=14, pady=14)

        panel = ctk.CTkFrame(
            root,
            fg_color=COLORS["glass"],
            corner_radius=22,
            border_width=1,
            border_color=COLORS["border"],
        )
        panel.pack(fill="both", expand=True)

        top = ctk.CTkFrame(panel, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(18, 10))

        title_row = ctk.CTkFrame(top, fg_color="transparent")
        title_row.pack(side="left")
        ctk.CTkLabel(
            title_row,
            text="🤖",
            font=("Segoe UI Emoji", 24),
            text_color=COLORS["gold"],
        ).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            title_row,
            text="Assistant IA",
            font=("Segoe UI", 22, "bold"),
            text_color=COLORS["night"],
        ).pack(side="left")

        self.chat_status_label = ctk.CTkLabel(
            top,
            text="Pret a repondre apres connexion.",
            font=("Segoe UI", 12, "bold"),
            fg_color=COLORS["card_alt"],
            corner_radius=14,
            text_color=COLORS["night_soft"],
            padx=14,
            pady=8,
        )
        self.chat_status_label.pack(side="right")

        self.chat_messages = ctk.CTkScrollableFrame(
            panel,
            fg_color="#faf6f0",
            corner_radius=18,
            scrollbar_button_color=COLORS["gold"],
            scrollbar_button_hover_color=COLORS["gold_hover"],
        )
        self.chat_messages.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        bottom = ctk.CTkFrame(panel, fg_color="transparent")
        bottom.pack(fill="x", padx=18, pady=(0, 18))

        self.chat_loader_label = ctk.CTkLabel(
            bottom,
            text="",
            font=("Segoe UI", 11),
            text_color=COLORS["gold"],
        )
        self.chat_loader_label.pack(anchor="w", pady=(0, 6))

        self.chat_loader = ctk.CTkProgressBar(
            bottom,
            mode="indeterminate",
            height=10,
            corner_radius=20,
            progress_color=COLORS["gold"],
            fg_color="#d7d0c6",
        )
        self.chat_loader.pack(fill="x", pady=(0, 10))
        self.chat_loader.pack_forget()

        input_row = ctk.CTkFrame(bottom, fg_color="transparent")
        input_row.pack(fill="x")

        self.e_question = ctk.CTkEntry(
            input_row,
            placeholder_text="Posez votre question sur la bibliotheque...",
            height=46,
            fg_color="#fbf8f2",
            text_color=COLORS["night"],
            border_color=COLORS["border"],
            corner_radius=15,
            font=("Segoe UI", 13),
        )
        self.e_question.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.e_question.bind("<Return>", lambda _: self.send_message())

        self.send_button = ctk.CTkButton(
            input_row,
            text="Envoyer",
            width=148,
            height=46,
            corner_radius=15,
            command=self.send_message,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
            text_color="#f7efe7",
            font=("Segoe UI", 13, "bold"),
        )
        self.send_button.pack(side="right")

        self._reset_chat()

    def _styled_entry(self, parent, placeholder, show=None, dark=False):
        fg_color = COLORS["card"] if not dark else COLORS["night_soft"]
        text_color = COLORS["night"] if not dark else COLORS["ink"]
        border_color = COLORS["border"] if not dark else "#44546a"
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            width=308,
            height=44,
            corner_radius=15,
            show=show,
            fg_color=fg_color,
            text_color=text_color,
            border_color=border_color,
            font=("Segoe UI", 13),
        )
        entry.pack(padx=20, pady=8)
        return entry

    def _action_button(self, parent, text, command, color, hover, text_color):
        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=color,
            hover_color=hover,
            text_color=text_color,
            height=42,
            corner_radius=15,
            font=("Segoe UI", 13, "bold"),
        )
        button.pack(fill="x", padx=20, pady=5)
        return button

    def _show_login_screen(self, initial=False):
        self.current_view = "login"
        self._refresh_background()
        self.transition_screen.place_forget()
        self.app_shell.place_forget()
        self.login_screen.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.login_feedback.configure(text="")
        self.after(80, self.login_username.focus)
        self._animate_window_alpha(0.9 if initial else 0.94, 1.0)

    def _show_transition_screen(self):
        self.current_view = "transition"
        self._refresh_background()
        self.login_screen.place_forget()
        self.app_shell.place_forget()
        self.transition_bar.set(0)
        self.transition_label.configure(text="Preparation de votre espace premium...")
        self.transition_screen.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._animate_window_alpha(0.95, 1.0)
        self._advance_transition(0)

    def _show_app_shell(self):
        self.current_view = "app"
        self._refresh_background()
        self.transition_screen.place_forget()
        self.login_screen.place_forget()
        self.app_shell.place(relx=0, rely=0, relwidth=1, relheight=1)
        self._animate_window_alpha(0.95, 1.0)

    def _advance_transition(self, step):
        progress = min(step / 10, 1)
        self.transition_bar.set(progress)
        if step < 10:
            self.transition_label.configure(text=f"Harmonisation de l'experience {step + 1}/10")
            self.after(70, lambda: self._advance_transition(step + 1))
            return
        self._show_app_shell()
        self._set_catalog_status("Connexion reussie. Chargement du catalogue...", "info")
        self._set_chat_status("Connecte. L'assistant est pret.", "success")
        self._play_welcome_sequence()
        self.after(120, self.load_livres)

    def _play_welcome_sequence(self):
        username = self.user_badge.cget("text").replace("Connecte : ", "")
        self.user_badge.configure(text=f"Bienvenue, {username}", fg_color=COLORS["gold"], text_color=COLORS["night"])
        self.after(2200, lambda: self.user_badge.configure(text=f"Connecte : {username}", fg_color=COLORS["card_alt"], text_color=COLORS["night"]))

    def _set_catalog_status(self, text, kind="neutral"):
        self.status_label.configure(text=text, text_color=STATUS_COLORS.get(kind, COLORS["muted_dark"]))

    def _set_chat_status(self, text, kind="neutral"):
        self.chat_status_label.configure(text=text, text_color=STATUS_COLORS.get(kind, COLORS["night_soft"]))
        if kind == "error":
            self.chat_status_label.configure(fg_color="#f3ddd8")
        elif kind == "success":
            self.chat_status_label.configure(fg_color="#dfeee5")
        elif kind == "info":
            self.chat_status_label.configure(fg_color="#efe2c7")
        else:
            self.chat_status_label.configure(fg_color=COLORS["card_alt"])

    def _tick_loader_label(self, kind, base_text, step=0):
        dots = "." * (step % 4)
        label = self.catalog_loader_label if kind == "catalog" else self.chat_loader_label
        busy = self.catalog_busy if kind == "catalog" else self.chat_busy
        label.configure(text=f"{base_text}{dots}")
        if not busy:
            return
        job_name = "catalog_loader_job" if kind == "catalog" else "chat_loader_job"
        next_job = self.after(280, lambda: self._tick_loader_label(kind, base_text, step + 1))
        setattr(self, job_name, next_job)

    def _set_catalog_busy(self, busy, message="Chargement des livres"):
        self.catalog_busy = busy
        state = "disabled" if busy else "normal"
        for button in (self.add_button, self.update_button, self.delete_button, self.refresh_button, self.search_button):
            button.configure(state=state)
        self.e_search.configure(state=state)
        if busy:
            self.catalog_loader.pack(fill="x", padx=20, pady=(0, 18))
            self.catalog_loader.start()
            self._set_catalog_status(f"{message}...", "info")
            self._tick_loader_label("catalog", message)
        else:
            if self.catalog_loader_job:
                self.after_cancel(self.catalog_loader_job)
                self.catalog_loader_job = None
            self.catalog_loader_label.configure(text="")
            self.catalog_loader.stop()
            self.catalog_loader.pack_forget()

    def _set_chat_busy(self, busy, message="Reponse en cours"):
        self.chat_busy = busy
        state = "disabled" if busy else "normal"
        self.send_button.configure(state=state)
        self.e_question.configure(state=state)
        if busy:
            self.chat_loader.pack(fill="x", pady=(0, 10))
            self.chat_loader.start()
            self._set_chat_status(f"{message}...", "info")
            self._tick_loader_label("chat", message)
        else:
            if self.chat_loader_job:
                self.after_cancel(self.chat_loader_job)
                self.chat_loader_job = None
            self.chat_loader_label.configure(text="")
            self.chat_loader.stop()
            self.chat_loader.pack_forget()

    def _session_valid(self, session_id):
        return self.is_authenticated and session_id == self.current_session

    def _run_async(self, worker, callback):
        def runner():
            result = worker()
            self.async_queue.put((callback, result))

        threading.Thread(target=runner, daemon=True).start()

    def _drain_async_queue(self):
        while not self.async_queue.empty():
            callback, result = self.async_queue.get()
            callback(result)
        self.after(80, self._drain_async_queue)

    def _request_json(self, method, path, timeout=DEFAULT_REQUEST_TIMEOUT, **kwargs):
        if not self.is_authenticated:
            return None, "Connectez-vous pour acceder a l'application."

        try:
            response = requests.request(method, f"{API_BASE_URL}{path}", timeout=timeout, **kwargs)
        except requests.Timeout:
            return None, "Le serveur met trop de temps a repondre. Reessayez dans un instant."
        except requests.ConnectionError:
            return None, BACKEND_UNAVAILABLE_MESSAGE
        except requests.RequestException:
            return None, BACKEND_UNAVAILABLE_MESSAGE

        try:
            payload = response.json() if response.content else None
        except ValueError:
            payload = None

        if response.ok:
            return payload, None

        if response.status_code >= 500:
            if isinstance(payload, dict) and payload.get("error"):
                return payload, self._humanize_api_error(payload["error"])
            return payload, "Une erreur serveur est survenue. Reessayez plus tard."

        if isinstance(payload, dict) and payload.get("error"):
            return payload, self._humanize_api_error(payload["error"])

        return payload, "La requete n'a pas pu etre finalisee."

    def _humanize_api_error(self, message):
        text = str(message).strip()
        if not text:
            return "Une erreur est survenue. Merci de reessayer."
        if "Ollama indisponible" in text:
            return "Le chatbot est indisponible. Verifiez Ollama et le modele mistral."
        if "Impossible" in text or "Question vide" in text or "Champ manquant" in text:
            return text
        return "Une erreur est survenue. Merci de reessayer."

    def _form_data(self):
        titre = self.e_titre.get().strip()
        auteur = self.e_auteur.get().strip()
        categorie = self.e_categorie.get().strip()
        statut = self.e_statut.get().strip()
        annee_raw = self.e_annee.get().strip()
        quantite_raw = self.e_quantite.get().strip()

        if not titre or not auteur:
            return None, "Le titre et l'auteur sont obligatoires."
        if not annee_raw or not quantite_raw:
            return None, "L'annee et la quantite sont obligatoires."

        try:
            annee = int(annee_raw)
            quantite = int(quantite_raw)
        except ValueError:
            return None, "Annee et quantite doivent etre numeriques."

        return {
            "titre": titre,
            "auteur": auteur,
            "categorie": categorie,
            "annee": annee,
            "quantite": quantite,
            "statut": statut or "disponible",
        }, None

    def _clear_form(self):
        for widget in (self.e_titre, self.e_auteur, self.e_categorie, self.e_annee, self.e_quantite):
            widget.delete(0, "end")
        self.e_statut.set("disponible")
        self.selected_id = None

    def _clear_books_table(self):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

    def _show_empty(self, text):
        self._clear_books_table()
        empty_card = ctk.CTkFrame(
            self.rows_frame,
            fg_color=COLORS["card"],
            corner_radius=18,
            border_width=1,
            border_color=COLORS["border"],
        )
        empty_card.grid(row=0, column=0, columnspan=7, padx=20, pady=28, sticky="ew")
        ctk.CTkLabel(
            empty_card,
            text="Aucune donnee a afficher",
            font=("Segoe UI", 16, "bold"),
            text_color=COLORS["night"],
        ).pack(anchor="w", padx=18, pady=(16, 6))
        ctk.CTkLabel(
            empty_card,
            text=text,
            text_color=COLORS["muted_dark"],
            font=("Segoe UI", 13),
            justify="left",
            wraplength=680,
        ).pack(anchor="w", padx=18, pady=(0, 16))

    def _render_livres(self, livres):
        self._clear_books_table()
        for row_index, livre in enumerate(livres):
            row_color = COLORS["card"] if row_index % 2 == 0 else "#efe5d8"
            values = [
                livre.get("id", ""),
                livre.get("titre", ""),
                livre.get("auteur", ""),
                livre.get("categorie", ""),
                livre.get("annee", ""),
                livre.get("quantite", ""),
                livre.get("statut", ""),
            ]
            for column, value in enumerate(values):
                cell = ctk.CTkLabel(
                    self.rows_frame,
                    text=str(value),
                    cursor="hand2",
                    fg_color=row_color,
                    text_color=COLORS["night"],
                    corner_radius=12,
                    padx=8,
                    pady=10,
                    font=("Segoe UI", 12),
                )
                cell.grid(row=row_index, column=column, padx=4, pady=3, sticky="ew")
                cell.bind("<Button-1>", lambda _, book=livre: self.select_livre(book))

    def _reset_catalog_view(self):
        self.current_books = []
        self.table_summary.configure(text="Aucune donnee chargee")
        self._show_empty("Connectez-vous pour afficher le catalogue.")
        self._set_catalog_status("Connectez-vous pour charger le catalogue.", "neutral")

    def _reset_chat(self):
        for widget in self.chat_messages.winfo_children():
            widget.destroy()
        self.append_chat("📚 IA", "Bonjour. Connectez-vous puis posez votre question sur la bibliotheque.", role="assistant")

    def _scroll_chat_to_bottom(self):
        self.after(50, lambda: self.chat_messages._parent_canvas.yview_moveto(1.0))

    def append_chat(self, sender, message, role="assistant"):
        row = ctk.CTkFrame(self.chat_messages, fg_color="transparent")
        row.pack(fill="x", padx=8, pady=6)

        bubble_color = COLORS["chat_user"] if role == "user" else COLORS["chat_assistant"]
        title_color = COLORS["primary"] if role == "user" else COLORS["gold"]
        anchor = "e" if role == "user" else "w"

        bubble = ctk.CTkFrame(
            row,
            fg_color=bubble_color,
            corner_radius=16,
            border_width=1,
            border_color=COLORS["border"],
        )
        bubble.pack(anchor=anchor, padx=6)

        ctk.CTkLabel(
            bubble,
            text=sender,
            font=("Segoe UI", 11, "bold"),
            text_color=title_color,
        ).pack(anchor="w", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            bubble,
            text=message,
            font=("Segoe UI", 13),
            text_color=COLORS["night"],
            justify="left",
            wraplength=640,
        ).pack(anchor="w", padx=14, pady=(0, 12))

        self._scroll_chat_to_bottom()

    def login(self):
        username = self.login_username.get().strip()
        password = self.login_password.get().strip()

        if username != LOGIN_USERNAME or password != LOGIN_PASSWORD:
            self.login_feedback.configure(text="Identifiants incorrects")
            return

        self.is_authenticated = True
        self.current_session += 1
        self.user_badge.configure(text=f"Connecte : {username}")
        self.login_feedback.configure(text="")
        self._show_transition_screen()

    def logout(self):
        self.is_authenticated = False
        self.current_session += 1
        self.selected_id = None
        self._set_catalog_busy(False)
        self._set_chat_busy(False)
        self._clear_form()
        self._clear_books_table()
        self._reset_catalog_view()
        self._reset_chat()
        self.e_search.delete(0, "end")
        self.e_question.delete(0, "end")
        self.login_username.delete(0, "end")
        self.login_password.delete(0, "end")
        self.login_feedback.configure(text="")
        self._set_chat_status("Session fermee. Reconnectez-vous pour utiliser l'assistant.", "neutral")
        self._show_login_screen()

    def select_livre(self, livre):
        self.selected_id = livre["id"]
        self.e_titre.delete(0, "end")
        self.e_titre.insert(0, livre.get("titre", ""))
        self.e_auteur.delete(0, "end")
        self.e_auteur.insert(0, livre.get("auteur", ""))
        self.e_categorie.delete(0, "end")
        self.e_categorie.insert(0, livre.get("categorie", ""))
        self.e_annee.delete(0, "end")
        self.e_annee.insert(0, str(livre.get("annee", "")))
        self.e_quantite.delete(0, "end")
        self.e_quantite.insert(0, str(livre.get("quantite", "")))
        self.e_statut.set(livre.get("statut", "disponible"))
        self._set_catalog_status(f"Livre #{self.selected_id} selectionne.", "info")

    def load_livres(self, post_message=None):
        if not self.is_authenticated or self.catalog_busy:
            return

        session_id = self.current_session
        self._set_catalog_busy(True, "Chargement des livres")

        def worker():
            return self._request_json("GET", "/livres", timeout=DEFAULT_REQUEST_TIMEOUT)

        def callback(result):
            if not self._session_valid(session_id):
                return

            livres, error = result
            self._set_catalog_busy(False)
            if error:
                self.table_summary.configure(text="Catalogue indisponible")
                self._show_empty(error)
                self._set_catalog_status(error, "error")
                return

            self.current_books = livres or []
            if not self.current_books:
                self.table_summary.configure(text="0 livre")
                self._show_empty("La bibliotheque est vide pour le moment.")
                self._set_catalog_status(post_message or "Aucun livre trouve.", "neutral")
                return

            self.table_summary.configure(text=f"{len(self.current_books)} livre(s)")
            self._render_livres(self.current_books)
            self._set_catalog_status(post_message or f"{len(self.current_books)} livre(s) charge(s).", "success")

        self._run_async(worker, callback)

    def _refresh_after_action(self, success_message):
        self.load_livres(post_message=success_message)

    def add_livre(self):
        if self.catalog_busy:
            return

        payload, error = self._form_data()
        if error:
            self._set_catalog_status(error, "error")
            return

        session_id = self.current_session
        self._set_catalog_busy(True, "Ajout du livre")

        def worker():
            return self._request_json("POST", "/livres", json=payload, timeout=DEFAULT_REQUEST_TIMEOUT)

        def callback(result):
            if not self._session_valid(session_id):
                return

            _, request_error = result
            self._set_catalog_busy(False)
            if request_error:
                self._set_catalog_status(request_error, "error")
                return

            self._clear_form()
            self._refresh_after_action("Livre ajoute avec succes.")

        self._run_async(worker, callback)

    def update_livre(self):
        if self.catalog_busy:
            return
        if not self.selected_id:
            self._set_catalog_status("Selectionnez un livre a modifier.", "error")
            return

        payload, error = self._form_data()
        if error:
            self._set_catalog_status(error, "error")
            return

        session_id = self.current_session
        self._set_catalog_busy(True, "Mise a jour du livre")

        def worker():
            return self._request_json("PUT", f"/livres/{self.selected_id}", json=payload, timeout=DEFAULT_REQUEST_TIMEOUT)

        def callback(result):
            if not self._session_valid(session_id):
                return

            _, request_error = result
            self._set_catalog_busy(False)
            if request_error:
                self._set_catalog_status(request_error, "error")
                return

            self._refresh_after_action("Livre modifie avec succes.")

        self._run_async(worker, callback)

    def delete_livre(self):
        if self.catalog_busy:
            return
        if not self.selected_id:
            self._set_catalog_status("Selectionnez un livre a supprimer.", "error")
            return

        book_id = self.selected_id
        session_id = self.current_session
        self._set_catalog_busy(True, "Suppression du livre")

        def worker():
            return self._request_json("DELETE", f"/livres/{book_id}", timeout=DEFAULT_REQUEST_TIMEOUT)

        def callback(result):
            if not self._session_valid(session_id):
                return

            _, request_error = result
            self._set_catalog_busy(False)
            if request_error:
                self._set_catalog_status(request_error, "error")
                return

            self._clear_form()
            self._refresh_after_action("Livre supprime avec succes.")

        self._run_async(worker, callback)

    def search_livre(self):
        if self.catalog_busy:
            return

        query = self.e_search.get().strip()
        if not query:
            self.load_livres()
            return

        session_id = self.current_session
        self._set_catalog_busy(True, "Recherche en cours")

        def worker():
            return self._request_json("GET", "/livres/search", params={"q": query}, timeout=DEFAULT_REQUEST_TIMEOUT)

        def callback(result):
            if not self._session_valid(session_id):
                return

            livres, error = result
            self._set_catalog_busy(False)
            if error:
                self.table_summary.configure(text="Recherche indisponible")
                self._show_empty(error)
                self._set_catalog_status(error, "error")
                return

            self.current_books = livres or []
            if not self.current_books:
                self.table_summary.configure(text="0 resultat")
                self._show_empty("Aucun livre ne correspond a votre recherche.")
                self._set_catalog_status("Recherche terminee : aucun resultat.", "neutral")
                return

            self.table_summary.configure(text=f"{len(self.current_books)} resultat(s)")
            self._render_livres(self.current_books)
            self._set_catalog_status(f"Recherche terminee : {len(self.current_books)} resultat(s).", "success")

        self._run_async(worker, callback)

    def send_message(self):
        if self.chat_busy:
            return

        question = self.e_question.get().strip()
        if not question:
            self._set_chat_status("Saisissez une question avant l'envoi.", "error")
            return

        if not self.is_authenticated:
            self._set_chat_status("Connectez-vous pour utiliser l'assistant.", "error")
            return

        self.append_chat("Vous", question, role="user")
        self.e_question.delete(0, "end")
        self._set_chat_busy(True, "Reponse en cours")

        session_id = self.current_session

        def worker():
            return self._request_json("POST", "/chat", json={"question": question}, timeout=CHAT_REQUEST_TIMEOUT)

        def callback(result):
            if not self._session_valid(session_id):
                return

            response, error = result
            self._set_chat_busy(False)
            if error or not isinstance(response, dict):
                message = error or "Le chatbot est indisponible pour le moment."
                self.append_chat("📚 IA", message, role="assistant")
                self._set_chat_status(message, "error")
                return

            message = response.get("reponse", "Pas de reponse disponible.")
            self.append_chat("📚 IA", message, role="assistant")
            self._set_chat_status("Reponse recue.", "success")

        self._run_async(worker, callback)


if __name__ == "__main__":
    App().mainloop()
