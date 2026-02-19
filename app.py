from flask import Flask, render_template_string, request, redirect, url_for

app = Flask(__name__)

transacciones = [
    {"tipo": "Ingreso", "monto": 1000, "descripcion": "Venta Inicial"},
    {"tipo": "Egreso", "monto": 200, "descripcion": "Gastos Operativos"}
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
        <title>DLSD Contable Pro</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{
                --primary: #2563eb;
                --success: #10b981;
                --danger: #ef4444;
                --dark: #1f2937;
            }}
            body {{ 
                font-family: 'Inter', sans-serif; 
                background-color: #f3f4f6; 
                margin: 0; padding: 20px;
                display: flex; justify-content: center;
            }}
            .container {{ 
                max-width: 600px; width: 100%; 
                background: white; padding: 30px; 
                border-radius: 20px; shadow: 0 10px 25px rgba(0,0,0,0.1); 
            }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .logo {{ 
                font-size: 50px; color: var(--primary); 
                margin-bottom: 10px; 
            }}
            .header h1 {{ margin: 0; color: var(--dark); font-size: 24px; }}
            
            .stats {{ 
                display: grid; grid-template-columns: 1fr; gap: 15px;
                margin-bottom: 30px;
            }}
            .stat-card {{ 
                padding: 15px; border-radius: 12px; color: white;
                text-align: center; font-weight: bold;
            }}
            .bg-blue {{ background: var(--primary); }}
            
            form {{ background: #f9fafb; padding: 20px; border-radius: 15px; border: 1px solid #e5e7eb; }}
            input, select, button {{ 
                width: 100%; padding: 12px; margin: 8px 0; 
                border-radius: 8px; border: 1px solid #d1d5db; box-sizing: border-box; 
            }}
            button {{ 
                background: var(--primary); color: white; border: none; 
                font-weight: bold; cursor: pointer; transition: 0.3s;
            }}
            button:hover {{ background: #1d4ed8; transform: translateY(-2px); }}
            
            table {{ width: 100%; border-collapse: collapse; margin-top: 25px; }}
            th {{ text-align: left; color: #6b7280; font-size: 12px; text-transform: uppercase; padding: 10px; }}
            td {{ padding: 12px; border-bottom: 1px solid #f3f4f6; }}
            .tag {{ 
                padding: 4px 8px; border-radius: 6px; font-size: 11px; font-weight: bold;
            }}
            .tag-ingreso {{ background: #d1fae5; color: #065f46; }}
            .tag-egreso {{ background: #fee2e2; color: #991b1b; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo"><i class="fas fa-chart-line"></i></div>
                <h1>DLSD SISTEMA CONTABLE</h1>
                <p style="color: #6b7280;">Bienvenida de nuevo, Dariana</p>
            </div>
            
            <div class="stats">
                <div class="stat-card bg-blue">
                    <small>BALANCE TOTAL</small>
                    <div style="font-size: 28px;">${balance:,.2f}</div>
                </div>
            </div>

            <form action="/agregar" method="POST">
                <label style="font-size: 12px; font-weight: bold; color: #374151;">NUEVO REGISTRO</label>
                <input type="text" name="desc" placeholder="Descripción de la operación" required>
                <input type="number" name="monto" placeholder="Monto 0.00" step="0.01" required>
                <select name="tipo">
                    <option value="Ingreso">🟢 Ingreso</option>
                    <option value="Egreso">🔴 Egreso</option>
                </select>
                <button type="submit"><i class="fas fa-plus"></i> GUARDAR EN SISTEMA</button>
            </form>

            <table>
                <thead>
                    <tr><th>Detalle</th><th>Monto</th><th>Tipo</th></tr>
                </thead>
                <tbody>
                    {"".join([f"<tr><td>{t['descripcion']}</td><td><b>${t['monto']:,.2f}</b></td><td><span class='tag tag-{t['tipo'].lower()}'>{t['tipo']}</span></td></tr>" for t in transacciones])}
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
