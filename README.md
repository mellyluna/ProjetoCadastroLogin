# ProjetoCadastroLogin
*PROJETO*
Criar um app Web utilizando 100% de IA (sem precisar escrever código)
Página de criação e autenticação de login senha
Armazenar usuario e senha em banco de dados( Obs: não armazenar senha em texto puro, somento o hash para validação)
Validar status do servidor da página de login
criar página (index_nome do usuario.html) para cada usuário

*UTILIZAÇÃO*
1 - Iniciar servidor (manualmente)
2 - abrir página através do link (http://localhost:5000/auth.html)
3 - Ctrl + C (Para parar o servidor)

*FALTA*
- Iniciar servidor automaticamente com página (é iniciado manualmente)
- Armazenar as página index_usuario.html em pasta separada do login (semelhantemente ao banco de dados)
- Se possivel, melhorar criptografia das senhas
- Subir para serviço em nuvem
- Atribuir função à opção "Esqueceu sua senhas?"
- Se possível melhorar criptografia
- Finalização automática do servidor após o encerramento do aplicativo

***Hitórico de versões***
- Cada utilizador tem a sua própria base de dados SQLite (calendario.db) dentro de uma subpasta calendario/ na sua pasta pessoal.
- Guardar Compromissos (/api/appointments/save): Permite que os utilizadores guardem novos compromissos (data, hora, título, descrição) no seu calendário pessoal.
- (/api/appointments/get/<username>/<year>/<month>): Permite que os utilizadores recuperem os seus compromissos para um mês e ano específicos.
- Existe uma rota (/admin/autorizar_modificacao) que requer um nome de utilizador (Melly) e uma "palavra-passe de emergência" (335666) para autorizar ações administrativas.
- Um painel administrativo (/admin_panel.html) é servido para gerir utilizadores (listagem e eliminação).
- O aplicativo utiliza um caminho base forçado (BASE_DIR_FORCED) para garantir que os ficheiros e diretórios sejam criados em locais específicos.
- user.db: A base de dados principal que armazena as informações de registo de todos os utilizadores (nomes de utilizador, hashes de palavra-passe, e-mails).

Ver1.2
- Organização: Cada usuário tem sua própria pasta exclusiva
- Escalabilidade: Fácil adicionar mais arquivos por usuário no futuro
- Segurança: Isolamento físico dos arquivos de cada usuário
- Flexibilidade: Possibilidade de adicionar uploads e outros recursos por usuário
- Listagem de Utilizadores (/list_users, /admin/list_users): Permite listar todos os utilizadores registados na base de dados.
- Eliminação de Utilizadores (/admin/delete_user): Uma funcionalidade administrativa para apagar utilizadores e os seus dados associados, incluindo as suas pastas pessoais e bases de dados de calendário. O utilizador 'Admin' está protegido contra eliminação por esta via.
- Uma página HTML personalizada (e.g., [username]_index.html) é criada dentro desta pasta para servir como o painel de controlo do utilizador.
- Ficheiros como calendario.html são copiados e adaptados para a pasta de cada utilizador, permitindo que cada um tenha a sua própria versão e dados.


Ver 1.1
- A apartir de link url (http://localhost:5000/auth.html)
- Verificação automática se o servidor está rodando
- Criar uma rota que sirva dinamicamente páginas (index_<username>.html)
- Atualizar o auth.html para redirecionar o usuário para a página correta
- Criar as páginas HTML personalizadas conforme os usuários forem se registrando.
- Prevenção de caracteres maliciosos
- Rastreamento de tentativas de login inválidas
- Criação de uma função ( showFeedback() ) para exibir mensagens
- Validação de tamanho mínimo de username (3 caracteres)
- Validação de tamanho mínimo de senha (4 caracteres)
- Verificação periódica do servidor (a cada 30 segundos)
- Função de teste de conexão (testConnection())
