from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

# Base de datos temporal
transacciones = [
    {"tipo": "Ingreso", "monto": 1000, "descripcion": "Saldo Inicial"},
    {"tipo": "Egreso", "monto": 150, "descripcion": "Gastos de Papelería"}
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
        <title>DLSD - Sistema Contable</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{
                --primary: #003366;
                --accent: #d4af37;
                --bg: #f8f9fa;
            }}
            body {{ 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                background-color: var(--bg); 
                margin: 0; padding: 20px;
            }}
            .container {{ 
                max-width: 600px; margin: auto; 
                background: white; padding: 30px; 
                border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.1); 
            }}
            .header {{ text-align: center; margin-bottom: 25px; }}
            /* AQUÍ ESTÁ TU LOGO */
            .logo-img {{ 
                width: 180px; 
                height: auto; 
                margin-bottom: 15px;
                border-radius: 10px;
            }}
            .balance-card {{ 
                background: linear-gradient(135deg, #003366 0%, #004080 100%);
                color: white; padding: 20px; border-radius: 12px;
                text-align: center; margin-bottom: 25px;
            }}
            form {{ background: #f1f3f5; padding: 20px; border-radius: 12px; margin-bottom: 25px; }}
            input, select, button {{ 
                width: 100%; padding: 12px; margin: 8px 0; 
                border-radius: 8px; border: 1px solid #ced4da; box-sizing: border-box; 
            }}
            button {{ 
                background-color: var(--primary); color: white; border: none; 
                font-weight: bold; cursor: pointer; transition: 0.3s;
            }}
            button:hover {{ background-color: #002244; transform: scale(1.02); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ text-align: left; color: #495057; font-size: 13px; padding: 10px; border-bottom: 2px solid #dee2e6; }}
            td {{ padding: 12px; border-bottom: 1px solid #eee; font-size: 14px; }}
            .monto-ingreso {{ color: #28a745; font-weight: bold; }}
            .monto-egreso {{ color: #dc3545; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://i.ibb.co/6RTPvjYd/logo.png" alt="Logo DLSD" class="logo-img">
                <p style="color: #6c757d; font-weight: bold; margin-top: 0;">SISTEMA CONTABLE PROFESIONAL</p>
            </div>
            
            <div class="balance-card">
                <small>BALANCE DISPONIBLE</small>
                <div style="font-size: 32px; font-weight: bold;">${balance:,.2f}</div>
            </div>

            <form action="/agregar" method="POST">
                <input type="text" name="desc" placeholder="Descripción (Ej: Honorarios)" required>
                <input type="number" name="monto" placeholder="Monto 0.00" step="0.01" required>
                <select name="tipo">
                    <option value="Ingreso">➕ Ingreso</option>
                    <option value="Egreso">➖ Egreso</option>
                </select>
                <button type="submit">REGISTRAR OPERACIÓN</button>
            </form>

            <h3><i class="fas fa-history"></i> Últimos Movimientos</h3>
            <table>
                <thead>
                    <tr><th>Detalle</th><th>Monto</th></tr>
                </thead>
                <tbody>
                    {"".join([f"<tr><td>{t['descripcion']}</td><td class='monto-{t['tipo'].lower()}'>{' + ' if t['tipo'] == 'Ingreso' else ' - '}${t['monto']:,.2f}</td></tr>" for t in transacciones])}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html_diseno

@app.route("/agregar", methods=["POST"])
def agregar():
    try:
        descripcion = request.form.get("desc")
        monto = float(request.form.get("monto"))
        tipo = request.form.get("tipo")
        transacciones.append({"tipo": tipo, "monto": monto, "descripcion": descripcion})
        return redirect(url_for("home"))
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
