from flask import Flask, render_template_string, request, redirect, url_for, Response, session
import sqlite3
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = "dlsd_secreto_super_seguro_ds" 

# --- CONFIGURACIÓN ---
PASSWORD_SISTEMA = "dariana29" 
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
    <title>Acceso Privado - D&S</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #001f3f; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-card { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.3); text-align: center; width: 320px; }
        .brand { font-size: 32px; font-weight: bold; color: #003366; margin: 0; }
        .sub { font-size: 12px; color: #d4af37; font-weight: bold; letter-spacing: 1px; margin-bottom: 25px; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 2px solid #eee; border-radius: 10px; box-sizing: border-box; outline: none; }
        button { width: 100%; padding: 12px; background: #003366; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; transition: 0.3s; }
        button:hover { background: #001f3f; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="brand">D&S</div>
        <div class="sub">Desarrollo de Software Admi.</div>
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña" required autofocus>
            <button type="submit">ENTRAR AL PANEL</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        clave = request.form.get("password", "").strip()
        if clave == PASSWORD_SISTEMA:
            session["logueado"] = True
            return redirect(url_for("home"))
    return render_template_string(LOGIN_HTML)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def home():
    if not session.get("logueado"): return redirect(url_for("login"))
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM transacciones ORDER BY id DESC").fetchall()
    
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
        <title>D&S Panel Profesional</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --primary: #003366; --accent: #d4af37; --bg: #f4f7f6; }}
            body {{ font-family: 'Segoe UI', sans-serif; background: var(--bg); margin: 0; padding: 20px; }}
            .container {{ max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
            .header {{ text-align: center; position: relative; padding-bottom: 20px; border-bottom: 1px solid #eee; margin-bottom: 20px; }}
            .logout {{ position: absolute; top: 0; right: 0; color: #ff4d4d; text-decoration: none; font-weight: bold; font-size: 12px; }}
            .brand {{ font-size: 28px; font-weight: bold; color: var(--primary); margin:0; }}
            .sub {{ font-size: 12px; color: var(--accent); font-weight: bold; text-transform: uppercase; }}
            .balance-card {{ background: {color_balance}; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }}
            form {{ background: #f9f9f9; padding: 20px; border-radius: 15px; margin-bottom: 20px; }}
            input, select, .btn-main {{ width: 100%; padding: 12px; margin: 5px 0; border-radius: 10px; border: 1px solid #ddd; box-sizing: border-box; }}
            .btn-main {{ background: var(--primary); color: white; border: none; font-weight: bold; cursor: pointer; }}
            .btn-excel {{ background: #1d6f42; color: white; padding: 12px; width: 100%; border-radius: 10px; text-decoration: none; display: block; text-align: center; font-weight: bold; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 15px 5px; border-bottom: 1px solid #f0f0f0; }}
            .m-in {{ color: #28a745; font-weight: bold; }}
            .m-out {{ color: #dc3545; font-weight: bold; }}
            .fecha {{ color: #bbb; font-size: 11px; display: block; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <a href="/logout" class="logout"><i class="fas fa-power-off"></i> SALIR</a>
                <h1 class="brand">D&S</h1>
                <div class="sub">Desarrollo de Software Admi.</div>
            </div>
            <div class="balance-card">
                <small>BALANCE ACTUAL</small>
                <div style="font-size: 32px; font-weight: bold;">${balance:,.2f}</div>
            </div>
            <form action="/add" method="POST">
                <input name="desc" placeholder="Descripción de la operación" required>
                <input name="monto" type="number" step="0.01" placeholder="Monto 0.00" required>
                <select name="tipo">
                    <option value="Ingreso">➕ Ingreso</option>
                    <option value="Egreso">➖ Egreso</option>
                </select>
                <button type="submit" class="btn-main">GUARDAR REGISTRO</button>
            </form>
            <a href="/export" class="btn-excel"><i class="fas fa-file-excel"></i> DESCARGAR EXCEL (CSV)</a>
            <h3 style="color:#444;"><i class="fas fa-list"></i> Movimientos ({len(rows)})</h3>
            <table>
                {% for row in rows %}
                <tr>
                    <td>
                        <strong>{{ row.descripcion }}</strong>
                        <span class="fecha">{{ row.fecha }}</span>
                    </td>
                    <td class="m-{{ 'in' if row.tipo == 'Ingreso' else 'out' }}" style="text-align:right;">
                        {{ '+' if row.tipo == 'Ingreso' else '-' }}${{ row.monto }}
                    </td>
                    <td style="text-align:right; padding-left:10px;">
                        <a href="/del/{{ row.id }}" style="color:#ccc;" onclick="return confirm('¿Eliminar?')"><i class="fas fa-trash"></i></a>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_diseno, rows=rows)

@app.route("/add", methods=["POST"])
def add():
    if not session.get("logueado"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO transacciones (tipo, monto, descripcion, fecha) VALUES (?, ?, ?, ?)", 
                 (request.form['tipo'], request.form['monto'], request.form['desc'], datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit(); conn.close()
    return redirect(url_for("home"))

@app.route("/del/<int:id>")
def delete(id):
    if not session.get("logueado"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM transacciones WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return redirect(url_for("home"))

@app.route("/export")
def export():
    if not session.get("logueado"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT fecha, descripcion, tipo, monto FROM transacciones").fetchall()
    conn.close()
    si = io.StringIO()
    si.write("Fecha,Descripcion,Tipo,Monto\\n")
    for row in rows:
        si.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\\n")
    return Response(si.getvalue(), mimetype="text/csv", headers={{"Content-disposition":"attachment; filename=Reporte_DS.csv"}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
