from flask import Flask, render_template_string, request, redirect, url_for, Response, session
import sqlite3
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = "dlsd_secreto_super_seguro_dariana" 

# --- CONFIGURACIÓN DE SEGURIDAD ---
PASSWORD_SISTEMA = "dariana29*" 
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
        .logo-text { font-size: 24px; font-weight: bold; color: #003366; margin-bottom: 5px; }
        .sub-text { font-size: 12px; color: #d4af37; font-weight: bold; margin-bottom: 20px; text-transform: uppercase; }
        input { width: 100%; padding: 12px; margin: 10px 0; border: 2px solid #eee; border-radius: 10px; box-sizing: border-box; outline: none; transition: 0.3s; }
        input:focus { border-color: #003366; }
        button { width: 100%; padding: 12px; background: #003366; color: white; border: none; border-radius: 10px; cursor: pointer; font-weight: bold; font-size: 16px; transition: 0.3s; }
        button:hover { background: #001f3f; }
        .error { color: #dc3545; font-size: 14px; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo-text">D&S</div>
        <div class="sub-text">Desarrollo de Software Admi.</div>
        <p style="color: #666; font-size: 14px;">Ingresa tu contraseña para administrar</p>
        {% if error %} <p class="error">{{ error }}</p> {% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="••••••••" required autofocus>
            <button type="submit">INICIAR SESIÓN</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        clave_ingresada = request.form.get("password", "").strip()
        if clave_ingresada == PASSWORD_SISTEMA:
            session["logueado"] = True
            return redirect(url_for("home"))
        else:
            error = "Contraseña incorrecta"
    return render_template_string(LOGIN_HTML, error=error)

@app.route("/logout")
def logout():
    session.clear()
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
        <title>D&S - Panel de Control</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ --primary: #003366; --accent: #d4af37; --bg: #f4f7f6; }}
            body {{ font-family: 'Segoe UI', sans-serif; background-color: var(--bg); margin: 0; padding: 20px; }}
            .container {{ max-width: 650px; margin: auto; background: white; padding: 30px; border-radius: 20px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
            
            .header {{ text-align: center; margin-bottom: 25px; position: relative; border-bottom: 2px solid #f0f0f0; padding-bottom: 20px; }}
            .logout-link {{ position: absolute; top: 0; right: 0; color: #ff4d4d; text-decoration: none; font-size: 13px; font-weight: bold; border: 1px solid #ff4d4d; padding: 5px 12px; border-radius: 8px; transition: 0.3s; }}
            .logout-link:hover {{ background: #ff4d4d; color: white; }}
            
            .brand-name {{ font-size: 32px; font-weight: bold; color: var(--primary); margin: 0; }}
            .brand-sub {{ font-size: 14px; color: var(--accent); font-weight: bold; letter-spacing: 2px; text-transform: uppercase; margin-top: 5px; }}

            .balance-card {{ background: {color_balance}; color: white; padding: 25px; border-radius: 15px; text-align: center; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }}
            
            form {{ background: #f9f9f9; padding: 20px; border-radius: 15px; border: 1px solid #eee; margin-bottom: 20px; }}
            input, select, button {{ width: 100%; padding: 12px; margin: 8px 0; border-radius: 10px; border: 1px solid #ddd; box-sizing: border-box; font-size: 15px; }}
            
            .btn-guardar {{ background-color: var(--primary); color: white; border: none; font-weight: bold; cursor: pointer; transition: 0.3s; }}
            .btn-guardar:hover {{ background: #001f3f; }}
            
            .btn-excel {{ background-color: #1d6f42; color: white; border: none; font-weight: bold; cursor: pointer; width: 100%; transition: 0.3s; }}
            .btn-excel:hover {{ background: #145532; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ text-align: left; color: #888; padding: 12px; font-size: 12px; text-transform: uppercase; border-bottom: 2px solid #eee; }}
            td {{ padding: 15px 12px; border-bottom: 1px solid #f9f9f9; }}
            
            .monto-ingreso {{ color: #28a745; font-weight: bold; }}
            .monto-egreso {{ color: #dc3545; font-weight: bold; }}
            .fecha-text {{ color: #aaa; font-size: 11px; display: block; margin-top: 4px; }}
            
            .btn-delete {{ color: #ccc; text-decoration: none; font-size: 18px; transition: 0.3s; }}
            .btn-delete:hover {{ color: #dc3545; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <a href="/logout" class="logout-link"><i class="fas fa-power-off"></i> SALIR</a>
                <h1 class="brand-name">D&S</h1>
                <div class="brand-sub">Desarrollo de Software Admi.</div>
            </div>
            
            <div class="balance-card">
                <small style="opacity: 0.8; letter-spacing: 1px;">ESTADO FINANCIERO ACTUAL</small>
                <div style="font-size: 36px; font-weight: bold; margin-top: 5px;">${balance:,.2f}</div>
            </div>

            <form action="/agregar" method="POST">
                <input type="text" name="desc" placeholder="¿En qué consistió la operación?" required>
                <input type="number" name="monto" placeholder="Monto (Ej: 1500.00)" step="0.01" required>
                <select name="tipo">
                    <option value="Ingreso">➕ Ingreso de Dinero</option>
                    <option value="Egreso">➖ Egreso / Gasto</option>
                </select>
                <button type="submit" class="btn-guardar"><i class="fas fa-check-circle"></i> REGISTRAR AHORA</button>
            </form>

            <a href="/exportar" style="text-decoration:none;">
                <button class="btn-excel"><i class="fas fa-file-csv"></i> EXPORTAR DATOS A EXCEL (CSV)</button>
            </a>

            <h3 style="margin-top:30px; color: #444; font-size: 18px;"><i class="fas fa-list-ul"></i> Historial de Movimientos</h3>
            <table>
                <thead>
                    <tr><th>Descripción / Fecha</th><th>Monto</th><th></th></tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td>
                            <strong style="color:#333;">{row['descripcion']}</strong>
                            <span class="fecha-text">{row['fecha']}</span>
                        </td>
                        <td class="monto-{row['tipo'].lower()}">
                            {' + ' if row['tipo'] == 'Ingreso' else ' - '}${row['monto']:,.2f}
                        </td>
                        <td style="text-align:right;">
                            <a href="/eliminar/{row['id']}" class="btn-delete" onclick="return confirm('¿Segura que quieres eliminar este registro?')">
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
    fecha = datetime.now().strftime("%d/%b/%Y %H:%M")
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
    return Response(output.getvalue(), mimetype="text/csv", headers={{"Content-disposition": "attachment; filename=Reporte_DS_Software.csv"}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
