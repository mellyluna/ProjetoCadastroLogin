from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime
import logging

app = Flask(__name__)
# Configuração mais específica do CORS
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]},
    r"/login": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]},
    r"/save_password": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]}
})

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuração do banco de dados
DATABASE_DIR = 'cadastro'
DATABASE = os.path.join(DATABASE_DIR, 'user.db')

def ensure_directory_exists():
    """Garante que a pasta cadastro existe"""
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        logger.info(f"Pasta '{DATABASE_DIR}' criada com sucesso!")

def init_database():
    """Inicializa o banco de dados e cria a tabela se não existir"""
    ensure_directory_exists()
    
    try:
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
        logger.info(f"Banco de dados inicializado: {DATABASE}")
        return True
    except Exception as e:
        logger.error(f"Erro ao inicializar banco de dados: {str(e)}")
        return False

def hash_password(password):
    """Gera um hash seguro da senha usando SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def verify_password(password, stored_hash):
    """Verifica se a senha fornecida corresponde ao hash armazenado"""
    return hash_password(password) == stored_hash

def create_user_html(username):
    """Cria a página HTML personalizada do usuário"""
    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bem-vindo, {username}!</title>
    <style>
        body {{
            background: linear-gradient(135deg, #000000 0%, #2d1b69 50%, #8B008B 100%);
            color: #ccc;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            text-align: center;
            padding: 50px;
            margin: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(139, 0, 139, 0.3);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5), 
                        0 0 60px rgba(139, 0, 139, 0.2);
        }}
        h1 {{
            color: #8B008B;
            margin-bottom: 20px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
        }}
        p {{
            font-size: 18px;
            line-height: 1.6;
            margin-bottom: 30px;
            color: #FFFFFF;
        }}
        .btn {{
            background: linear-gradient(135deg, #8B008B 0%, #FF0000 100%);
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 12px;
            display: inline-block;
            transition: all 0.3s ease;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 8px 25px rgba(139, 0, 139, 0.3);
            border: none;
            cursor: pointer;
            font-size: 16px;
        }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 15px 40px rgba(139, 0, 139, 0.4);
        }}
        .welcome-info {{
            background: rgba(255, 255, 255, 0.1);
            padding: 25px;
            border-radius: 15px;
            margin: 30px 0;
            border: 1px solid rgba(139, 0, 139, 0.2);
        }}
        .welcome-info p {{
            margin: 10px 0;
            font-size: 16px;
        }}
        .welcome-info strong {{
            color: #8B008B;
        }}
        .actions {{
            margin-top: 30px;
            display: flex;
            gap: 15px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        @media (max-width: 768px) {{
            .container {{
                margin: 20px;
                padding: 30px 20px;
            }}
            h1 {{
                font-size: 2em;
            }}
            .actions {{
                flex-direction: column;
                align-items: center;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Olá, {username}!</h1>
        <p>Bem-vindo ao seu painel personalizado! Você fez login com sucesso.</p>
        <div class="welcome-info">
            <p><strong>Usuário:</strong> {username}</p>
            <p><strong>Data de acesso:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
            <p><strong>Status:</strong> Conectado</p>
        </div>
        <div class="actions">
            <button onclick="logout()" class="btn">Sair</button>
            <button onclick="refreshPage()" class="btn" style="background: linear-gradient(135deg, #FF0000 0%, #8B008B 100%);">Atualizar</button>
        </div>
    </div>

    <script>
        function logout() {{
            if (confirm('Deseja realmente sair?')) {{
                localStorage.removeItem('currentUser');
                window.location.href = '/auth.html';
            }}
        }}

        function refreshPage() {{
            window.location.reload();
        }}

        // Verificar se o usuário está logado
        window.addEventListener('load', function() {{
            const currentUser = localStorage.getItem('currentUser');
            if (!currentUser || currentUser !== '{username}') {{
                alert('Sessão expirada. Redirecionando para login...');
                window.location.href = '/auth.html';
            }}
        }});
    </script>
</body>
</html>
"""
    
    filename = f'index_{username}.html'
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Página HTML criada para o usuário: {username}")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar página HTML para {username}: {str(e)}")
        return False

