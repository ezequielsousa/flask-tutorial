#importa o banco de dados
import sqlite3

import click

# CRIAÇÃO DA  CONEXÃO COM O BANCO DE DADOS

#importa dois objetos especiais necessarios para ultilização do banco de dados
from flask import current_app, g

# estabelece a conexão com o banco
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

# verifica a conexão foi criada
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()



# funções que executarão os comandos SQL

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))


@click.command('init-db')
#Limpa os dados existentes e cria novas tabelas
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


#função que recebe o app e faz o registro
def init_app(app):
    #diz ao Flask para chamar essa função ao limpar após retornar a resposta
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)