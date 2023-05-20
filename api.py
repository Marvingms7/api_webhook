from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from sqlalchemy.orm import sessionmaker, session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # Configurar a URL do banco de dados
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

# Modelo de dados do usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password):
        self.email = email
        self.password = password

#Modelo de dados do webhook para salvar

class WebhookData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    valor = db.Column(db.Float, nullable=True)
    forma_pagamento = db.Column(db.String(100), nullable=True)
    parcelas = db.Column(db.Integer, nullable=True)

# Rota para criar uma nova conta
@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    email = data['email']
    password = data['password']
    confirm_password = data['confirm_password']
    token = data['token']

    if token != 'uhdfaAADF123':
        return jsonify({'message': 'Token inválido'}), 401

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'Email já cadastrado'}), 400

    if password != confirm_password:
        return jsonify({'message': 'As senhas não correspondem'}), 400

    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Conta criada com sucesso'}), 201

# Rota para autenticação de login
@app.route('/login', methods=['POST'])
def login():
    data = request.form
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        return jsonify({'message': 'Credenciais inválidas'}), 401

    # Aqui você pode gerar um token de autenticação para o usuário se desejar

    return jsonify({'message': 'Login bem-sucedido'}), 200

# Dicionário para armazenar os registros de webhooks
webhooks = []

# Rota para receber o webhook do sistema de pagamento
@app.route('/webhook1000', methods=['POST'])
def handle_webhook():
    response = request.data
    response_str = response.decode('utf-8')
    response_json = json.loads(response_str)
    webhooks.append(response_json)
    print(response_json)

    # Extrair os dados do webhook
    nome = response_json['nome']
    email = response_json['email']
    status = response_json['status']
    valor = response_json['valor']
    forma_pagamento = response_json['forma_pagamento']
    parcelas = response_json['parcelas']

    # Verificar o status do pagamento
    if status == 'aprovado':
        # Liberar acesso ao curso
        liberar_acesso(nome, email)
        # Enviar mensagem de boas-vindas
        enviar_mensagem_boas_vindas(nome, email)
    elif status == 'recusado':
        # Enviar mensagem de pagamento recusado
        enviar_mensagem_pagamento_recusado(nome, email)
    elif status == 'reembolsado':
        # Remover acesso ao curso
        remover_acesso(nome, email)
    session.bulk_insert_mappings(WebhookData, webhooks)
    return 'Webhook recebido'

# Função para liberar acesso ao curso
def liberar_acesso(nome, email):
    print(f"Liberar acesso do cliente: {nome} ({email})")

# Função para enviar mensagem de boas-vindas
def enviar_mensagem_boas_vindas(nome, email):
    print(f"Seja muito bem-vindo a nossa plataforma: {nome} ({email})")

# Função para enviar mensagem de pagamento recusado
def enviar_mensagem_pagamento_recusado(nome, email):
    print(f"Seu pagamento foi recusado: {nome} ({email})")

# Função para remover acesso ao curso
def remover_acesso(nome, email):
    print(f"Remover acesso do cliente: {nome} ({email})")

# Rota para exibir os registros de webhooks
@app.route('/webhooks', methods=['GET'])
def get_webhooks():
    return jsonify(webhooks)

# Rota para pesquisar tratativas por cliente
@app.route('/tratativas/<cliente>', methods=['GET'])
def get_tratativas(cliente):
    tratativas = []
    for webhook in webhooks.values():
        if webhook['nome'] == cliente:
            tratativas.append(webhook)
    return jsonify({'tratativas': tratativas})

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)