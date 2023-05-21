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

    def __init__(self, nome, email, status, valor, forma_pagamento, parcelas):
        self.nome = nome
        self.email = email
        self.status = status
        self.valor = valor
        self.forma_pagamento = forma_pagamento
        self.parcelas = parcelas

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
        return jsonify({'message': 'Token inválido'}), 401

    if UserModel.query.filter_by(email=email).first():
        return jsonify({'message': 'Email já cadastrado'}), 400

    if password != confirm_password:
        return jsonify({'message': 'As senhas não correspondem'}), 400

    new_user = UserModel(email=email, password=password, token=expected_token)
    db.session.add(new_user)
    db.session.commit()

    # Redirecionar o usuário para a rota '/webhooks'
    return redirect(url_for('webhooks'))



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
        liberar_acesso(nome, email)
        enviar_mensagem_boas_vindas(nome, email)
    elif status == 'recusado':
        enviar_mensagem_pagamento_recusado(nome, email)
    elif status == 'reembolsado':
        remover_acesso(nome, email)

    new_webhook = WebhookData(nome=nome, email=email, status=status, valor=valor,
                              forma_pagamento=forma_pagamento, parcelas=parcelas)
    db.session.add(new_webhook)
    db.session.commit()

    return 'Webhook recebido'

def liberar_acesso(nome, email):
    print(f"Liberar acesso do cliente: {nome} ({email})")

def enviar_mensagem_boas_vindas(nome, email):
    print(f"Seja muito bem-vindo à nossa plataforma: {nome} ({email})")

def enviar_mensagem_pagamento_recusado(nome, email):
    print(f"Seu pagamento foi recusado: {nome} ({email})")

def remover_acesso(nome, email):
    print(f"Remover acesso do cliente: {nome} ({email})")

@app.route('/filtrar_tratativas', methods=['GET'])
def filtrar_tratativas():
    email = request.args.get('email')
    if not email:
        return render_template('webhooks.html', webhooks=[])
    tratativas = WebhookData.query.filter(WebhookData.email.ilike(f'%{email}%')).all()
    return render_template('webhooks.html', webhooks=tratativas)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
