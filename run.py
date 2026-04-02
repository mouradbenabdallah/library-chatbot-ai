from app import create_app

# Point d'entree de l'API Flask.
app = create_app()

if __name__ == "__main__":
    # Mode debug pour le developpement local.
    print("Flask demarre sur http://localhost:5000")
    app.run(debug=True, port=5000)