import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy import or_

app = Flask(__name__)
try:
    prodURI = os.getenv('DATABASE_URL')
    prodURI = prodURI.replace("postgres://", "postgresql://")
    app.config['SQLALCHEMY_DATABASE_URI'] = prodURI
except:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1@localhost/api_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class UserModel(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    token = db.Column(db.String(100))

    def __init__(self, email, password, token):
        self.email = email
        self.password = password
        self.token = token

class WebhookData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    valor = db.Column(db.Float, nullable=True)
    forma_pagamento = db.Column(db.String(100), nullable=True)
    parcelas = db.Column(db.Integer, nullable=True)
    status_atual = db.Column(db.String(200), nullable=True)  # Nova coluna para as mensagens das tratativas

    def __init__(self, nome, email, status, valor, forma_pagamento, parcelas, status_atual):
        self.nome = nome
        self.email = email
        self.status = status
        self.valor = valor
        self.forma_pagamento = forma_pagamento
        self.parcelas = parcelas
        self.status_atual = status_atual

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_post():
    data = request.form
    email = data['email']
    password = data['password']
    user = UserModel.query.filter_by(email=email).first()

    if not user or user.password != password:
        return jsonify({'message': 'Credenciais inválidas'}), 401

    return redirect(url_for('webhooks', _method='GET'))

@app.route('/signup', methods=['GET'])
def show_signup_form():
    return render_template('signup.html')


@app.route('/signup', methods=['POST'])
def signup_post():
    data = request.form
    email = data['email']
    password = data['password']
    confirm_password = data['confirm_password']
    token = data['token']

    expected_token = 'uhdfaAADF123'
    if token != expected_token:
        return render_template('signup.html', message='Token inválido')

    if UserModel.query.filter_by(email=email).first():
        return render_template('signup.html', message='Email já cadastrado')

    if password != confirm_password:
        return render_template('signup.html', message='As senhas não correspondem')

    new_user = UserModel(email=email, password=password, token=expected_token)
    db.session.add(new_user)
    db.session.commit()

    return render_template('signup.html', message='Cadastro realizado com sucesso! Faça o login.')



@app.route('/webhooks', methods=['GET'])
def webhooks():
    webhooks = WebhookData.query.all()
    return render_template('webhooks.html', webhooks=webhooks)

@app.route('/webhook1000/', methods=['POST'])
def handle_webhook():
    response = request.data
    response_str = response.decode('utf-8')
    response_json = json.loads(response_str)
    nome = response_json['nome']
    email = response_json['email']
    status = response_json['status']
    valor = response_json['valor']
    forma_pagamento = response_json['forma_pagamento']
    parcelas = response_json['parcelas']

    if status == 'aprovado':
        status_atual = liberar_acesso(nome, email)
    elif status == 'recusado':
        status_atual = enviar_mensagem_pagamento_recusado(nome, email)
    elif status == 'reembolsado':
        status_atual = remover_acesso(nome, email)
    else:
        status_atual = 'Tratativa não definida'

    new_webhook = WebhookData(nome=nome, email=email, status=status, valor=valor,
                              forma_pagamento=forma_pagamento, parcelas=parcelas, status_atual=status_atual)
    db.session.add(new_webhook)
    db.session.commit()

    return 'Webhook recebido'

def liberar_acesso(nome, email):
    status_atual = f"Acesso liberarado , Seja muito bem-vindo(a) à nossa plataforma {nome} {email}"
    print(status_atual)
    return status_atual

def enviar_mensagem_pagamento_recusado(nome, email):
    status_atual = f"Seu pagamento foi recusado {nome} {email}"
    print(status_atual)
    return status_atual

def remover_acesso(nome, email):
    status_atual = f"Seu acesso removido, {nome} {email}"
    print(status_atual)
    return status_atual

@app.route('/filtrar_tratativas', methods=['GET'])
def filtrar_tratativas():
    email = request.args.get('email')
    if email:
        tratativas = WebhookData.query.filter(WebhookData.email.ilike(f'%{email}%')).all()
    else:
        tratativas = WebhookData.query.all()
    return render_template('webhooks.html', webhooks=tratativas)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
