from flask import Flask, render_template

app = Flask(__name__)

# Datos de ejemplo para probar
clientes = [
    {"nombre": "Cliente 1", "saldo": 1200},
    {"nombre": "Cliente 2", "saldo": 4500},
    {"nombre": "Cliente 3", "saldo": 300},
]

@app.route("/")
def home():
    # Mostramos los clientes y sus saldos
    html = "<h1>DLSD - Sistema Contable</h1><ul>"
    for c in clientes:
        html += f"<li>{c['nombre']}: ${c['saldo']}</li>"
    html += "</ul>"
    return html

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
