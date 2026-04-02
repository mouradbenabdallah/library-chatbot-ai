import threading

import customtkinter as ctk
import requests

API = "http://localhost:5000/api"

COLORS = {
    "bg": "#f3f5f7",
    "surface": "#ffffff",
    "ink": "#1e2a33",
    "muted": "#6d7f8a",
    "primary": "#0b6e99",
    "primary_hover": "#095b7f",
    "success": "#1f8a55",
    "success_hover": "#1a7649",
    "warning": "#d08c00",
    "warning_hover": "#b47900",
    "danger": "#c94133",
    "danger_hover": "#aa372b",
}

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Chatbot AI")
        self.geometry("1180x720")
        self.configure(fg_color=COLORS["bg"])

        self.selected_id = None

        self._build_header()
        self._build_tabs()
        self._build_livres_tab()
        self._build_chat_tab()

        # Charge les livres apres ouverture complete de la fenetre.
        self.after(250, self.load_livres)

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=14)
        header.pack(fill="x", padx=14, pady=(14, 8))

        ctk.CTkLabel(
            header,
            text="Library Chatbot AI",
            font=("Poppins", 26, "bold"),
            text_color=COLORS["ink"],
        ).pack(anchor="w", padx=16, pady=(12, 2))

        ctk.CTkLabel(
            header,
            text="Gerez votre catalogue et posez des questions sur vos livres en temps reel.",
            font=("Poppins", 13),
            text_color=COLORS["muted"],
        ).pack(anchor="w", padx=16, pady=(0, 12))

    def _build_tabs(self):
        self.tabview = ctk.CTkTabview(
            self,
            fg_color=COLORS["surface"],
            segmented_button_fg_color="#dce3e8",
            segmented_button_selected_color=COLORS["primary"],
            segmented_button_selected_hover_color=COLORS["primary_hover"],
            segmented_button_unselected_color="#dce3e8",
            segmented_button_unselected_hover_color="#cfd8df",
            text_color=COLORS["ink"],
        )
        self.tabview.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        self.tab_livres = self.tabview.add("Catalogue")
        self.tab_chat = self.tabview.add("Assistant")

    def _build_livres_tab(self):
        root = ctk.CTkFrame(self.tab_livres, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=12, pady=12)

        form = ctk.CTkFrame(root, fg_color=COLORS["surface"], corner_radius=12, width=320)
        form.pack(side="left", fill="y", padx=(0, 10))
        form.pack_propagate(False)

        ctk.CTkLabel(
            form,
            text="Gestion des livres",
            font=("Poppins", 18, "bold"),
            text_color=COLORS["ink"],
        ).pack(anchor="w", padx=14, pady=(14, 6))

        self.e_titre = self._entry(form, "Titre")
        self.e_auteur = self._entry(form, "Auteur")
        self.e_categorie = self._entry(form, "Categorie")
        self.e_annee = self._entry(form, "Annee")
        self.e_quantite = self._entry(form, "Quantite")

        self.e_statut = ctk.CTkComboBox(
            form,
            values=["disponible", "emprunte", "reserve"],
            width=285,
            fg_color="#f6f8fa",
            button_color=COLORS["primary"],
            button_hover_color=COLORS["primary_hover"],
            dropdown_fg_color="#ffffff",
            text_color=COLORS["ink"],
            border_color="#d8e1e8",
        )
        self.e_statut.set("disponible")
        self.e_statut.pack(padx=14, pady=6)

        self._action_button(form, "Ajouter", self.add_livre, COLORS["success"], COLORS["success_hover"])
        self._action_button(form, "Modifier", self.update_livre, COLORS["primary"], COLORS["primary_hover"])
        self._action_button(form, "Supprimer", self.delete_livre, COLORS["danger"], COLORS["danger_hover"])
        self._action_button(form, "Rafraichir", self.load_livres, "#8ea1ad", "#7b8e9a")

        search = ctk.CTkFrame(form, fg_color="#f7f9fb", corner_radius=10)
        search.pack(fill="x", padx=14, pady=(8, 8))
        self.e_search = ctk.CTkEntry(
            search,
            placeholder_text="Rechercher titre/auteur...",
            width=190,
            fg_color="#ffffff",
            text_color=COLORS["ink"],
            border_color="#d8e1e8",
        )
        self.e_search.pack(side="left", padx=(8, 6), pady=8)
        ctk.CTkButton(
            search,
            text="Go",
            width=40,
            command=self.search_livre,
            fg_color=COLORS["warning"],
            hover_color=COLORS["warning_hover"],
        ).pack(side="left", padx=(0, 8), pady=8)

        self.status_label = ctk.CTkLabel(form, text="Chargement...", text_color=COLORS["muted"], font=("Poppins", 12))
        self.status_label.pack(anchor="w", padx=14, pady=(0, 12))

        table = ctk.CTkFrame(root, fg_color=COLORS["surface"], corner_radius=12)
        table.pack(side="right", fill="both", expand=True)

        headers = ["ID", "Titre", "Auteur", "Categorie", "Annee", "Qte", "Statut"]
        for i, header in enumerate(headers):
            ctk.CTkLabel(
                table,
                text=header,
                font=("Poppins", 12, "bold"),
                fg_color=COLORS["primary"],
                text_color="#ffffff",
                corner_radius=8,
                padx=8,
                pady=6,
            ).grid(row=0, column=i, padx=3, pady=(10, 6), sticky="ew")

        self.rows_frame = ctk.CTkScrollableFrame(table, fg_color="#f7f9fb", corner_radius=10)
        self.rows_frame.grid(row=1, column=0, columnspan=7, sticky="nsew", padx=8, pady=(0, 8))

        table.grid_rowconfigure(1, weight=1)
        for i in range(7):
            table.grid_columnconfigure(i, weight=1)
            self.rows_frame.grid_columnconfigure(i, weight=1)

    def _build_chat_tab(self):
        root = ctk.CTkFrame(self.tab_chat, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=12, pady=12)

        panel = ctk.CTkFrame(root, fg_color=COLORS["surface"], corner_radius=12)
        panel.pack(fill="both", expand=True)

        self.chat_history = ctk.CTkTextbox(
            panel,
            state="disabled",
            font=("Poppins", 13),
            fg_color="#f7f9fb",
            text_color=COLORS["ink"],
            corner_radius=10,
        )
        self.chat_history.pack(fill="both", expand=True, padx=12, pady=(12, 8))

        bottom = ctk.CTkFrame(panel, fg_color="transparent")
        bottom.pack(fill="x", padx=12, pady=(0, 12))

        self.e_question = ctk.CTkEntry(
            bottom,
            placeholder_text="Posez votre question...",
            height=40,
            fg_color="#ffffff",
            text_color=COLORS["ink"],
            border_color="#d8e1e8",
        )
        self.e_question.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.e_question.bind("<Return>", lambda _: self.send_message())

        ctk.CTkButton(
            bottom,
            text="Envoyer",
            width=130,
            command=self.send_message,
            fg_color=COLORS["primary"],
            hover_color=COLORS["primary_hover"],
        ).pack(side="right")

        self.append_chat("Mistral", "Bonjour. Je suis votre assistant bibliotheque.")

    def _entry(self, parent, placeholder):
        widget = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            width=285,
            fg_color="#ffffff",
            text_color=COLORS["ink"],
            border_color="#d8e1e8",
        )
        widget.pack(padx=14, pady=6)
        return widget

    def _action_button(self, parent, text, command, color, hover):
        ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=color,
            hover_color=hover,
            height=34,
        ).pack(fill="x", padx=14, pady=4)

    def _request_json(self, method, path, timeout=6, **kwargs):
        try:
            response = requests.request(method, f"{API}{path}", timeout=timeout, **kwargs)
            try:
                payload = response.json()
            except ValueError:
                payload = None

            if response.ok:
                return payload, None

            if isinstance(payload, dict) and payload.get("error"):
                return payload, payload["error"]

            return payload, f"Erreur HTTP {response.status_code}"
        except ValueError:
            return None, "Reponse invalide du serveur"
        except requests.RequestException as exc:
            return None, f"API indisponible: {exc}"

    def _set_status(self, text, ok=True):
        self.status_label.configure(text=text, text_color=COLORS["success"] if ok else COLORS["danger"])

    def _form_data(self):
        annee_raw = self.e_annee.get().strip() or "0"
        quantite_raw = self.e_quantite.get().strip() or "1"
        annee = int(annee_raw)
        quantite = int(quantite_raw)

        return {
            "titre": self.e_titre.get().strip(),
            "auteur": self.e_auteur.get().strip(),
            "categorie": self.e_categorie.get().strip(),
            "annee": annee,
            "quantite": quantite,
            "statut": self.e_statut.get().strip(),
        }

    def _clear_form(self):
        for widget in [self.e_titre, self.e_auteur, self.e_categorie, self.e_annee, self.e_quantite]:
            widget.delete(0, "end")
        self.e_statut.set("disponible")
        self.selected_id = None

    def load_livres(self, livres=None):
        for widget in self.rows_frame.winfo_children():
            widget.destroy()

        if livres is None:
            livres, error = self._request_json("GET", "/livres", timeout=8)
            if error:
                self._set_status("Aucun livre charge: API indisponible", ok=False)
                self._show_empty("Impossible de charger la liste des livres")
                return

        if not livres:
            self._set_status("Aucun livre trouve", ok=False)
            self._show_empty("La bibliotheque est vide")
            return

        self._set_status(f"{len(livres)} livre(s) charge(s)")
        for row_index, livre in enumerate(livres):
            bg = "#ffffff" if row_index % 2 == 0 else "#f0f4f7"
            values = [
                livre.get("id", ""),
                livre.get("titre", ""),
                livre.get("auteur", ""),
                livre.get("categorie", ""),
                livre.get("annee", ""),
                livre.get("quantite", ""),
                livre.get("statut", ""),
            ]
            for col_index, value in enumerate(values):
                label = ctk.CTkLabel(
                    self.rows_frame,
                    text=str(value),
                    cursor="hand2",
                    fg_color=bg,
                    text_color=COLORS["ink"],
                    corner_radius=5,
                    padx=6,
                    pady=4,
                )
                label.grid(row=row_index, column=col_index, padx=2, pady=2, sticky="ew")
                label.bind("<Button-1>", lambda _, book=livre: self.select_livre(book))

    def _show_empty(self, text):
        ctk.CTkLabel(
            self.rows_frame,
            text=text,
            text_color=COLORS["muted"],
            font=("Poppins", 13),
        ).grid(row=0, column=0, columnspan=7, padx=10, pady=20, sticky="w")

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
        self._set_status(f"Livre #{self.selected_id} selectionne")

    def add_livre(self):
        try:
            payload = self._form_data()
        except ValueError:
            self._set_status("Annee et quantite doivent etre numeriques", ok=False)
            return

        _, error = self._request_json("POST", "/livres", json=payload, timeout=8)
        if error:
            self._set_status("Echec ajout livre", ok=False)
            return
        self._set_status("Livre ajoute")
        self._clear_form()
        self.load_livres()

    def update_livre(self):
        if not self.selected_id:
            self._set_status("Selectionnez un livre a modifier", ok=False)
            return

        try:
            payload = self._form_data()
        except ValueError:
            self._set_status("Annee et quantite doivent etre numeriques", ok=False)
            return

        _, error = self._request_json("PUT", f"/livres/{self.selected_id}", json=payload, timeout=8)
        if error:
            self._set_status("Echec mise a jour", ok=False)
            return
        self._set_status("Livre modifie")
        self.load_livres()

    def delete_livre(self):
        if not self.selected_id:
            self._set_status("Selectionnez un livre a supprimer", ok=False)
            return
        _, error = self._request_json("DELETE", f"/livres/{self.selected_id}", timeout=8)
        if error:
            self._set_status("Echec suppression", ok=False)
            return
        self._set_status("Livre supprime")
        self._clear_form()
        self.load_livres()

    def search_livre(self):
        query = self.e_search.get().strip()
        if not query:
            self.load_livres()
            return

        result, error = self._request_json("GET", "/livres/search", params={"q": query}, timeout=8)
        if error:
            self._set_status("Echec recherche", ok=False)
            self._show_empty("Erreur de recherche")
            return
        self.load_livres(result or [])

    def append_chat(self, sender, message):
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"{sender}:\n{message}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

    def send_message(self):
        question = self.e_question.get().strip()
        if not question:
            return

        self.append_chat("Vous", question)
        self.e_question.delete(0, "end")
        self.append_chat("Mistral", "Je reflechis...")

        def call_api():
            response, error = self._request_json("POST", "/chat", json={"question": question}, timeout=90)
            if error or not isinstance(response, dict):
                message = error or "API chatbot indisponible"
            else:
                message = response.get("reponse", "Pas de reponse")

            self.append_chat("Mistral", message)

        threading.Thread(target=call_api, daemon=True).start()


if __name__ == "__main__":
    App().mainloop()