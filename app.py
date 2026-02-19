from flask import Flask, render_template_string, request, redirect, url_for, Response, session
import sqlite3
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = "dlsd_pro_2026_final_fix" 

# --- CONFIGURACIÓN ---
ADMIN_PASS = "dariana29" 
DB_NAME = "database.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS transacciones 
        (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, monto REAL, descripcion TEXT, fecha TEXT)''')

init_db()

# --- VISTA: LOGIN ---
LOGIN_UI = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D&S - Acceso</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { font-family: 'Segoe UI', sans-serif; background: #001529; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .login-box { background: white; padding: 40px; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); text-align: center; width: 300px; }
        .brand { color: #003366; font-size: 30px; font-weight: bold; margin: 0; }
        .sub { color: #d4af37; font-size: 11px; font-weight: bold; text-transform: uppercase; margin-bottom: 20px; display: block; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 1px solid #ddd; border-radius: 8px; box-sizing: border-box; }
        button { width: 100%; padding: 12px; background: #003366; color: white; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .footer { margin-top: 20px; font-size: 11px; color: #999; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1 class="brand">D&S</h1>
        <span class="sub">Desarrollo de Software Admi.</span>
        <form method="POST">
            <input type="password" name="password" placeholder="Contraseña" required autofocus>
            <button type="submit">ENTRAR</button>
        </form>
        <div class="footer">Realizado por Dariana © 2026</div>
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

# --- VISTA: PANEL PRINCIPAL ---
MAIN_UI = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D&S - Administración</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { background: #f0f2f5; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 15px; }
        .container { max-width: 600px; margin: auto; background: white; padding: 25px; border-radius: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 2px solid #eee; padding-bottom: 15px; margin-bottom: 20px; position: relative; }
        .brand { color: #003366; margin: 0; font-size: 28px; }
        .sub { color: #d4af37; font-size: 10px; font-weight: bold; letter-spacing: 2px; }
        .balance { background: {{ color_bal }}; color: white; padding: 20px; border-radius: 15px; text-align: center; margin-bottom: 20px; }
        .form-box { background: #f8f9fa; padding: 15px; border-radius: 15px; margin-bottom: 20px; border: 1px solid #eee; }
        input, select, .btn-save { width: 100%; padding: 12px; margin: 5px 0; border-radius: 8px; border: 1px solid #ddd; box-sizing: border-box; }
        .btn-save { background: #003366; color: white; border: none; font-weight: bold; cursor: pointer; }
        .btn-excel { background: #1d6f42; color: white; text-decoration: none; display: block; text-align: center; padding: 12px; border-radius: 8px; font-weight: bold; margin-bottom: 20px; }
        table { width: 100%; border-collapse: collapse; }
        td { padding: 12px 5px; border-bottom: 1px solid #f0f0f0; }
        .m-in { color: #28a745; font-weight: bold; }
        .m-out { color: #dc3545; font-weight: bold; }
        .footer { text-align: center; margin-top: 30px; font-size: 11px; color: #999; border-top: 1px solid #eee; padding-top: 15px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/logout" style="position:absolute; right:0; color:#ff4d4d; text-decoration:none;"><i class="fas fa-power-off"></i></a>
            <h1 class="brand">D&S</h1>
            <div class="sub">Desarrollo de Software Admi.</div>
        </div>
        
        <div class="balance">
            <small>BALANCE TOTAL</small>
            <div style="font-size: 30px; font-weight: bold;">${{ "{:,.2f}".format(bal) }}</div>
        </div>

        <div class="form-box">
            <form action="/add" method="POST">
                <input name="desc" placeholder="¿Qué compraste o vendiste?" required>
                <input name="monto" type="number" step="0.01" placeholder="Monto 0.00" required>
                <select name="tipo">
                    <option value="Ingreso">➕ Ingreso</option>
                    <option value="Egreso">➖ Egreso</option>
                </select>
                <button type="submit" class="btn-save">GUARDAR</button>
            </form>
        </div>

        <a href="/export" class="btn-excel"><i class="fas fa-file-excel"></i> DESCARGAR EXCEL</a>

        <h3>Historial</h3>
        <table>
            {% for row in rows %}
            <tr>
                <td><strong>{{ row.descripcion }}</strong><br><small style="color:#aaa;">{{ row.fecha }}</small></td>
                <td class="{{ 'm-in' if row.tipo == 'Ingreso' else 'm-out' }}" style="text-align:right;">
                    {{ '+' if row.tipo == 'Ingreso' else '-' }}${{ "{:,.2f}".format(row.monto) }}
                </td>
                <td style="text-align:right;">
                    <a href="/del/{{ row.id }}" style="color:#ddd;" onclick="return confirm('Dariana, ¿segura que quieres borrar esto?')">
                        <i class="fas fa-trash"></i>
                    </a>
                </td>
            </tr>
            {% endfor %}
        </table>

        <div class="footer">Realizado por Dariana © 2026 | D&S Admin</div>
    </div>
</body>
</html>
"""

@app.route("/")
def home():
    if not session.get("logged"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM transacciones ORDER BY id DESC").fetchall()
    
    ing = sum(r['monto'] for r in rows if r['tipo'] == 'Ingreso')
    egr = sum(r['monto'] for r in rows if r['tipo'] == 'Egreso')
    bal = ing - egr
    color_bal = "#28a745" if bal >= 0 else "#dc3545"
    conn.close()
    
    return render_template_string(MAIN_UI, rows=rows, bal=bal, color_bal=color_bal)

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
    output = io.StringIO()
    output.write("Fecha,Descripcion,Tipo,Monto\n")
    for r in rows:
        output.write(f"{r[0]},{r[1]},{r[2]},{r[3]}\n")
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-disposition":"attachment; filename=Reporte_DS.csv"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
