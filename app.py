from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1@localhost/api_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de dados do usuário
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password):
        self.email = email
        self.password = password

# Modelo de dados do webhook para salvar
class WebhookData(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    valor = db.Column(db.Float, nullable=True)
    forma_pagamento = db.Column(db.String(100), nullable=True)
    parcelas = db.Column(db.Integer, nullable=True)

# Rota para exibir a tela de login
@app.route('/login', methods=['GET'])
def login():
    return render_template('login.html')

# Rota para autenticação de login
@app.route('/login', methods=['POST', 'GET'])
def login_post():
    data = request.form
    email = data['email']
    password = data['password']

    user = User.query.filter_by(email=email).first()

    if not user or user.password != password:
        return jsonify({'message': 'Credenciais inválidas'}), 401

    # Aqui você pode gerar um token de autenticação para o usuário se desejar

    return jsonify({'message': 'Login bem-sucedido'}), 200

# Rota para exibir a tela de cadastro
@app.route('/signup', methods=['GET'])
def signup():
    return render_template('signup.html')

# Rota para criar uma nova conta
@app.route('/signup', methods=['POST'])
def signup_post():
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

# Rota para exibir a tela de webhooks
@app.route('/webhooks', methods=['GET'])
def webhooks():
    webhooks = WebhookData.query.all()
    return render_template('webhooks.html', webhooks=webhooks)

# Rota para receber o webhook do sistema de pagamento
@app.route('/webhook1000/', methods=['POST'])
def handle_webhook():
    response = request.data
    response_str = response.decode('utf-8')
    response_json = json.loads(response_str)
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

    # Salvar o webhook no banco de dados
    new_webhook = WebhookData(nome=nome, email=email, status=status, valor=valor,
                              forma_pagamento=forma_pagamento, parcelas=parcelas)
    db.session.add(new_webhook)
    db.session.commit()

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

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
