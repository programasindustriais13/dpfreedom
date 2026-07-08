# 🧠 SPEC — Dashboard de Atestados Médicos do RH (Privacidade por Design)

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas**: 
  - `/` (Página de login)
  - `/dashboard/` (Página principal: upload da planilha e visualização do dashboard)
  - `/logout/` (Desconexão segura)
  - `/acesso-negado/` (Página amigável de erro 403)
- **Contexto**: Gestão de RH, Segurança da Informação, Privacidade de Dados de Saúde.
- **Perfil(s) afetados**: Usuários com permissão operacional explícita de `RH` (grupo `RH` ou permissão `dashboard.view_rh_dashboard`).

---

## ❗ 2. PROBLEMA ATUAL

Atualmente, não existe um sistema centralizado para analisar os atestados médicos apresentados pelos colaboradores. O RH precisa de uma ferramenta rápida e profissional para consolidar e visualizar esses dados graficamente. No entanto, por envolver informações altamente confidenciais e de saúde (CIDs e nomes), a persistência permanente desses dados representa um alto risco de privacidade sob a LGPD.

---

## 🎯 3. OBJETIVO

Desenvolver um sistema Django que permita ao RH:
1. Efetuar login com credenciais seguras.
2. Fazer upload de uma planilha de atestados (`.xlsx`).
3. Processar os dados inteiramente em memória e gerar instantaneamente um dashboard com indicadores e gráficos interativos locais.
4. Garantir que nenhuma informação da planilha seja persistida em banco de dados, sessão, arquivos em disco ou transmitida a terceiros.
5. Limitar rigorosamente o acesso operacional, impedindo que administradores comuns (`is_superuser`, `is_staff`) acessem os dados sem a permissão explícita de RH.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Novo Projeto Django e Estrutura:
- `rh_dashboard/` (Configurações do projeto)
- `dashboard/` (App principal)
  - `views.py` (Visualizações de login, dashboard e erro)
  - `forms.py` (Formulário de upload e opções de processamento)
  - `utils/excel_parser.py` (Serviço de validação e leitura do Excel em memória)
  - `templates/` (Templates HTML estruturados e limpos)
  - `static/` (Arquivos locais do CSS customizado e biblioteca Chart.js)
- `requirements.txt` (Instalação de dependências mínimas: Django, openpyxl)
- `.gitignore` (Configurações Git seguras)
- `.env.example` (Modelo de configuração de ambiente)

---

## 🚫 5. FORA DE ESCOPO

- **Modelos de dados para atestados**: Proibido criar tabelas para atestados ou linhas do Excel.
- **Upload persistente**: Proibido salvar arquivos no diretório `media/` ou usar `FileField`.
- **Bibliotecas externas ou CDNs**: Não usar CDNs para carregar scripts (ex: Tailwind, Bootstrap ou Chart.js via CDN). Todos os arquivos de dependência de frontend devem ser mantidos localmente no projeto.
- **Integrações de terceiros ou APIs externas**: Processamento 100% local.

---

## 📐 6. ARQUITETURA ATUAL AFETADA

Como não há um projeto Django existente, o projeto será inicializado do zero na pasta raiz, respeitando estritamente o limite de atuação da pasta do projeto. O app `dashboard` centralizará a lógica de visualizações, autenticação e processamento em memória.

---

## 🔐 7. PRIVACIDADE E SEGURANÇA

⚠️ **Regras Máximas de Privacidade**:
- **Processamento em Memória**: O arquivo carregado será recebido como `InMemoryUploadedFile` e lido usando `openpyxl` através de um buffer em memória (`BytesIO`), sendo descartado imediatamente após a renderização da página.
- **Controle de Cache**: A view do dashboard retornará obrigatoriamente o cabeçalho `Cache-Control: no-store, no-cache, must-revalidate, max-age=0, private` para impedir que os navegadores armazenem os dados processados.
- **Segurança de Logs**: Em caso de erro de processamento, os logs do sistema nunca devem conter dados pessoais, nomes de colaboradores, CIDs ou linhas completas da planilha.
- **Ocultação de CID**: Na tabela de resumo do dashboard, os CIDs individuais por colaborador não serão exibidos. O CID será exibido unicamente no gráfico de distribuição agregada.
- **Desconexão Rápida**: Botão de logout proeminente que limpa a sessão Django e redireciona ao login.

