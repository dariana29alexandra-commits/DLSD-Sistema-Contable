from flask import Flask, render_template_string, request, redirect, url_for, Response, session
import sqlite3
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = "dlsd_secreto_super_seguro" # Llave interna del sistema

# --- CONFIGURACIÓN DE SEGURIDAD ---
PASSWORD_SISTEMA = "admin123" # <--- CAMBIA TU CONTRASEÑA AQUÍ
DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT NOT NULL,
            monto REAL NOT NULL,
            descripcion TEXT NOT NULL,
            fecha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- PANTALLA DE LOGIN ---
LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acceso Privado - DLSD</title>
    <style>
        body { font-family: sans-serif; background: #f3f4f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: white; padding: 40px; border-radius: 15px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); text-align: center; width: 300px; }
        img { width: 120px; margin-bottom: 20px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #003366; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .error { color: red; font-size: 14px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <img src="https://i.ibb.co/6RTPvjYd/logo.png" alt="Logo">
        <h2>Acceso Privado</h2>
        {% if error %} <p class="error">{{ error }}</p> {% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña" required>
            <button type="submit">Entrar al Sistema</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        if request.form.get("password") == PASSWORD_SISTEMA:
            session["logueado"] = True
            return redirect(url_for("home"))
        else:
            error = "Contraseña incorrecta"
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/logout")
def logout():
    session.pop("logueado", None)
    return redirect(url_for("login"))

@app.route("/")
def home():
    if not session.get("logueado"):
        return redirect(url_for("login"))
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transacciones ORDER BY id DESC")
    rows = cursor.fetchall()
    
    ingresos = sum(row['monto'] for row in rows if row['tipo'] == 'Ingreso')
    egresos = sum(row['monto'] for row in rows if row['tipo'] == 'Egreso')
    balance = ingresos - egresos
    conn.close()

    color_balance = "#28a745" if balance >= 0 else "#dc3545"

    html_diseno = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>DLSD - Sistema Contable Pro</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --primary: #003366; --bg: #f8f9fa; }}
            body {{ font-family: 'Segoe UI', sans-serif; background-color: var(--bg); margin: 0; padding: 20px; }}
            .container {{ max-width: 650px; margin: auto; background: white; padding: 30px; border-radius: 15px; box-shadow: 0 8px 30px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; margin-bottom: 25px; position: relative; }}
            .logout-link {{ position: absolute; top: 0; right: 0; color: #666; text-decoration: none; font-size: 14px; }}
            .logo-img {{ width: 180px; height: auto; border-radius: 10px; }}
            .balance-card {{ background: {color_balance}; color: white; padding: 20px; border-radius: 12px; text-align: center; margin-bottom: 25px; }}
            form {{ background: #f1f3f5; padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
            input, select, button {{ width: 100%; padding: 12px; margin: 8px 0; border-radius: 8px; border: 1px solid #ced4da; box-sizing: border-box; }}
            .btn-guardar {{ background-color: var(--primary); color: white; border: none; font-weight: bold; cursor: pointer; }}
            .btn-excel {{ background-color: #1d6f42; color: white; border: none; font-weight: bold; cursor: pointer; width: 100%; }}
            table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
            th {{ text-align: left; color: #495057; padding: 10px; border-bottom: 2px solid #dee2e6; }}
            td {{ padding: 10px; border-bottom: 1px solid #eee; }}
            .monto-ingreso {{ color: #28a745; font-weight: bold; }}
            .monto-egreso {{ color: #dc3545; font-weight: bold; }}
            .fecha-text {{ color: #888; font-size: 11px; display: block; }}
            .btn-delete {{ color: #dc3545; text-decoration: none; font-size: 16px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <a href="/logout" class="logout-link"><i class="fas fa-sign-out-alt"></i> Salir</a>
                <img src="https://i.ibb.co/6RTPvjYd/logo.png" alt="Logo DLSD" class="logo-img">
                <p style="color: #6c757d; font-weight: bold;">SISTEMA CONTABLE PROFESIONAL</p>
            </div>
            
            <div class="balance-card">
                <small>BALANCE DISPONIBLE</small>
                <div style="font-size: 32px; font-weight: bold;">${balance:,.2f}</div>
            </div>

            <form action="/agregar" method="POST">
                <input type="text" name="desc" placeholder="Descripción de la operación" required>
                <input type="number" name="monto" placeholder="Monto 0.00" step="0.01" required>
                <select name="tipo">
                    <option value="Ingreso">➕ Ingreso</option>
                    <option value="Egreso">➖ Egreso</option>
                </select>
                <button type="submit" class="btn-guardar"><i class="fas fa-save"></i> GUARDAR REGISTRO</button>
            </form>

            <a href="/exportar" style="text-decoration:none;">
                <button class="btn-excel"><i class="fas fa-file-excel"></i> DESCARGAR REPORTE EXCEL</button>
            </a>

            <h3 style="margin-top:25px;"><i class="fas fa-history"></i> Movimientos ({len(rows)})</h3>
            <table>
                <thead>
                    <tr><th>Detalle / Fecha</th><th>Monto</th><th></th></tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td>
                            <strong>{row['descripcion']}</strong>
                            <span class="fecha-text">{row['fecha']}</span>
                        </td>
                        <td class="monto-{row['tipo'].lower()}">
                            {' + ' if row['tipo'] == 'Ingreso' else ' - '}${row['monto']:,.2f}
                        </td>
                        <td>
                            <a href="/eliminar/{row['id']}" class="btn-delete" onclick="return confirm('¿Eliminar?')">
                                <i class="fas fa-trash-alt"></i>
                            </a>
                        </td>
                    </tr>
                    ''' for row in rows])}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return html_diseno

@app.route("/agregar", methods=["POST"])
def agregar():
    if not session.get("logueado"): return redirect(url_for("login"))
    descripcion = request.form.get("desc")
    monto = float(request.form.get("monto"))
    tipo = request.form.get("tipo")
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("INSERT INTO transacciones (tipo, monto, descripcion, fecha) VALUES (?, ?, ?, ?)", (tipo, monto, descripcion, fecha))
    conn.commit(); conn.close()
    return redirect(url_for("home"))

@app.route("/eliminar/<int:id>")
def eliminar(id):
    if not session.get("logueado"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("DELETE FROM transacciones WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return redirect(url_for("home"))

@app.route("/exportar")
def exportar():
    if not session.get("logueado"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("SELECT fecha, descripcion, tipo, monto FROM transacciones")
    rows = cursor.fetchall(); conn.close()
    output = io.StringIO()
    output.write("Fecha,Descripcion,Tipo,Monto\\n")
    for row in rows: output.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\\n")
    return Response(output.getvalue(), mimetype="text/csv", headers={{"Content-disposition": "attachment; filename=Reporte_DLSD.csv"}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
