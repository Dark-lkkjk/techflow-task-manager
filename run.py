"""Ponto de entrada da aplicação TechFlow Task Manager."""
from src.app import create_app

app = create_app()

if __name__ == '__main__':
    print("=" * 50)
    print("  TechFlow Task Manager — Iniciando...")
    print("  Acesse: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, port=5000)
