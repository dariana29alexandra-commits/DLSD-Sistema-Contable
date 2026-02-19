from flask import Flask, render_template_string, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "clave_secreta_provisional"

# --- NUEVA CONTRASEÑA MÁS SIMPLE ---
PASSWORD_SISTEMA = "dariana29" 
DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS transacciones 
    (id INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT, monto REAL, descripcion TEXT, fecha TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Eliminamos espacios y comparamos
        password = request.form.get("password", "").strip()
        if password == PASSWORD_SISTEMA:
            session["user"] = "admin"
            return redirect(url_for("home"))
        else:
            return render_template_string('<h1>Clave incorrecta. Escribe: dariana29</h1><a href="/login">Volver</a>')
    
    return render_template_string('''
        <body style="background:#001f3f; color:white; font-family:sans-serif; text-align:center; padding:50px;">
            <div style="background:white; color:black; display:inline-block; padding:30px; border-radius:15px;">
                <h2>D&S Desarrollo</h2>
                <form method="POST">
                    <input type="password" name="password" placeholder="Clave" style="padding:10px; width:100%; border-radius:5px; border:1px solid #ccc;"><br><br>
                    <button type="submit" style="padding:10px 20px; background:#003366; color:white; border:none; border-radius:5px; cursor:pointer;">ENTRAR</button>
                </form>
            </div>
        </body>
    ''')

@app.route("/")
def home():
    if not session.get("user"): return redirect(url_for("login"))
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("SELECT * FROM transacciones ORDER BY id DESC").fetchall()
    conn.close()

    return render_template_string('''
        <body style="font-family:sans-serif; padding:20px; background:#f4f7f6;">
            <div style="max-width:500px; margin:auto; background:white; padding:20px; border-radius:15px; box-shadow:0 5px 15px rgba(0,0,0,0.1);">
                <h1 style="color:#003366; text-align:center;">D&S Soft Admi</h1>
                <p style="text-align:right;"><a href="/logout">Cerrar Sesión</a></p>
                
                <form action="/add" method="POST" style="background:#eee; padding:15px; border-radius:10px;">
                    <input name="desc" placeholder="Gasto/Ingreso" required style="width:100%; margin-bottom:10px; padding:8px;">
                    <input name="monto" type="number" step="0.01" placeholder="0.00" required style="width:100%; margin-bottom:10px; padding:8px;">
                    <select name="tipo" style="width:100%; margin-bottom:10px; padding:8px;">
                        <option value="Ingreso">Ingreso</option>
                        <option value="Egreso">Egreso</option>
                    </select>
                    <button style="width:100%; padding:10px; background:#003366; color:white; border:none; border-radius:5px;">GUARDAR</button>
                </form>

                <table style="width:100%; margin-top:20px; border-collapse:collapse;">
                    {% for row in rows %}
                    <tr style="border-bottom:1px solid #ddd;">
                        <td style="padding:10px;">{{ row.descripcion }}<br><small style="color:grey">{{ row.fecha }}</small></td>
                        <td style="text-align:right; font-weight:bold; color: {{ 'green' if row.tipo == 'Ingreso' else 'red' }}">
                            {{ '+' if row.tipo == 'Ingreso' else '-' }}${{ row.monto }}
                        </td>
                    </tr>
                    {% endfor %}
                </table>
            </div>
        </body>
    ''', rows=rows)

@app.route("/add", methods=["POST"])
def add():
    if not session.get("user"): return redirect(url_for("login"))
    conn = sqlite3.connect(DB_FILE)
    conn.execute("INSERT INTO transacciones (tipo, monto, descripcion, fecha) VALUES (?, ?, ?, ?)", 
                 (request.form['tipo'], request.form['monto'], request.form['desc'], datetime.now().strftime("%d/%m/%y %H:%M")))
    conn.commit(); conn.close()
    return redirect(url_for("home"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