def save_user_to_db(username, password):
    """Salva o usuário no banco de dados e cria a página personalizada"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()

        # Hash da senha para segurança
        password_hash = hash_password(password)

        # Inserir usuário no banco
        cursor.execute('''
            INSERT INTO users (username, password_hash)
            VALUES (?, ?)
        ''', (username, password_hash))

        conn.commit()
        conn.close()

        # Criar a página HTML personalizada do usuário
        html_created = create_user_html(username)
        
        if html_created:
            logger.info(f"Usuário {username} criado com sucesso")
            return True, "Usuário criado com sucesso!"
        else:
            return True, "Usuário salvo, mas houve problema ao criar a página personalizada"

    except sqlite3.IntegrityError:
        logger.warning(f"Tentativa de criar usuário duplicado: {username}")
        return False, "Nome de usuário já existe!"
    except Exception as e:
        logger.error(f"Erro ao salvar usuário {username}: {str(e)}")
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
            logger.warning(f"Tentativa de login com usuário inexistente: {username}")
            return False, "Usuário não encontrado"
        
        stored_hash = result[0]
        
        # Verificar se a senha está correta
        if verify_password(password, stored_hash):
            logger.info(f"Login bem-sucedido para o usuário: {username}")
            return True, "Login realizado com sucesso!"
        else:
            logger.warning(f"Tentativa de login com senha incorreta para: {username}")
            return False, "Senha incorreta"
            
    except Exception as e:
        logger.error(f"Erro ao autenticar usuário {username}: {str(e)}")
        return False, f"Erro ao autenticar usuário: {str(e)}"

@app.route('/')
def index():
    """Redireciona para a página de login"""
    return send_from_directory('.', 'auth.html')

@app.route('/auth.html')
def auth_page():
    """Serve a página de login"""
    try:
        return send_from_directory('.', 'auth.html')
    except FileNotFoundError:
        return jsonify({'error': 'Página de login não encontrada'}), 404

@app.route('/cadastro.html')
def cadastro_page():
    """Serve a página de cadastro"""
    try:
        return send_from_directory('.', 'cadastro.html')
    except FileNotFoundError:
        return jsonify({'error': 'Página de cadastro não encontrada'}), 404

@app.route('/user/<username>')
def user_dashboard(username):
    """Serve a página personalizada do usuário"""
    # Validar se o username contém apenas caracteres válidos
    if not username.replace('_', '').replace('-', '').isalnum():
        return jsonify({'error': 'Nome de usuário inválido'}), 400
    
    filename = f'index_{username}.html'
    filepath = os.path.join('.', filename)
    
    if os.path.exists(filepath):
        try:
            return send_from_directory('.', filename)
        except Exception as e:
            logger.error(f"Erro ao servir página do usuário {username}: {str(e)}")
            return jsonify({'error': 'Erro ao carregar página do usuário'}), 500
    else:
        logger.warning(f"Página não encontrada para usuário: {username}")
        return f'''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Página não encontrada</title>
            <style>
                body {{ 
                    background: #111; 
                    color: #fff; 
                    text-align: center; 
                    font-family: Arial, sans-serif; 
                    padding: 50px; 
                }}
                .error {{ 
                    background: #333; 
                    padding: 30px; 
                    border-radius: 10px; 
                    display: inline-block; 
                }}
                a {{ 
                    color: #8B008B; 
                    text-decoration: none; 
                }}
            </style>
        </head>
        <body>
            <div class="error">
                <h1>Página não encontrada</h1>
                <p>A página personalizada para o usuário "{username}" não foi encontrada.</p>
                <p><a href="/auth.html">Voltar ao login</a></p>
            </div>
        </body>
        </html>
        ''', 404

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
            # Verificar se a página HTML do usuário existe, se não, criar
            filename = f'index_{username}.html'
            if not os.path.exists(filename):
                logger.info(f"Criando página HTML para usuário existente: {username}")
                create_user_html(username)
            
            return jsonify({
                'success': True,
                'message': message,
                'username': username,
                'redirect_url': f'/user/{username}'
            }), 200
        else:
            return jsonify({'error': message, 'success': False}), 401
            
    except Exception as e:
        logger.error(f"Erro no endpoint de login: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'success': False}), 500

@app.route('/save_password', methods=['POST'])
def save_password():
    """Endpoint para salvar a senha no banco de dados"""
    try:
        data = request.get_json()
        
        if not data or 'username' not in data or 'password' not in data:
            return jsonify({'error': 'Dados incompletos', 'success': False}), 400
        
        username = data['username'].strip()
        password = data['password']
        
        # Validações básicas
        if not username or not password:
            return jsonify({'error': 'Nome de usuário e senha são obrigatórios', 'success': False}), 400
        
        if len(username) < 3:
            return jsonify({'error': 'Nome de usuário deve ter pelo menos 3 caracteres', 'success': False}), 400
        
        if len(password) < 4:
            return jsonify({'error': 'Senha deve ter pelo menos 4 caracteres', 'success': False}), 400
        
        # Verificar se o username contém apenas caracteres válidos
        if not username.replace('_', '').replace('-', '').isalnum():
            return jsonify({'error': 'Nome de usuário deve conter apenas letras, números, _ e -', 'success': False}), 400
        
        # Salvar no banco de dados
        success, message = save_user_to_db(username, password)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'username': username
            }), 200
        else:
            return jsonify({'error': message, 'success': False}), 400
            
    except Exception as e:
        logger.error(f"Erro no endpoint de cadastro: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'success': False}), 500

@app.route('/list_users', methods=['GET'])
def list_users():
    """Endpoint para listar usuários (apenas para desenvolvimento)"""
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
        
        return jsonify({'users': user_list, 'total': len(user_list)}), 200
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({'error': f'Erro ao listar usuários: {str(e)}'}), 500

@app.route('/check_db', methods=['GET'])
def check_database():
    """Endpoint para verificar o status do banco de dados"""
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        
        # Verificar se o arquivo de banco existe
        db_exists = os.path.exists(DATABASE)
        
        conn.close()
        
        return jsonify({
            'message': 'Banco de dados funcionando',
            'total_users': count,
            'database_file': DATABASE,
            'database_directory': DATABASE_DIR,
            'database_exists': db_exists,
            'database_size': os.path.getsize(DATABASE) if db_exists else 0
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao verificar banco de dados: {str(e)}")
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
            
            # Criar página HTML para o usuário teste
            create_user_html(test_username)
            
            message = f"Usuário teste criado: {test_username} / {test_password}"
        else:
            message = f"Usuário teste já existe: {test_username} / {test_password}"
        
        conn.close()
        
        return jsonify({
            'message': message,
            'test_credentials': {
                'username': test_username,
                'password': test_password
            },
            'login_url': '/login',
            'user_page': f'/user/{test_username}'
        }), 200
        
    except Exception as e:
        logger.error(f"Erro ao criar usuário teste: {str(e)}")
        return jsonify({'error': f'Erro ao criar usuário teste: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handler para páginas não encontradas"""
    return jsonify({'error': 'Página não encontrada'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos do servidor"""
    logger.error(f"Erro interno do servidor: {str(error)}")
    return jsonify({'error': 'Erro interno do servidor'}), 500

if __name__ == '__main__':
    # Inicializar o banco de dados
    if not init_database():
        print("ERRO: Não foi possível inicializar o banco de dados!")
        exit(1)
    
    print("=== Sistema de Login com Flask ===")
    print(f"Banco de dados: {DATABASE}")
    print("Servidor iniciando...")
    print("Páginas disponíveis:")
    print("  - Login: http://localhost:5000/auth.html")
    print("  - Cadastro: http://localhost:5000/cadastro.html")
    print("  - Teste: http://localhost:5000/test_login")
    print("  - Status DB: http://localhost:5000/check_db")
    print("  - Listar usuários: http://localhost:5000/list_users")
    print("Para parar o servidor: Ctrl+C")
    
    # Executar a aplicação Flask
    app.run(debug=True, host='0.0.0.0', port=5000)