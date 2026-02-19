from flask import Flask, render_template_string, request, redirect, url_for, Response, session
import sqlite3
from datetime import datetime
import io

app = Flask(__name__)
app.secret_key = "clave_segura_dariana_software_admi" # ¡No olvides cambiarla por una más compleja en un entorno real!

# --- CONFIGURACIÓN CENTRAL ---
PASSWORD_SISTEMA = "dariana29" # Tu contraseña actual
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

# --- Diseño de la Página de Inicio de Sesión ---
LOGIN_HTML_CUSTOM = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Acceso Seguro - D&S Admi</title>
    <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        body { 
            font-family: 'Montserrat', sans-serif; 
            background: linear-gradient(135deg, #001f3f 0%, #000a1a 100%); 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            min-height: 100vh; 
            margin: 0; 
            color: #fff;
        }
        .login-card { 
            background: rgba(255, 255, 255, 0.08); /* Transparente con ligero fondo */
            backdrop-filter: blur(10px); /* Efecto de cristal esmerilado */
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 50px 40px; 
            border-radius: 20px; 
            box-shadow: 0 10px 40px rgba(0,0,0,0.4); 
            text-align: center; 
            width: 350px; 
            animation: fadeIn 1s ease-out;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }

        .logo-section { margin-bottom: 30px; }
        .logo-section .icon { font-size: 50px; color: #d4af37; margin-bottom: 15px; }
        .logo-section .brand { font-size: 32px; font-weight: 700; color: #fff; margin: 0; }
        .logo-section .sub { font-size: 13px; color: #aaa; text-transform: uppercase; letter-spacing: 2px; }
        
        input { 
            width: calc(100% - 24px); 
            padding: 12px; 
            margin: 10px 0; 
            border: 1px solid rgba(255, 255, 255, 0.3); 
            border-radius: 10px; 
            box-sizing: border-box; 
            background: rgba(255, 255, 255, 0.1); 
            color: #fff; 
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s ease;
        }
        input::placeholder { color: #ccc; }
        input:focus { border-color: #d4af37; }

        button { 
            width: 100%; 
            padding: 15px; 
            background: #d4af37; 
            color: #001f3f; 
            border: none; 
            border-radius: 10px; 
            cursor: pointer; 
            font-weight: 700; 
            font-size: 17px; 
            transition: background 0.3s ease, transform 0.2s ease;
            margin-top: 20px;
        }
        button:hover { background: #e0b84f; transform: translateY(-2px); }
        .error { color: #ff6b6b; font-size: 14px; margin-top: 15px; }
        
        .footer-login { margin-top: 30px; font-size: 12px; color: #888; }
    </style>
</head>
<body>
    <div class="login-card">
        <div class="logo-section">
            <i class="fas fa-lock icon"></i>
            <h1 class="brand">D&S</h1>
            <div class="sub">Desarrollo de Software Admi.</div>
        </div>
        
        <p style="color: #eee; margin-bottom: 25px;">Accede a tu panel de control</p>
        
        {% if error %} <p class="error">{{ error }}</p> {% endif %}
        <form method="POST">
            <input type="password" name="password" placeholder="Ingresa tu contraseña" required autofocus>
            <button type="submit"><i class="fas fa-sign-in-alt"></i> ENTRAR</button>
        </form>
        <div class="footer-login">Realizado por Dariana © 2024</div>
    </div>
</body>
</html>
"""

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        clave = request.form.get("password", "").strip()
        if clave == PASSWORD_SISTEMA:
            session["logueado"] = True
            return redirect(url_for("home"))
        else:
            error = "Contraseña incorrecta."
    return render_template_string(LOGIN_HTML_CUSTOM, error=error)

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

    html_diseno_main = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>D&S - Panel Administrativo</title>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
        <style>
            :root {{ 
                --primary-dark: #001f3f; 
                --primary-medium: #003366; 
                --accent-gold: #d4af37; 
                --text-dark: #333; 
                --text-light: #f8f9fa;
                --bg-light: #eef1f6;
                --card-bg: #ffffff;
                --border-light: #e0e0e0;
                --shadow-light: rgba(0,0,0,0.08);
            }}
            body {{ 
                font-family: 'Montserrat', sans-serif; 
                background: var(--bg-light); 
                margin: 0; 
                padding: 20px; 
                color: var(--text-dark);
            }}
            .container {{ 
                max-width: 700px; 
                margin: 20px auto; 
                background: var(--card-bg); 
                padding: 35px; 
                border-radius: 25px; 
                box-shadow: 0 10px 40px var(--shadow-light); 
            }}
            
            /* Header */
            .header {{ 
                text-align: center; 
                position: relative; 
                padding-bottom: 25px; 
                border-bottom: 2px solid var(--border-light); 
                margin-bottom: 30px; 
            }}
            .logout-btn {{ 
                position: absolute; 
                top: 0; 
                right: 0; 
                color: #ff6b6b; 
                text-decoration: none; 
                font-weight: 600; 
                font-size: 13px; 
                padding: 8px 15px; 
                border: 1px solid #ff6b6b; 
                border-radius: 10px; 
                transition: all 0.3s ease;
            }}
            .logout-btn:hover {{ background: #ff6b6b; color: white; transform: translateY(-2px); }}
            
            .brand-logo .icon {{ font-size: 45px; color: var(--accent-gold); margin-bottom: 10px; }}
            .brand-logo .name {{ font-size: 30px; font-weight: 700; color: var(--primary-dark); margin: 0; }}
            .brand-logo .tagline {{ font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 2px; margin-top: 5px; }}

            /* Balance Card */
            .balance-card {{ 
                background: {color_balance}; 
                color: white; 
                padding: 25px; 
                border-radius: 18px; 
                text-align: center; 
                margin-bottom: 30px; 
                box-shadow: 0 5px 20px rgba(0,0,0,0.15);
                animation: scaleIn 0.5s ease-out;
            }}
            @keyframes scaleIn { from { transform: scale(0.9); opacity: 0; } to { transform: scale(1); opacity: 1; } }

            .balance-card small {{ opacity: 0.9; letter-spacing: 1px; font-size: 12px; }}
            .balance-card .amount {{ font-size: 38px; font-weight: 700; margin-top: 8px; }}

            /* Forms & Buttons */
            .form-section {{ 
                background: var(--bg-light); 
                padding: 25px; 
                border-radius: 18px; 
                border: 1px solid var(--border-light); 
                margin-bottom: 25px; 
            }}
            input, select {{ 
                width: calc(100% - 24px); 
                padding: 12px; 
                margin: 8px 0; 
                border-radius: 10px; 
                border: 1px solid var(--border-light); 
                box-sizing: border-box; 
                font-size: 15px; 
                outline: none;
                transition: border-color 0.3s ease;
            }}
            input:focus, select:focus {{ border-color: var(--primary-medium); }}
            
            .btn-action {{ 
                width: 100%; 
                padding: 14px; 
                margin-top: 15px; 
                border: none; 
                border-radius: 10px; 
                font-weight: 600; 
                font-size: 16px; 
                cursor: pointer; 
                transition: all 0.3s ease;
            }}
            .btn-save {{ background: var(--primary-medium); color: white; }}
            .btn-save:hover {{ background: var(--primary-dark); transform: translateY(-2px); }}
            
            .btn-export {{ background: #1d6f42; color: white; text-decoration: none; display: block; text-align: center; }}
            .btn-export:hover {{ background: #145532; transform: translateY(-2px); }}

            /* Transactions Table */
            h3 {{ 
                color: var(--primary-dark); 
                font-size: 20px; 
                margin-bottom: 20px; 
                display: flex; 
                align-items: center; 
            }}
            h3 .fas {{ margin-right: 10px; color: var(--accent-gold); }}
            
            table {{ 
                width: 100%; 
                border-collapse: separate; /* Para border-radius en td */
                border-spacing: 0 8px; /* Espacio entre filas */
            }}
            th {{ 
                text-align: left; 
                color: #888; 
                padding: 12px; 
                font-size: 11px; 
                text-transform: uppercase; 
                background: var(--bg-light);
                border-bottom: none; /* Eliminar borde inferior de th */
            }}
            td {{ 
                padding: 15px 12px; 
                background: var(--card-bg); 
                border-bottom: 1px solid var(--border-light); /* Borde entre filas */
            }}
            /* Estilos para la primera y última celda de cada fila */
            tr td:first-child {{ border-top-left-radius: 8px; border-bottom-left-radius: 8px; }}
            tr td:last-child {{ border-top-right-radius: 8px; border-bottom-right-radius: 8px; }}
            
            .transaction-description {{ font-weight: 600; color: var(--text-dark); }}
            .transaction-date {{ color: #aaa; font-size: 10px; display: block; margin-top: 4px; }}
            
            .monto-ingreso {{ color: #28a745; font-weight: 700; }}
            .monto-egreso {{ color: #dc3545; font-weight: 700; }}
            
            .btn-delete {{ 
                color: #ccc; 
                text-decoration: none; 
                font-size: 18px; 
                transition: color 0.3s ease, transform 0.2s ease;
            }}
            .btn-delete:hover {{ color: #dc3545; transform: scale(1.1); }}

            /* Footer */
            .footer {{ 
                text-align: center; 
                margin-top: 40px; 
                color: #888; 
                font-size: 13px; 
                border-top: 1px solid var(--border-light); 
                padding-top: 20px; 
            }}
            .footer a {{ color: var(--primary-medium); text-decoration: none; font-weight: 600; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <a href="/logout" class="logout-btn"><i class="fas fa-sign-out-alt"></i> CERRAR SESIÓN</a>
                <div class="brand-logo">
                    <i class="fas fa-cubes icon"></i>
                    <h1 class="name">D&S</h1>
                    <div class="tagline">Desarrollo de Software Admi.</div>
                </div>
            </div>
            
            <div class="balance-card">
                <small>BALANCE TOTAL</small>
                <div class="amount">${balance:,.2f}</div>
            </div>

            <div class="form-section">
                <form action="/add" method="POST">
                    <input name="desc" placeholder="Descripción de la operación (ej: Pago de cliente)" required>
                    <input name="monto" type="number" step="0.01" placeholder="Monto (ej: 1500.00)" required>
                    <select name="tipo">
                        <option value="Ingreso">➕ Ingreso</option>
                        <option value="Egreso">➖ Egreso</option>
                    </select>
                    <button type="submit" class="btn-action btn-save"><i class="fas fa-plus-circle"></i> AÑADIR REGISTRO</button>
                </form>
            </div>

            <a href="/export" class="btn-action btn-export"><i class="fas fa-file-csv"></i> DESCARGAR REPORTE EXCEL (CSV)</a>

            <h3><i class="fas fa-chart-line"></i> Historial de Movimientos ({len(rows)})</h3>
            <table>
                <thead>
                    <tr>
                        <th style="width: 55%;">DETALLE</th>
                        <th style="width: 35%;">MONTO</th>
                        <th style="width: 10%;"></th>
                    </tr>
                </thead>
                <tbody>
                    {"".join([f'''
                    <tr>
                        <td>
                            <span class="transaction-description">{row['descripcion']}</span>
                            <span class="transaction-date">{row['fecha']}</span>
                        </td>
                        <td class="monto-{'ingreso' if row['tipo'] == 'Ingreso' else 'egreso'}">
                            {' + ' if row['tipo'] == 'Ingreso' else ' - '}${row['monto']:,.2f}
                        </td>
                        <td style="text-align:right;">
                            <a href="/del/{row['id']}" class="btn-delete" onclick="return confirm('¿Confirmas que deseas eliminar este registro de forma permanente?')">
                                <i class="fas fa-trash-alt"></i>
                            </a>
                        </td>
                    </tr>
                    ''' for row in rows])}
                </tbody>
            </table>
            
            <div class="footer">
                Realizado por Dariana © 2024 | <a href="https://github.com/dariana29alexandra-commits" target="_blank">Visita mi GitHub</a>
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html_diseno_main, rows=rows)

@app.route("/add", methods=["POST"])
def add():
    if not session.get("logueado"): return redirect(url_for("login"))
    descripcion = request.form.get("desc")
    monto = float(request.form.get("monto"))
    tipo = request.form.get("tipo")
    fecha = datetime.now().strftime("%d/%b/%Y %H:%M") # Formato con mes abreviado
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("INSERT INTO transacciones (tipo, monto, descripcion, fecha) VALUES (?, ?, ?, ?)", (tipo, monto, descripcion, fecha))
    conn.commit(); conn.close()
    return redirect(url_for("home"))

@app.route("/del/<int:id>")
def delete(id):
    if not session.get("logueado"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("DELETE FROM transacciones WHERE id = ?", (id,))
    conn.commit(); conn.close()
    return redirect(url_for("home"))

@app.route("/export")
def export():
    if not session.get("logueado"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE); cursor = conn.cursor()
    cursor.execute("SELECT fecha, descripcion, tipo, monto FROM transacciones")
    rows = cursor.fetchall(); conn.close()
    si = io.StringIO()
    si.write("Fecha,Descripcion,Tipo,Monto\\n") # Encabezados CSV
    for row in rows:
        si.write(f"{row[0]},{row[1]},{row[2]},{row[3]}\\n")
    return Response(si.getvalue(), mimetype="text/csv", headers={{"Content-disposition":"attachment; filename=Reporte_DS_Administracion.csv"}})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
