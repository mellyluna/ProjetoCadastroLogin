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
Ver1.2
- Organização: Cada usuário tem sua própria pasta exclusiva
- Escalabilidade: Fácil adicionar mais arquivos por usuário no futuro
- Segurança: Isolamento físico dos arquivos de cada usuário
- Flexibilidade: Possibilidade de adicionar uploads e outros recursos por usuário

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
