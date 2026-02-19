from flask import Flask, render_template_string

app = Flask(__name__)

# Simulación de tu base de datos contable
datos_contables = {
    "empresa": "DLSD Consultores",
    "ingresos": 1500.50,
    "egresos": 450.25,
    "clientes": [
        {"id": 1, "nombre": "Inversiones ABC", "estado": "Al día"},
        {"id": 2, "nombre": "Tienda Variedades", "estado": "Pendiente"},
        {"id": 3, "nombre": "Suministros Global", "estado": "Al día"}
    ]
}

@app.route("/")
def home():
    # Calculamos el balance
    balance = datos_contables["ingresos"] - datos_contables["egresos"]
    
    # Diseño profesional (HTML) dentro de Python para ir rápido
    html_diseno = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Panel DLSD</title>
        <style>
            body {{ font-family: sans-serif; background-color: #f4f7f6; color: #333; margin: 0; padding: 20px; }}
            .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); max-width: 600px; margin: auto; }}
            h1 {{ color: #4e73df; }}
            .resumen {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
            .box {{ padding: 10px; border-radius: 5px; width: 30%; text-align: center; color: white; }}
            .ingresos {{ background-color: #1cc88a; }}
            .egresos {{ background-color: #e74a3b; }}
            .balance {{ background-color: #4e73df; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>📊 Sistema Contable DLSD</h1>
            <p>Bienvenida, <strong>Dariana</strong>. Aquí está el resumen de hoy:</p>
            
            <div class="resumen">
                <div class="box ingresos"><b>Ingresos</b><br>${datos_contables["ingresos"]}</div>
                <div class="box egresos"><b>Egresos</b><br>${datos_contables["egresos"]}</div>
                <div class="box balance"><b>Balance</b><br>${balance}</div>
            </div>

            <h3>Lista de Clientes</h3>
            <table>
                <tr><th>Cliente</th><th>Estado</th></tr>
                {"".join([f"<tr><td>{c['nombre']}</td><td>{c['estado']}</td></tr>" for c in datos_contables["clientes"]])}
            </table>
        </div>
    </body>
    </html>
    """
    return html_diseno

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
    """
    return render_template_string(html, clientes=clientes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
