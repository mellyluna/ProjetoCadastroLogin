from flask import Flask, request, jsonify, render_template_string, send_from_directory, redirect, url_for
from flask_cors import CORS
import sqlite3
import hashlib
import os
from datetime import datetime
import logging
import sys # Importa sys para lidar com caminhos do PyInstaller
import shutil # Importa shutil para lidar com caminhos do PyInstaller

# --- INÍCIO DA MODIFICAÇÃO CRÍTICA DO CAMINHO ---
# IMPORTANTE: CAMINHO HARDCODED TEMPORÁRIO PARA TESTE
# Esta seção sobrescreve a lógica original de determinação de BASE_DIR.
# Substitua 'C:\\Users\\Luna\\Desktop\\Projeto1.2' pelo caminho EXATO da sua pasta 'Projeto1.2'.
# Use 'r' para raw string (r'...') para evitar problemas com barras invertidas.
# OU, se preferir, use barras duplas: 'C:\\Users\\Luna\\Desktop\\Projeto1.2'
BASE_DIR_FORCED = r'C:\Users\Luna\Desktop\Projeto1.2'

# Configura o Flask para usar o BASE_DIR_FORCED como template_folder e static_folder.
# Isso significa que seus arquivos HTML (auth.html, cadastro.html, Melly_index.html, admin_panel.html etc.)
# devem estar diretamente na pasta definida em BASE_DIR_FORCED.
app = Flask(__name__, template_folder=BASE_DIR_FORCED, static_folder=BASE_DIR_FORCED)

# Define o caminho para a pasta 'cadastro' dentro do seu diretório de projeto
DATABASE_DIR_PATH = os.path.join(BASE_DIR_FORCED, 'cadastro')

# Define o caminho completo para o arquivo user.db
DATABASE_PATH = os.path.join(DATABASE_DIR_PATH, 'user.db')
# --- FIM DA MODIFICAÇÃO CRÍTICA DO CAMINHO ---


# Configuração mais específica do CORS
CORS(app, resources={
    r"/api/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]},
    r"/login": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]},
    r"/save_password": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]},
    r"/list_users": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]},
    r"/admin/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]},
    r"/*": {"origins": ["http://localhost:5000", "http://127.0.0.1:5000"]}
})

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define a pasta base para os arquivos de usuário (dentro do BASE_DIR_FORCED)
USER_DIR = 'user'
USER_DIR_PATH = os.path.join(BASE_DIR_FORCED, USER_DIR)


def ensure_directory_exists():
    """Garante que as pastas necessárias existem"""
    # Criar pasta do banco de dados
    if not os.path.exists(DATABASE_DIR_PATH):
        os.makedirs(DATABASE_DIR_PATH)
        logger.info(f"Pasta '{DATABASE_DIR_PATH}' criada com sucesso!")
    
    # Criar pasta base dos usuários
    if not os.path.exists(USER_DIR_PATH):
        os.makedirs(USER_DIR_PATH)
        logger.info(f"Pasta '{USER_DIR_PATH}' criada com sucesso!")

def ensure_user_directory_exists(username):
    """Garante que a pasta do usuário específico existe"""
    user_folder = os.path.join(USER_DIR_PATH, username)
    if not os.path.exists(user_folder):
        os.makedirs(user_folder)
        logger.info(f"Pasta do usuário '{user_folder}' criada com sucesso!")
    return user_folder

def init_database():
    """Inicializa o banco de dados e cria a tabela se não existir"""
    ensure_directory_exists()
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Criar tabela users se não existir
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                email TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info(f"Banco de dados inicializado: {DATABASE_PATH}")
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

