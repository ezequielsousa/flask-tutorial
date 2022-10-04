import os

from flask import Flask


def create_app(test_config=None):
    # cria e configura o aplicativo
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # carrega a configuração da instância, se existir, quando não estiver testando
        app.config.from_pyfile('config.py', silent=True)
    else:
        # carrega a configuração de teste se passado em
        app.config.from_mapping(test_config)

    # verifique se a pasta da instância existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # uma página simples que diz olá
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    return app