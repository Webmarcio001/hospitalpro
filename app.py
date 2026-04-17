from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'chave-secreta-forte'

DB = 'pacientes.db'

# BANCO
def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute('''CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        cpf TEXT NOT NULL
    )''')
    conn.commit()
    conn.close()

with app.app_context():
    init_db()

# LOGIN
@app.route('/', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        if request.form['user'] == 'admin' and request.form['pass'] == '123':
            session['logado'] = True
            return redirect(url_for('lista'))
        flash('Login inválido')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# LISTA
@app.route('/lista')
def lista():
    if not session.get('logado'):
        return redirect('/')
    conn = get_db_connection()
    pacientes = conn.execute('SELECT * FROM pacientes').fetchall()
    conn.close()
    return render_template('lista.html', pacientes=pacientes)

# CADASTRO
@app.route('/cadastro', methods=['GET','POST'])
def cadastro():
    if not session.get('logado'):
        return redirect('/')

    if request.method == 'POST':
        conn = get_db_connection()
        conn.execute('INSERT INTO pacientes (nome, cpf) VALUES (?,?)',
                     (request.form['nome'], request.form['cpf']))
        conn.commit()
        conn.close()
        return redirect('/lista')

    return render_template('cadastro.html')

# EDITAR
@app.route('/editar/<int:id>', methods=['GET','POST'])
def editar(id):
    if not session.get('logado'):
        return redirect('/')

    conn = get_db_connection()
    paciente = conn.execute('SELECT * FROM pacientes WHERE id=?',(id,)).fetchone()

    if request.method == 'POST':
        conn.execute('UPDATE pacientes SET nome=?, cpf=? WHERE id=?',
                     (request.form['nome'], request.form['cpf'], id))
        conn.commit()
        conn.close()
        return redirect('/lista')

    conn.close()
    return render_template('editar.html', paciente=paciente)

# DELETAR
@app.route('/deletar/<int:id>', methods=['POST'])
def deletar(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM pacientes WHERE id=?',(id,))
    conn.commit()
    conn.close()
    return redirect('/lista')

if __name__ == '__main__':
    app.run(debug=True)

