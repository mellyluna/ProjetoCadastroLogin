from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuração do banco de dados - agora na subpasta cadastro
DATABASE_DIR = 'cadastro'
DATABASE = os.path.join(DATABASE_DIR, 'user.db')

def ensure_directory_exists():
    """Garante que a pasta cadastro existe"""
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        print(f"Pasta '{DATABASE_DIR}' criada com sucesso!")

def init_database():
    """Inicializa o banco de dados e cria a tabela se não existir"""
    ensure_directory_exists()
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Criar tabela users se não existir
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Banco de dados inicializado: {DATABASE}")

def hash_password(password):
    """Gera um hash seguro da senha usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, stored_hash):
    """Verifica se a senha fornecida corresponde ao hash armazenado"""
    return hash_password(password) == stored_hash

def save_user_to_db(username, password):
    """Salva o usuário no banco de dados"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Hash da senha para segurança
        password_hash = hash_password(password)
        
        # Inserir usuário
        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', (username, password_hash))
        
        conn.commit()
        conn.close()
        
        return True, "Usuário salvo com sucesso!"
        
    except sqlite3.IntegrityError:
        return False, "Nome de usuário já existe!"
    except Exception as e:
        return False, f"Erro ao salvar usuário: {str(e)}"

def authenticate_user(username, password):
    """Autentica um usuário verificando username e senha"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Buscar usuário pelo username
        cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result is None:
            return False, "Usuário não encontrado"
        
        stored_hash = result[0]
        
        # Verificar se a senha está correta
        if verify_password(password, stored_hash):
            return True, "Login realizado com sucesso!"
        else:
            return False, "Senha incorreta"
            
    except Exception as e:
        return False, f"Erro ao autenticar usuário: {str(e)}"

@app.route('/')
def index():
    """Redireciona para a página de login"""
    return send_from_directory('.', 'auth.html')

@app.route('/auth.html')
def auth_page():
    """Serve a página de login"""
    return send_from_directory('.', 'auth.html')

@app.route('/cadastro.html')
def cadastro_page():
    """Serve a página de cadastro"""
    return send_from_directory('.', 'cadastro.html')

@app.route('/login', methods=['POST'])
def login():
    """Endpoint para autenticação de usuários"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Dados incompletos', 'success': False}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Validações básicas
        if not username or not password:
            return jsonify({'error': 'Nome de usuário e senha são obrigatórios', 'success': False}), 400
        
        # Tentar autenticar o usuário
        success, message = authenticate_user(username, password)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'username': username
            }), 200
        else:
            return jsonify({'error': message, 'success': False}), 401
            
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}', 'success': False}), 500

@app.route('/save_password', methods=['POST'])
def save_password():
    """Endpoint para salvar a senha no banco de dados"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Dados incompletos'}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Validações básicas
        if not username or not password:
            return jsonify({'error': 'Nome de usuário e senha são obrigatórios'}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Nome de usuário deve ter pelo menos 3 caracteres'}), 400
        
        if len(password) < 4:
            return jsonify({'error': 'Senha deve ter pelo menos 4 caracteres'}), 400
        
        # Salvar no banco de dados
        success, message = save_user_to_db(username, password)
        
        if success:
            return jsonify({'message': message}), 200
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        return jsonify({'error': f'Erro interno do servidor: {str(e)}'}), 500

@app.route('/list_users', methods=['GET'])
def list_users():
    """Endpoint para listar usuários (apenas para teste - remova em produção)"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        
        conn.close()
        
        user_list = []
        for user in users:
            user_list.append({
                'id': user[0],
                'username': user[1],
                'created_at': user[2]
            })
        
        return jsonify({'users': user_list}), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao listar usuários: {str(e)}'}), 500

@app.route('/check_db', methods=['GET'])
def check_database():
    """Endpoint para verificar o status do banco de dados"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            'message': 'Banco de dados funcionando',
            'total_users': count,
            'database_file': DATABASE,
            'database_directory': DATABASE_DIR
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao verificar banco de dados: {str(e)}'}), 500

@app.route('/test_login', methods=['GET'])
def test_login():
    """Endpoint para testar o sistema de login (apenas para desenvolvimento)"""
    try:
        # Criar um usuário teste se não existir
        test_username = "admin"
        test_password = "1234"
        
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        # Verificar se o usuário teste já existe
        cursor.execute('SELECT username FROM users WHERE username = ?', (test_username,))
        if cursor.fetchone() is None:
            # Criar usuário teste
            password_hash = hash_password(test_password)
            cursor.execute('''
                INSERT INTO users (username, password_hash)
                VALUES (?, ?)
            ''', (test_username, password_hash))
            conn.commit()
            message = f"Usuário teste criado: {test_username} / {test_password}"
        else:
            message = f"Usuário teste já existe: {test_username} / {test_password}"
        
        conn.close()
        
        return jsonify({
            'message': message,
            'test_credentials': {
                'username': test_username,
                'password': test_password
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': f'Erro ao criar usuário teste: {str(e)}'}), 500

if __name__ == '__main__':
    # Inicializar o banco de dados
    init_database()
    
    print("=== Sistema de Login com Flask ===")
    print(f"Banco de dados: {DATABASE}")
    print("Servidor iniciando...")
    print("Páginas disponíveis:")
    print("  - Login: http://localhost:5000/auth.html")
    print("  - Cadastro: http://localhost:5000/cadastro.html")
    print("  - Teste: http://localhost:5000/test_login")
    print("  - Status DB: http://localhost:5000/check_db")
    print("Para parar o servidor: Ctrl+C")
    
    # Executar a aplicação Flask
    app.run(debug=True, host='0.0.0.0', port=5000)