---

## 👥 8. PERFIS E PERMISSÕES

- **Permissão Customizada**: `dashboard.view_rh_dashboard` (ou pertencer ao grupo `RH`).
- **Lógica de Bloqueio**:
  - Usuários não autenticados -> Redirecionar para `/login/`.
  - Usuários autenticados mas sem a permissão `view_rh_dashboard` (mesmo se `is_superuser` ou `is_staff` for True) -> Impedir acesso e exibir página amigável de Acesso Negado (HTTP 403).
- **Django Admin**: Apenas para administração de contas, grupos e permissões. Não registrar nenhum modelo relacionado a atestados.

---

## 📄 9. CONTRATO DOS ARQUIVOS DE ENTRADA

A planilha deve ser um arquivo no formato `.xlsx`. Os cabeçalhos de coluna válidos serão identificados (ignorando maiúsculas/minúsculas, acentuação leve, quebras de linha e espaços excedentes) correspondendo a:
1. **Nome do Colaborador**: Ex: `Nome do colaborador`, `nome do colaborador \n`, `Nome`
2. **Função do Colaborador**: Ex: `Função do colaborador`, `Funcao do colaborador`, `Função`
3. **Data Inicial do Atestado**: Ex: `Data inicial do atestado`, `Data inicial`
4. **CID**: Ex: `CID`
5. **Quantidade de dias/ HORAS**: Ex: `Quantidade de dias/ HORAS`, `dias/horas`, `quantidade de dias/ horas `

---

## 🧼 10. REGRAS DE VALIDAÇÃO

- **Tamanho do Arquivo**: Limite de 5 MB.
- **Linhas**: Limite de 1000 linhas de dados.
- **Extensão**: Apenas arquivos terminando em `.xlsx`.
- **Aba do Arquivo**: Se houver múltiplas abas, ler a primeira que possuir todas as colunas obrigatórias. Se nenhuma possuir, rejeitar o arquivo.
- **Linhas Vazias**: Ignorar linhas onde todas as colunas estejam vazias.
- **Consistência de Datas**: A data deve ser um objeto `datetime` válido do Excel ou texto convertível no formato `DD/MM/AAAA` ou `AAAA-MM-DD`. Datas inválidas tornam a linha inválida (registrada no resumo de inconsistências).
- **Detecção de Duplicados**: Linhas com mesmos valores exatos para (Nome, Função, Data Inicial, CID, Quantidade/Unidade) serão contadas como "possíveis duplicidades" e listadas em um painel informativo, mas não removidas.

---

## ⚙️ 11. REGRAS DE NEGÓCIO

- **Tratamento de Quantidades (Dias vs Horas)**:
  - Formatos detectados:
    - `X dias`, `X dia`, `X d` -> Interpretado como X dias.
    - `Y horas`, `Y hora`, `Y h`, `Y:00` -> Interpretado como Y horas.
    - Numérico puro (ex: `3` ou `8`): Comportamento ditado pelo formulário:
      - `reject` (Padrão): Linha inválida (rejeitar valores sem unidade).
      - `days`: Interpretado como dias.
      - `hours`: Interpretado como horas.
  - Dias e horas são acumulados e exibidos separadamente no dashboard. **Nunca somar dias com horas.**
- **Colaborador e Função**: Nomes terão espaços extras removidos. Se a função estiver em branco, classificar como `"Não informada"`.
- **Contagem**: Cada linha válida é igual a 1 atestado.

---

## 📊 12. REQUISITOS DE INTERFACE E VISUALIZAÇÃO

Design Premium: Dark mode elegante (fundo `#0f172a`, cards `#1e293b`, bordas sutis, fontes limpas como Outfit ou Inter).
- **Cards de Indicadores**:
  1. Total de atestados válidos
  2. Colaboradores únicos afetados
  3. Total de dias acumulados
  4. Total de horas acumuladas
  5. Contagem de linhas inválidas (inconsistências)
  6. Quantidade de duplicidades suspeitas
  7. Período geral (Data inicial mais antiga até a data inicial mais recente)
