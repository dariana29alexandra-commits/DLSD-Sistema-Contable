from flask import Flask, render_template_string

app = Flask(__name__)

clientes = [
    {"nombre": "Cliente 1", "saldo": 1200},
    {"nombre": "Cliente 2", "saldo": 4500},
    {"nombre": "Cliente 3", "saldo": 300},
]

@app.route("/")
def home():
    html = """
    <html>
    <head><title>DLSD - Sistema Contable</title></head>
    <body>
        <h1>DLSD - Sistema Contable</h1>
        <ul>
        {% for c in clientes %}
            <li>{{ c.nombre }}: ${{ c.saldo }}</li>
        {% endfor %}
        </ul>
    </body>
    </html>
    """
    return render_template_string(html, clientes=clientes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
