import customtkinter as ctk
import requests
import threading

API = "http://localhost:5000/api"

# Configuration visuelle globale de l'application desktop.
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Fenetre principale de l'interface graphique CustomTkinter.
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Library Chatbot AI")
        self.geometry("1100x650")

        # Deux onglets: gestion des livres et conversation avec le chatbot.
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        self.tab_livres = self.tabview.add("Livres")
        self.tab_chat   = self.tabview.add("Chatbot")

        self.build_livres_tab()
        self.build_chat_tab()
        self.load_livres()

    def build_livres_tab(self):
        # Colonne de gauche: formulaire de saisie et actions CRUD.
        form = ctk.CTkFrame(self.tab_livres, width=300)
        form.pack(side="left", fill="y", padx=10, pady=10)

        ctk.CTkLabel(form, text="Gestion des livres", font=("Arial",16,"bold")).pack(pady=10)

        self.e_titre     = ctk.CTkEntry(form, placeholder_text="Titre",     width=260)
        self.e_auteur    = ctk.CTkEntry(form, placeholder_text="Auteur",    width=260)
        self.e_categorie = ctk.CTkEntry(form, placeholder_text="Catégorie", width=260)
        self.e_annee     = ctk.CTkEntry(form, placeholder_text="Année",     width=260)
        self.e_quantite  = ctk.CTkEntry(form, placeholder_text="Quantité",  width=260)
        self.e_statut    = ctk.CTkComboBox(form, values=["disponible","emprunté","réservé"], width=260)

        # Champs du formulaire pour construire un payload JSON vers l'API.
        for w in [self.e_titre, self.e_auteur, self.e_categorie,
                  self.e_annee, self.e_quantite, self.e_statut]:
            w.pack(pady=4)

        # Boutons d'actions sur les livres.
        ctk.CTkButton(form, text="Ajouter",    command=self.add_livre,    fg_color="#2ecc71").pack(pady=4, fill="x", padx=10)
        ctk.CTkButton(form, text="Modifier",   command=self.update_livre, fg_color="#3498db").pack(pady=4, fill="x", padx=10)
        ctk.CTkButton(form, text="Supprimer",  command=self.delete_livre, fg_color="#e74c3c").pack(pady=4, fill="x", padx=10)
        ctk.CTkButton(form, text="Rafraîchir",  command=self.load_livres,  fg_color="#95a5a6").pack(pady=4, fill="x", padx=10)

        search_frame = ctk.CTkFrame(form)
        search_frame.pack(fill="x", padx=10, pady=8)
        self.e_search = ctk.CTkEntry(search_frame, placeholder_text="Rechercher...", width=180)
        self.e_search.pack(side="left", padx=4)
        ctk.CTkButton(search_frame, text="OK", width=40, command=self.search_livre).pack(side="left")

        # Table de résultats a droite.
        table_frame = ctk.CTkFrame(self.tab_livres)
        table_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        headers = ["ID","Titre","Auteur","Catégorie","Année","Qté","Statut"]
        for i, h in enumerate(headers):
            ctk.CTkLabel(table_frame, text=h, font=("Arial",12,"bold"),
                         fg_color="#2c3e50", corner_radius=4).grid(row=0, column=i, padx=2, pady=2, sticky="ew")

        self.rows_frame = ctk.CTkScrollableFrame(table_frame)
        self.rows_frame.grid(row=1, column=0, columnspan=7, sticky="nsew", padx=2, pady=2)
        table_frame.grid_rowconfigure(1, weight=1)
        for i in range(7):
            table_frame.grid_columnconfigure(i, weight=1)

        self.selected_id = None

    def load_livres(self, livres=None):
        # Reconstruit l'affichage du tableau depuis l'API ou depuis une liste fournie.
        for w in self.rows_frame.winfo_children():
            w.destroy()
        if livres is None:
            try:
                livres = requests.get(f"{API}/livres").json()
            except:
                livres = []
        for r, l in enumerate(livres):
            vals = [l['id'], l['titre'], l['auteur'], l['categorie'], l['annee'], l['quantite'], l['statut']]
            for c, v in enumerate(vals):
                lbl = ctk.CTkLabel(self.rows_frame, text=str(v), cursor="hand2")
                lbl.grid(row=r, column=c, padx=2, pady=1, sticky="ew")
                lbl.bind("<Button-1>", lambda e, livre=l: self.select_livre(livre))
            self.rows_frame.grid_columnconfigure(c, weight=1)

    def select_livre(self, l):
            # Copie les valeurs de la ligne selectionnee dans le formulaire.
        self.selected_id = l['id']
        self.e_titre.delete(0,"end");     self.e_titre.insert(0, l['titre'])
        self.e_auteur.delete(0,"end");    self.e_auteur.insert(0, l['auteur'])
        self.e_categorie.delete(0,"end"); self.e_categorie.insert(0, l['categorie'])
        self.e_annee.delete(0,"end");     self.e_annee.insert(0, str(l['annee']))
        self.e_quantite.delete(0,"end");  self.e_quantite.insert(0, str(l['quantite']))
        self.e_statut.set(l['statut'])

    def get_form_data(self):
        # Normalise les donnees du formulaire avant envoi a l'API.
        return {
            "titre":     self.e_titre.get(),
            "auteur":    self.e_auteur.get(),
            "categorie": self.e_categorie.get(),
            "annee":     int(self.e_annee.get() or 0),
            "quantite":  int(self.e_quantite.get() or 1),
            "statut":    self.e_statut.get()
        }

    def add_livre(self):
        # Cree un livre puis recharge le tableau.
        requests.post(f"{API}/livres", json=self.get_form_data())
        self.load_livres()

    def update_livre(self):
        # Met a jour uniquement si un livre a ete selectionne.
        if self.selected_id:
            requests.put(f"{API}/livres/{self.selected_id}", json=self.get_form_data())
            self.load_livres()

    def delete_livre(self):
        # Supprime le livre actuellement selectionne.
        if self.selected_id:
            requests.delete(f"{API}/livres/{self.selected_id}")
            self.selected_id = None
            self.load_livres()

    def search_livre(self):
        # Interroge l'API de recherche puis affiche uniquement les resultats.
        q = self.e_search.get()
        res = requests.get(f"{API}/livres/search?q={q}").json()
        self.load_livres(res)

    def build_chat_tab(self):
        # Zone de conversation avec historique.
        self.chat_history = ctk.CTkTextbox(self.tab_chat, state="disabled", font=("Arial", 13))
        self.chat_history.pack(fill="both", expand=True, padx=10, pady=10)

        bottom = ctk.CTkFrame(self.tab_chat)
        bottom.pack(fill="x", padx=10, pady=6)

        self.e_question = ctk.CTkEntry(bottom, placeholder_text="Posez votre question...", height=40)
        self.e_question.pack(side="left", fill="x", expand=True, padx=(0,8))
        self.e_question.bind("<Return>", lambda e: self.send_message())

        ctk.CTkButton(bottom, text="Envoyer", width=120,
                      command=self.send_message, fg_color="#2ecc71").pack(side="right")

        self.append_chat("Mistral", "Bonjour ! Je suis votre assistant bibliothèque. Posez-moi une question sur les livres.")

    def append_chat(self, sender, message):
        # Ajoute un message dans la zone d'historique.
        self.chat_history.configure(state="normal")
        self.chat_history.insert("end", f"{sender}:\n{message}\n\n")
        self.chat_history.configure(state="disabled")
        self.chat_history.see("end")

    def send_message(self):
        # Envoie la question a l'API sans bloquer l'interface graphique.
        question = self.e_question.get().strip()
        if not question:
            return
        self.append_chat("Vous", question)
        self.e_question.delete(0, "end")
        self.append_chat("Mistral", "En train de réfléchir...")

        def call_api():
            try:
                res = requests.post(
                    "http://localhost:5000/api/chat",
                    json={"question": question}
                ).json()
                reponse = res.get("reponse", "Pas de réponse.")
            except:
                reponse = "Erreur : Flask API non accessible."
            self.chat_history.configure(state="normal")
            self.chat_history.delete("1.0", "end")
            self.chat_history.configure(state="disabled")
            self.append_chat("Vous", question)
            self.append_chat("Mistral", reponse)

        threading.Thread(target=call_api, daemon=True).start()


if __name__ == "__main__":
    # Lance l'application desktop en mode autonome.
    app = App()
    app.mainloop()