def create_user_html(username, email=None):
    """Cria a página HTML personalizada do usuário na sua pasta específica e copia arquivos necessários."""
    # Lê o conteúdo de Melly_index.html para usar como template para novos usuários
    # Usamos a versão do template que o usuário forneceu, que tem as opções do grimório
    melly_index_path = os.path.join(app.template_folder, 'Melly_index.html')
    html_content = ""
    if not os.path.exists(melly_index_path):
        logger.warning(f"Melly_index.html não encontrado em {melly_index_path}. Usando um template básico para {username}.")
        # Fallback para um template mais simples se Melly_index.html não for encontrado
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
        .btn:active {{
            transform: translateY(0);
            box-shadow: 0 5px 15px rgba(139, 0, 139, 0.6);
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
        .folder-info {{
            background: rgba(139, 0, 139, 0.1);
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            border: 1px solid rgba(139, 0, 139, 0.2);
        }}
        .folder-info h3 {{
            color: #8B008B;
            margin-bottom: 10px;
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
        
        <div class="folder-info">
            <h3>📁 Sua Pasta Pessoal</h3>
            <p>Esta página está localizada em: <strong>user/{username}/{username}_index.html</strong></p>
            <p>Você tem sua própria pasta exclusiva para arquivos e conteúdos!</p>
        </div>
        
        <div class="welcome-info">
            <p><strong>Usuário:</strong> {username}</p>
            <p><strong>Email:</strong> {email if email else 'Não informado'}</p>
            <p><strong>Data de acesso:</strong> {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</p>
            <p><strong>Status:</strong> Conectado</p>
            <p><strong>Pasta:</strong> user/{username}/</p>
        </div>
        <div class="actions">
            <button onclick="logout()" class="btn">Sair</button>
            <button onclick="refreshPage()" class="btn" style="background: linear-gradient(135deg, #FF0000 0%, #8B008B 100%);">Atualizar</button>
            <a href="calendario.html" class="btn" style="background: linear-gradient(135deg, #0044cc 0%, #00ccff 100%);">Calendário</a>
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
    else:
        with open(melly_index_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Substitui "Melly" e informações estáticas pelo nome de usuário dinâmico
        html_content = html_content.replace("Grimório de Melly", f"Grimório de {username}")
        html_content = html_content.replace("Portal das Sombras • Domínio da Bruxa", f"Portal de {username} • Domínio do Usuário")
        html_content = html_content.replace("© 2025 Grimório de Melly", f"© {datetime.now().year} Grimório de {username}")
        
        # === INJETAR A FUNÇÃO navigateTo CORRIGIDA E LÓGICA DE VERIFICAÇÃO DE SESSÃO ===
        new_script_content = f"""
        <script>
        // === FUNÇÃO DE NAVEGAÇÃO CORRIGIDA ===
        function navigateTo(page) {{
            // Obtém o nome de usuário atual da URL
            const pathParts = window.location.pathname.split('/');
            let currentUsername = '';

            // Encontra o segmento 'user' e o nome de usuário que o segue
            for (let i = 0; i < pathParts.length; i++) {{
                if (pathParts[i] === 'user' && i + 1 < pathParts.length) {{
                    currentUsername = pathParts[i + 1];
                    // Se o nome de usuário tiver '_index.html' (do Melly_index.html gerado), remove
                    if (currentUsername.endsWith('_index.html')) {{
                        currentUsername = currentUsername.replace('_index.html', '');
                    }}
                    break;
                }}
            }}
            
            let targetUrl = '';
            if (page.startsWith('http://') || page.startsWith('https://') || page.startsWith('/')) {{
                targetUrl = page; // Se já for um caminho absoluto ou URL completa
            }} else if (currentUsername) {{
                // Constrói a URL corretamente: /user/nome_do_usuario/pagina.html
                targetUrl = `/user/${{currentUsername}}/${{page}}`;
            }} else {{
                console.error("Não foi possível determinar o nome de usuário para navegação. Tentando redirecionar para a raiz.");
                targetUrl = `/${{page}}`; // Fallback para a raiz se o nome de usuário não for encontrado na URL
            }}

            // Efeito de transição
            document.body.style.transition = 'opacity 0.5s ease';
            document.body.style.opacity = '0.5';
            
            setTimeout(() => {{
                window.location.href = targetUrl;
            }}, 500);
        }}
        // === FIM DA FUNÇÃO DE NAVEGAÇÃO CORRIGIDA ===

        // === LÓGICA DE VERIFICAÇÃO DE SESSÃO E LOGOUT ===
        function logout() {{
            if (confirm('Deseja realmente sair?')) {{
                localStorage.removeItem('currentUser');
                window.location.href = '/auth.html';
            }}
        }}

        function refreshPage() {{
            window.location.reload();
        }}

        // Verificar se o usuário está logado ao carregar a página
        window.addEventListener('load', function() {{
            const currentUser = localStorage.getItem('currentUser');
            const pathParts = window.location.pathname.split('/');
            let urlUsername = '';
            
            for (let i = 0; i < pathParts.length; i++) {{
                if (pathParts[i] === 'user' && i + 1 < pathParts.length) {{
                    urlUsername = pathParts[i + 1];
                    if (urlUsername.endsWith('_index.html')) {{
                        urlUsername = urlUsername.replace('_index.html', '');
                    }}
                    break;
                }}
            }}

            if (!currentUser || currentUser !== urlUsername) {{
                alert('Sessão expirada ou usuário incorreto. Redirecionando para login...');
                window.location.href = '/auth.html';
            }}
        }});
        // === FIM DA LÓGICA DE VERIFICAÇÃO DE SESSÃO E LOGOUT ===

        // Lógica para mostrar o botão "Acesso Administrativo" apenas para Melly
        document.addEventListener('DOMContentLoaded', () => {{
            const adminAccessBtn = document.getElementById('adminAccessBtn');
            const pathParts = window.location.pathname.split('/');
            let currentLoggedInUsername = '';
            
            for (let i = 0; i < pathParts.length; i++) {{
                if (pathParts[i] === 'user' && i + 1 < pathParts.length) {{
                    currentLoggedInUsername = pathParts[i + 1];
                    if (currentLoggedInUsername.endsWith('_index.html')) {{
                        currentLoggedInUsername = currentLoggedInUsername.replace('_index.html', '');
                    }}
                    break;
                }}
            }}

            if (currentLoggedInUsername === 'Melly') {{
                adminAccessBtn.style.display = 'inline-block'; // Mostra o botão
            }} else {{
                adminAccessBtn.style.display = 'none'; // Garante que esteja escondido para outros usuários
            }}
        }});
        </script>
        """
        # Encontra o final da tag </body> e injeta o novo script antes dela
        body_end_index = html_content.rfind("</body>")
        if body_end_index != -1:
            html_content = html_content[:body_end_index] + new_script_content + html_content[body_end_index:]
        else:
            # Fallback caso </body> não seja encontrado (improvável)
            html_content += new_script_content

    # Criar pasta do usuário se não existir
    user_folder = ensure_user_directory_exists(username)
    
    # Criar arquivo HTML na pasta do usuário
    filename = f'{username}_index.html'
    filepath = os.path.join(user_folder, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)

        # Copia o arquivo calendario.html original para a pasta do usuário e modifica
        original_calendario_path = os.path.join(app.template_folder, 'calendario.html')
        user_calendario_path = os.path.join(user_folder, 'calendario.html')

        if os.path.exists(original_calendario_path):
            with open(original_calendario_path, 'r', encoding='utf-8') as f:
                calendar_content = f.read()

            # Modifica o botão "Voltar" para apontar para o index do usuário gerado
            calendar_content = calendar_content.replace(
                "onclick=\"window.location.href='index.html'\"",
                f"onclick=\"window.location.href='{username}_index.html'\""
            )
            
            with open(user_calendario_path, 'w', encoding='utf-8') as f:
                f.write(calendar_content)
            logger.info(f"Copiado e modificado calendario.html para {user_folder}")
        else:
            logger.warning(f"calendario.html não encontrado em {original_calendario_path}. Criando uma versão básica para {username}.")
            # Cria um calendario.html básico se o original não for encontrado
            calendar_html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head><meta charset="UTF-8"><title>Calendário de {username}</title></head>
<body style="background:#111;color:#fff;text-align:center;padding:50px;">
    <h1>Calendário Pessoal de {username}</h1>
    <p>Este é o calendário de {username}. Conteúdo personalizado pode ser adicionado aqui.</p>
    <a href="{username}_index.html" style="color:#8B008B;">⬅ Voltar ao painel</a>
</body>
</html>
"""
            calendar_path = os.path.join(user_folder, 'calendario.html')
            with open(calendar_path, 'w', encoding='utf-8') as f:
                f.write(calendar_html)


        logger.info(f"Página HTML criada para o usuário: {username} em {filepath}")
        return True
    except Exception as e:
        logger.error(f"Erro ao criar página HTML para {username}: {str(e)}")
        return False

def save_user_to_db(username, password, email=None):
    """Salva o usuário no banco de dados e cria a página personalizada"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # Hash da senha para segurança
        password_hash = hash_password(password)

        # Inserir usuário no banco
        cursor.execute('''
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
        ''', (username, password_hash, email))

        conn.commit()
        conn.close()

        # Criar a página HTML personalizada do usuário
        html_created = create_user_html(username, email)
        
        if html_created:
            logger.info(f"Usuário {username} criado com sucesso com pasta própria")
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
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row # Retorna linhas como objetos que podem ser acessados por nome
        cursor = conn.cursor()
        
        # Buscar usuário pelo username
        cursor.execute('SELECT password_hash, email FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        
        conn.close()
        
        if result is None:
            logger.warning(f"Tentativa de login com usuário inexistente: {username}")
            return False, "Usuário não encontrado", None
        
        stored_hash = result['password_hash']
        user_email = result['email']
        
        # Verificar se a senha está correta
        if verify_password(password, stored_hash):
            logger.info(f"Login bem-sucedido para o usuário: {username}")
            return True, "Login realizado com sucesso!", user_email
        else:
            logger.warning(f"Tentativa de login com senha incorreta para: {username}")
            return False, "Senha incorreta", None
            
    except Exception as e:
        logger.error(f"Erro no login do usuário {username}: {str(e)}")
        return False, f"Erro ao autenticar usuário: {str(e)}", None

@app.route('/')
def index():
    """Redireciona para a página de login"""
    return redirect(url_for('auth_page'))

@app.route('/auth.html')
def auth_page():
    """Serve a página de login"""
    try:
        return send_from_directory(app.template_folder, 'auth.html')
    except FileNotFoundError:
        logger.error(f"Página auth.html não encontrada em: {app.template_folder}")
        return jsonify({'error': 'Página de login não encontrada'}), 404

@app.route('/cadastro.html')
def cadastro_page():
    """Serve a página de cadastro"""
    try:
        return send_from_directory(app.template_folder, 'cadastro.html')
    except FileNotFoundError:
        logger.error(f"Página cadastro.html não encontrada em: {app.template_folder}")
        return jsonify({'error': 'Página de cadastro não encontrada'}), 404

@app.route('/Melly_index.html')
def melly_index_page():
    """Serve a página Melly_index.html (template original) diretamente."""
    try:
        return send_from_directory(app.template_folder, 'Melly_index.html')
    except FileNotFoundError:
        logger.error(f"Página Melly_index.html não encontrada em: {app.template_folder}")
        return jsonify({'error': 'Página Melly_index.html não encontrada'}), 404

# Nova rota para servir o painel administrativo
@app.route('/admin_panel.html')
def admin_panel_page():
    """Serve a página do painel administrativo."""
    try:
        return send_from_directory(app.template_folder, 'admin_panel.html')
    except FileNotFoundError:
        logger.error(f"Página admin_panel.html não encontrada em: {app.template_folder}")
        return jsonify({'error': 'Página administrativa não encontrada'}), 404


@app.route('/user/<username>')
def user_dashboard(username):
    """Serve a página personalizada do usuário da sua pasta específica"""
    # Validação do nome de usuário mais robusta
    if not username or not username.replace('_', '').replace('-', '').isalnum():
        logger.warning(f"Tentativa de acesso com nome de usuário inválido: {username}")
        return jsonify({'error': 'Nome de usuário inválido'}), 400
    
    user_folder = os.path.join(USER_DIR_PATH, username)
    filename = f'{username}_index.html'
    filepath = os.path.join(user_folder, filename)
    
    # Se a requisição é para /user/Melly (sem o .html), redireciona para /user/Melly/Melly_index.html
    if not request.path.endswith('.html') and os.path.exists(filepath):
        return redirect(url_for('serve_user_file', username=username, filename=filename))

    if os.path.exists(filepath):
        try:
            return send_from_directory(user_folder, filename)
        except Exception as e:
            logger.error(f"Erro ao servir página do usuário {username} de {user_folder}: {str(e)}")
            return jsonify({'error': 'Erro ao carregar página do usuário'}), 500
    else:
        logger.warning(f"Página '{filename}' não encontrada para usuário: {username}. Tentando recriar...")
        # Se a página não existe, verifica se o usuário existe no DB e tenta recriar
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        user_data_in_db = conn.execute('SELECT email FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()

        if user_data_in_db:
            user_email = user_data_in_db['email']
            success = create_user_html(username, user_email)
            if success and os.path.exists(filepath):
                logger.info(f"Página recriada com sucesso para {username}. Tentando servir novamente.")
                return send_from_directory(user_folder, filename)
            else:
                logger.error(f"Falha ao recriar a página para {username} ou arquivo ainda ausente.")
        
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
                <p>Pasta esperada: {USER_DIR_PATH}/{username}/{username}_index.html</p>
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
        success, message, user_email = authenticate_user(username, password)
        
        if success:
            # Verificar se a página HTML do usuário existe, se não, criar
            user_folder = os.path.join(USER_DIR_PATH, username)
            filename = f'{username}_index.html'
            filepath = os.path.join(user_folder, filename)
            
            if not os.path.exists(filepath):
                logger.info(f"Criando página HTML para usuário existente: {username}")
                create_user_html(username, user_email)
            
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
        email = data.get('email')
        
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
        success, message = save_user_to_db(username, password, email)
        
        if success:
            return jsonify({
                'success': True,
                'message': message,
                'username': username,
                'user_folder': f'user/{username}/'
            }), 200
        else:
            return jsonify({'error': message, 'success': False}), 400
            
    except Exception as e:
        logger.error(f"Erro no endpoint de cadastro: {str(e)}")
        return jsonify({'error': 'Erro interno do servidor', 'success': False}), 500

@app.route('/list_users', methods=['GET'])
def list_users():
    """Endpoint para listar usuários"""
    conn = None
    try:
        logger.info("Tentando conectar ao banco de dados para listar usuários...")
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        logger.info("Executando query para selecionar usuários...")
        cursor.execute('SELECT username, email, created_at FROM users ORDER BY created_at DESC')
        users = cursor.fetchall()
        logger.info(f"Query executada. Encontrados {len(users)} usuários.")
        
        user_list = []
        for user in users:
            user_list.append(dict(user))
        
        logger.info("Usuários processados com sucesso. Retornando resposta.")
        return jsonify({'success': True, 'users': user_list, 'total': len(user_list)}), 200
        
    except sqlite3.Error as se:
        logger.error(f"Erro de SQLite ao listar usuários: {str(se)}")
        return jsonify({'success': False, 'message': f'Erro no banco de dados: {str(se)}'}), 500
    except Exception as e:
        logger.error(f"Erro geral ao listar usuários: {str(e)}", exc_info=True)
        return jsonify({'success': False, 'message': f'Erro interno ao listar usuários: {str(e)}'}), 500
    finally:
        if conn:
            conn.close()
            logger.info("Conexão com o banco de dados fechada.")

@app.route('/admin/list_users', methods=['GET'])
def admin_list_users():
    """Endpoint para listar usuários sob o prefixo admin (chama a função original)"""
    return list_users()

@app.route('/check_db', methods=['GET'])
def check_database():
    """Endpoint para verificar o status do banco de dados"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users')
        count = cursor.fetchone()[0]
        
        # Verificar se os diretórios existem
        db_exists = os.path.exists(DATABASE_PATH)
        user_dir_exists = os.path.exists(USER_DIR_PATH)
        
        # Listar pastas de usuários
        user_folders = []
        if user_dir_exists:
            user_folders = [f for f in os.listdir(USER_DIR_PATH) if os.path.isdir(os.path.join(USER_DIR_PATH, f))]
        
        conn.close()
        
        return jsonify({
            'message': 'Banco de dados funcionando',
            'total_users': count,
            'database_file': DATABASE_PATH,
            'database_directory': DATABASE_DIR_PATH,
            'user_directory': USER_DIR_PATH,
            'database_exists': db_exists,
            'user_dir_exists': user_dir_exists,
            'user_folders': user_folders,
            'total_user_folders': len(user_folders),
            'database_size': os.path.getsize(DATABASE_PATH) if db_exists else 0
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
        test_email = "admin@example.com"
        
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Verificar se o usuário teste já existe
        cursor.execute('SELECT username FROM users WHERE username = ?', (test_username,))
        if cursor.fetchone() is None:
            # Criar usuário teste
            password_hash = hash_password(test_password)
            cursor.execute('''
                INSERT INTO users (username, password_hash, email)
                VALUES (?, ?, ?)
            ''', (test_username, password_hash, test_email))
            conn.commit()
            
            # Criar página HTML para o usuário teste
            create_user_html(test_username, test_email)
            
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
            'user_page': f'/user/{test_username}',
            'user_folder': f'user/{test_username}/',
            'user_html_file': f'user/{test_username}/{test_username}_index.html'
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

@app.route('/user/<username>/<path:filename>')
def serve_user_file(username, filename):
    """Serve arquivos adicionais da pasta do usuário, como calendario.html"""
    if not username or not username.replace('_', '').replace('-', '').isalnum():
        logger.warning(f"Tentativa de acesso a arquivo de usuário com nome de usuário inválido: {username}")
        return jsonify({'error': 'Nome de usuário inválido'}), 400

    user_folder = os.path.join(USER_DIR_PATH, username)
    full_path = os.path.join(user_folder, filename)

    if not os.path.isfile(full_path):
        logger.warning(f"Arquivo '{filename}' não encontrado para o usuário '{username}' em '{user_folder}'.")
        return jsonify({'error': 'Arquivo não encontrado'}), 404

    logger.info(f"Servindo arquivo '{filename}' para o usuário '{username}' de '{user_folder}'.")
    return send_from_directory(user_folder, filename)

@app.route('/admin/autorizar_modificacao', methods=['POST'])
def autorizar_modificacao():
    """Permite ações administrativas apenas para Melly com senha especial"""
    data = request.get_json()
    username = data.get('username')
    emergency_password = data.get('emergency_password')

    if username == 'Melly' and emergency_password == '335666':
        logger.info(f"Autorização administrativa concedida para '{username}'.")
        return jsonify({'success': True, 'message': 'Autorizado!'}), 200
    else:
        logger.warning(f"Tentativa de autorização administrativa falhou para '{username}'.")
        return jsonify({'success': False, 'message': 'Acesso negado'}), 403

@app.route('/admin/delete_user', methods=['DELETE'])
def admin_delete_user():
    data = request.get_json()
    username_to_delete = data.get('username_to_delete') 

    if not username_to_delete:
        return jsonify({'success': False, 'message': 'Nome de usuário para deletar é obrigatório'}), 400

    if username_to_delete == 'Melly':
        logger.warning(f"Tentativa de deletar usuário Melly negada via API.")
        return jsonify({'success': False, 'message': 'Não é permitido apagar o usuário Melly via esta interface.'}), 403

    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        # 1. Apagar a pasta do usuário
        user_folder = os.path.join(USER_DIR_PATH, username_to_delete)
        if os.path.exists(user_folder):
            shutil.rmtree(user_folder)
            logger.info(f"Pasta do usuário '{username_to_delete}' em '{user_folder}' deletada com sucesso.")
        else:
            logger.warning(f"Pasta do usuário '{username_to_delete}' não encontrada para exclusão (pode já ter sido apagada ou nunca existiu).")

        # 2. Apagar o usuário do banco de dados
        cursor.execute("DELETE FROM users WHERE username = ?", (username_to_delete,))
        if cursor.rowcount > 0:
            conn.commit()
            logger.info(f"Usuário '{username_to_delete}' deletado com sucesso do banco de dados.")
            return jsonify({'success': True, 'message': f'Usuário {username_to_delete} e seus dados foram deletados com sucesso!'}), 200
        else:
            logger.warning(f"Tentativa de deletar usuário inexistente no DB: '{username_to_delete}'.")
            return jsonify({'success': False, 'message': 'Usuário não encontrado no banco de dados.'}), 404
    except Exception as e:
        logger.error(f"Erro ao deletar usuário '{username_to_delete}': {e}")
        return jsonify({'success': False, 'message': f'Erro interno ao deletar usuário: {e}'}), 500
    finally:
        conn.close()

if __name__ == '__main__':
    # Inicializar o banco de dados
    if not init_database():
        print("ERRO: Não foi possível inicializar o banco de dados!")
        exit(1)
    
    print("=== Sistema de Login com Flask ===")
    print(f"Banco de dados: {DATABASE_PATH}")
    print(f"Pasta de usuários: {USER_DIR_PATH}")
    print("Servidor iniciando...")
    print("Páginas disponíveis:")
    print("  - Login: http://localhost:5000/auth.html")
    print("  - Cadastro: http://localhost:5000/cadastro.html")
    print("  - Teste: http://localhost:5000/test_login")
    print("  - Status DB: http://localhost:5000/check_db")
    print("  - Listar usuários (API): http://localhost:5000/list_users")
    print("  - Painel Administrativo: http://localhost:5000/admin_panel.html") # Nova linha
    print("Para parar o servidor: Ctrl+C")
    
    # Executar a aplicação Flask
    app.run(debug=True, host='0.0.0.0', port=5000)