- **Gráficos (Chart.js local)**:
  1. *Barras Horizontais*: Quantidade de atestados por colaborador (ordenado).
  2. *Linhas/Colunas*: Evolução temporal (atestados por mês em ordem cronológica).
  3. *Colunas/Barras*: Atestados por função.
  4. *Barras Horizontais*: Dias de afastamento por colaborador.
  5. *Barras Horizontais*: Horas de afastamento por colaborador.
  6. *Pizza/Rosca*: Distribuição de atestados por CID (agregado, mostrando top N e agrupando o restante em "Outros").
- **Tabela de Resumo**: Colaborador, Qtd Atestados, Total Dias, Total Horas, Data Mínima, Data Máxima. Com busca e ordenação em JavaScript no frontend.
- **Filtros locais**: Filtro por período, colaborador, função e CID. As alterações devem refletir instantaneamente nos gráficos, tabela e cards usando JavaScript.

---

## ❌ 13. TRATAMENTO DE ERROS

- Erro de permissão: Página amigável alertando a necessidade do perfil RH.
- Erro de formato de Excel/Arquivo corrompido: Exibe mensagem clara no formulário de upload sem revelar stack traces ou caminhos de arquivos.

---

## 🧪 14. CRITÉRIOS DE ACEITAÇÃO

- [x] O usuário faz login, anexa planilha, e vê os gráficos imediatamente.
- [x] Ao recarregar a página, os dados expiram e o formulário de upload é reexibido.
- [x] Nenhuma tabela de atestado no banco SQLite.
- [x] A pasta `media/` não é criada/usada para armazenar planilhas.
- [x] Usuários comuns ou administradores sem o perfil RH são bloqueados.
- [x] Dias e horas são exibidos e processados em separado.

---

## ⚠️ 15. RISCOS

- **Vazamento de dados por logs**: Mitigado garantindo que blocos de `try-except` registrem apenas o tipo da exceção e uma mensagem genérica sem dados pessoais.
- **Bypass de visualização**: Mitigado validando a permissão do usuário em nível de view via decorator customizado (`@user_passes_test` ou similar no backend).

---

## 📦 16. DEPENDÊNCIAS

- `django>=4.2,<5.0`
- `openpyxl>=3.1.0,<3.2.0`
- `python-dotenv>=1.0.0`

---

## 🔍 17. PLANO DE IMPLEMENTAÇÃO

1. **Setup**: Criar `.gitignore`, `requirements.txt` e iniciar projeto Django com `manage.py` na raiz.
2. **Autenticação e Perfis**: Views de login, logout e view customizada para desvio 403. Criar permissão/grupo RH.
3. **Parser do Excel**: Criar módulo utilitário em `dashboard/utils/excel_parser.py` para receber o arquivo do formulário, processar em memória e retornar um dicionário JSON pronto para os gráficos.
4. **Dashboard View**: Criar view protegida que recebe o POST, chama o parser, e injeta os dados estruturados no template.
5. **Interface e Chart.js**: Criar templates e baixar/incluir a biblioteca `chart.js` localmente nos estáticos do app. Implementar o frontend e filtros dinâmicos em Vanilla JS.
6. **Testes e Validações**: Escrever testes automatizados robustos cobrindo todas as especificidades.

---

## 🧪 18. TESTES AUTOMATIZADOS

- Testar controle de acesso (RH vs Usuário comum vs Superuser sem perfil).
- Testar upload de arquivos corrompidos, extensões incorretas, planilha vazia ou com colunas erradas.
- Testar cálculo correto de dias e horas, linhas inválidas e detecção de duplicidades.
- Testar se os dados não são persistidos.

---

## 🧪 19. TESTES MANUAIS

- Seguir estritamente o roteiro contido nas `INSTRUCOES_EXECUCAO.txt`.

---

## 📂 20. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

A serem geradas e listadas no relatório final e no walkthrough.
