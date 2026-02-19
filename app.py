from flask import Flask, render_template_string, request, redirect, url_for, Response, session
import sqlite3
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = "dlsd_pro_system_2026_secure" # Cambio de llave para forzar nueva sesion

# --- SYSTEM CONFIG ---
ADMIN_PASS = "dariana29" 
DB_NAME = "database.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS transacciones 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, monto REAL, descripcion TEXT, fecha TEXT)''')

init_db()

# --- DESIGN: CORPORATE LOGIN ---
LOGIN_UI = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>D&S - Access</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #001529; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; color: white; }
        .login-box { background: #ffffff; color: #333; padding: 40px; border-radius: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.5); text-align: center; width: 320px; }
        .brand { color: #003366; font-size: 35px; font-weight: bold; margin: 0; }
        .tagline { color: #d4af37; font-size: 12px; font-weight: bold; text-transform: uppercase; margin-bottom: 25px; display: block; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #003366; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .footer-text { margin-top: 20px; font-size: 11px; color: #999; }
    </style>
</head>
<body>
    <div class="login-box">
        <i class="fas fa-shield-halved" style="font-size: 40px; color: #003366; margin-bottom: 10px;"></i>
        <h1 class="brand">D&S</h1>
        <span class="tagline">Desarrollo de Software Admi.</span>
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña de Administrador" required autofocus>
            <button type="submit">INGRESAR AL SISTEMA</button>
        </form>
        <div class="footer-text">Realizado por Dariana © 2026</div>
    </div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("password", "").strip() == ADMIN_PASS:
            session["logged"] = True
            return redirect(url_for("home"))
    return render_template_string(LOGIN_UI)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# --- DESIGN: MAIN PANEL ---
@app.route("/")
def home():
    if not session.get("logged"): return redirect(url_for("login"))
    
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM transacciones ORDER BY id DESC").fetchall()
    
    ing = sum(r['monto'] for r in rows if r['tipo'] == 'Ingreso')
    egr = sum(r['monto'] for r in rows if r['tipo'] == 'Egreso')
    bal = ing - egr
    conn.close()

    return render_template_string(f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>D&S - Control Panel</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            body {{ background: #f0f2f5; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; }}
            .card {{ max-width: 650px; margin: auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); }}
            .header {{ text-align: center; border-bottom: 2px solid #eee; padding-bottom: 20px; margin-bottom: 20px; position: relative; }}
            .brand {{ color: #003366; margin: 0; font-size: 30px; }}
            .sub {{ color: #d4af37; font-size: 12px; font-weight: bold; letter-spacing: 2px; }}
            .balance {{ background: {"#28a745" if bal >= 0 else "#dc3545"}; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 25px; }}
            .form-box {{ background: #f8f9fa; padding: 20px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #eee; }}
            input, select, button {{ width: 100%; padding: 12px; margin: 5px 0; border-radius: 8px; border: 1px solid #ddd; box-sizing: border-box; }}
            .btn-save {{ background: #003366; color: white; border: none; font-weight: bold; cursor: pointer; }}
            .btn-excel {{ background: #1d6f42; color: white; text-decoration: none; display: block; text-align: center; padding: 12px; border-radius: 8px; font-weight: bold; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            td {{ padding: 12px; border-bottom: 1px solid #f0f0f0; }}
            .footer {{ text-align: center; margin-top: 30px; font-size: 12px; color: #999; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <div class="header">
                <a href="/logout" style="position:absolute; right:0; color:#ff4d4d; text-decoration:none; font-weight:bold;"><i class="fas fa-power-off"></i></a>
                <h1 class="brand">D&S</h1>
                <div class="sub">Desarrollo de Software Admi.</div>
            </div>
            <div class="balance">
                <small>BALANCE TOTAL</small>
                <div style="font-size: 32px; font-weight: bold;">${bal:,.2f}</div>
            </div>
            <div class="form-box">
                <form action="/add" method="POST">
                    <input name="desc" placeholder="Descripción" required>
                    <input name="monto" type="number" step="0.01" placeholder="Monto" required>
                    <select name="tipo">
                        <option value="Ingreso">Ingreso (+)</option>
                        <option value="Egreso">Egreso (-)</option>
                    </select>
                    <button type="submit" class="btn-save">GUARDAR REGISTRO</button>
                </form>
            </div>
            <a href="/export" class="btn-excel"><i class="fas fa-file-excel"></i> DESCARGAR REPORTE EXCEL</a>
            <h3 style="color:#003366;"><i class="fas fa-list-check"></i> Historial de Movimientos</h3>
            <table>
                {{% for row in rows %}}
                <tr>
                    <td><strong>{{{{ row.descripcion }}}}</strong><br><small style="color:#aaa;">{{{{ row.fecha }}}}</small></td>
                    <td style="text-align:right; font-weight:bold; color: {{{{ 'green' if row.tipo == 'Ingreso' else 'red' }}}};">
                        {{{{ '+' if row.tipo == 'Ingreso' else '-' }}}}${{{{ row.monto }}}}
                    </td>
                    <td style="text-align:right;"><a href="/del/{{{{ row.id }}}}" style="color:#ddd;"><i class="fas fa-trash"></i></a></td>
                </tr>
                {{% endfor %}}
            </table>
            <div class="footer">Realizado por Dariana © 2026 | D&S Business Intelligence</div>
        </div>
    </body>
    </html>
    ''', rows=rows)

@app.route("/add", methods=["POST"])
def add():
    if not session.get("logged"): return redirect(url_for("login"))
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("INSERT INTO transacciones (tipo, monto, descripcion, fecha) VALUES (?, ?, ?, ?)", 
                     (request.form['tipo'], request.form['monto'], request.form['desc'], datetime.now().strftime("%d/%m/%Y %H:%M")))
    return redirect(url_for("home"))

@app.route("/del/<int:id>")
def delete(id):
    if not session.get("logged"): return redirect(url_for("login"))
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("DELETE FROM transacciones WHERE id = ?", (id,))
    return redirect(url_for("home"))

@app.route("/export")
def export():
    if not session.get("logged"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    rows = conn.execute("SELECT fecha, descripcion, tipo, monto FROM transacciones").fetchall()
    conn.close()
    si = io.StringIO()
    si.write("Fecha,Descripcion,Tipo,Monto\\n")
    for row in rows: si.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\\n")
    return Response(si.getvalue(), mimetype="text/csv", headers={{"Content-disposition":"attachment; filename=Reporte_DS.csv"}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
                     
