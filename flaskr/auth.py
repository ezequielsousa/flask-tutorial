import functools

# cria uma blueprint
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')


# CRIA A PAGINA DE REGISTRO

# @bp.route associa a URL register à registerfunção de visualização
@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
       # request.form é um tipo especial de dict mapeamento de chaves e valores de formulário enviados
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                # db.execute recebe uma consulta SQL com ? espaços reservados para qualquer entrada do usuário e uma tupla de valores para substituir os espaços reservados.
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    #generate_password_hash()é usado para fazer o hash seguro da senha e esse hash é armazenado
                    (username, generate_password_hash(password)),
                )
                # Como essa consulta feita ao banco modifica os dados db.commit() precisa ser chamada posteriormente ao  para salvar as alterações
                db.commit()
                # sqlite3.IntegrityError ocorrerá se o nome de usuário já existir, sera mostrado ao usuario um erro de validação
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                #  url_for() gera a URL para a visualização de login
                # redirect() gera uma resposta de redirecionamento para a URL gerada
                return redirect(url_for("auth.login"))
        # se a validação falhar será mostrado um erro ao usuário
        #  flash() armazena mensagens que podem ser recuperadas ao renderizar o modelo
        flash(error)
    # . render_template() renderizará um modelo contendo o HTML
    return render_template('auth/register.html')


    # CRIA A PAGINA DE LOGIN

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        # fetchone() retorna uma linha da consulta
        ).fetchone()

        if user is None:
            error = 'Incorrect username.'
        # check_password_hash() faz o hash da senha enviada da mesma maneira que o hash armazenado e os compara com segurança. Se corresponderem, a senha é válida
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            # session é um dictque armazena dados entre solicitações
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')



# bp.before_app_request() registra uma função que é executada antes da função de visualização, não importa qual URL é solicitada.
@bp.before_app_request
# load_logged_in_user verifica se um id de usuário está armazenado no session e obtém os dados desse usuário do banco de dados, armazenando-os em g.user, que dura a duração da solicitação. Se não houver id de usuário, ou se o id não existir, g.user será None
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()


# SAIR DO LOGIN
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


# EXIGE ALTETICAÇÃO DE OUTROS USUARIOS
# essa função verifica se um usuário está carregado e redireciona para a página de login
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            # url_for() gera a URL para uma exibição com base em um nome e argumentos.
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view