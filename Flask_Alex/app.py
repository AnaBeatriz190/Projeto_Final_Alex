from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tarefas.db'
app.config['SECRET_KEY'] = 'chave_secreta'  # Gere uma chave mais segura se necessário
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Modelo de Usuário
class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_usuario = db.Column(db.String(150), unique=True, nullable=False)
    senha = db.Column(db.String(150), nullable=False)
    tarefas = db.relationship('Tarefa', backref='dono', lazy=True)

# Modelo de Tarefa
class Tarefa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.String(500), nullable=True)
    data_vencimento = db.Column(db.String(100), nullable=False)
    concluida = db.Column(db.Boolean, default=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)

@login_manager.user_loader
def load_usuario(usuario_id):
    return Usuario.query.get(int(usuario_id))

@app.route('/')
@login_required
def index():
    tarefas = Tarefa.query.filter_by(usuario_id=current_user.id).all()
    return render_template('index.html', tarefas=tarefas)

@app.route('/adicionar_tarefa', methods=['GET', 'POST'])
@login_required
def adicionar_tarefa():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']
        data_vencimento = request.form['data_vencimento']
        nova_tarefa = Tarefa(titulo=titulo, descricao=descricao, data_vencimento=data_vencimento, usuario_id=current_user.id)
        db.session.add(nova_tarefa)
        db.session.commit()
        flash("Tarefa adicionada com sucesso!", "success")
        return redirect(url_for('index'))
    return render_template('tarefa_form.html')

@app.route('/editar_tarefa/<int:tarefa_id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if tarefa.dono != current_user:
        flash("Acesso negado!", "danger")
        return redirect(url_for('index'))

    if request.method == 'POST':
        tarefa.titulo = request.form['titulo']
        tarefa.descricao = request.form['descricao']
        tarefa.data_vencimento = request.form['data_vencimento']
        db.session.commit()
        flash("Tarefa atualizada com sucesso!", "success")
        return redirect(url_for('index'))

    return render_template('tarefa_form.html', tarefa=tarefa)

@app.route('/excluir_tarefa/<int:tarefa_id>', methods=['POST'])
@login_required
def excluir_tarefa(tarefa_id):
    tarefa = Tarefa.query.get_or_404(tarefa_id)
    if tarefa.dono != current_user:
        flash("Acesso negado!", "danger")
        return redirect(url_for('index'))
    db.session.delete(tarefa)
    db.session.commit()
    flash("Tarefa excluída com sucesso!", "danger")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(nome_usuario=nome_usuario).first()
        if usuario and usuario.senha == senha:
            login_user(usuario)
            return redirect(url_for('index'))
        flash("Credenciais inválidas!", "danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if request.method == 'POST':
        nome_usuario = request.form['nome_usuario']
        senha = request.form['senha']
        novo_usuario = Usuario(nome_usuario=nome_usuario, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        flash("Usuário cadastrado com sucesso!", "success")
        return redirect(url_for('login'))
    return render_template('cadastro.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Cria o banco de dados na primeira execução
    app.run(debug=True)
