from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Nuestra "Base de Datos" temporal
transacciones = [
    {"tipo": "Ingreso", "monto": 1000, "descripcion": "Pago Cliente A"},
    {"tipo": "Egreso", "monto": 200, "descripcion": "Pago Internet"}
]

@app.route("/")
def home():
    ingresos = sum(t['monto'] for t in transacciones if t['tipo'] == 'Ingreso')
    egresos = sum(t['monto'] for t in transacciones if t['tipo'] == 'Egreso')
    balance = ingresos - egresos

    html_diseno = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DLSD Contable</title>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0f2f5; margin: 0; padding: 20px; }}
            .container {{ max-width: 500px; margin: auto; background: white; padding: 20px; border-radius: 12px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
            h1, h2 {{ color: #1a73e8; text-align: center; }}
            .resumen {{ display: flex; justify-content: space-around; background: #e8f0fe; padding: 15px; border-radius: 8px; margin-bottom: 20px; }}
            input, select, button {{ width: 100%; padding: 10px; margin: 5px 0; border-radius: 5px; border: 1px solid #ccc; box-sizing: border-box; }}
            button {{ background-color: #1a73e8; color: white; border: none; cursor: pointer; font-weight: bold; }}
            button:hover {{ background-color: #1557b0; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; font-size: 14px; }}
            th {{ background: #f8f9fa; }}
            td, th {{ border-bottom: 1px solid #eee; padding: 10px; text-align: left; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📊 Sistema DLSD</h1>
            
            <div class="resumen">
                <div><strong>Balance:</strong><br>${balance}</div>
            </div>

            <h2>Agregar Movimiento</h2>
            <form action="/agregar" method="POST">
                <input type="text" name="desc" placeholder="Descripción (ej: Venta de producto)" required>
                <input type="number" name="monto" placeholder="Monto $" step="0.01" required>
                <select name="tipo">
                    <option value="Ingreso">Ingreso (+)</option>
                    <option value="Egreso">Egreso (-)</option>
                </select>
                <button type="submit">Guardar Registro</button>
            </form>

            <h2>Historial</h2>
            <table>
                <tr><th>Descripción</th><th>Monto</th><th>Tipo</th></tr>
                {"".join([f"<tr><td>{t['descripcion']}</td><td>${t['monto']}</td><td>{t['tipo']}</td></tr>" for t in transacciones])}
            </table>
        </div>
    </body>
    </html>
    """
    return html_diseno

@app.route("/agregar", methods=["POST"])
def agregar():
    descripcion = request.form.get("desc")
    monto = float(request.form.get("monto"))
    tipo = request.form.get("tipo")
    
    transacciones.append({{"tipo": tipo, "monto": monto, "descripcion": descripcion}})
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
