# 🧠 SPEC — [NOME DA FEATURE OU CORREÇÃO]

---

## 📌 1. CONTEXTO

Descreva rapidamente onde isso acontece no sistema:

- URL(s) envolvidas:
- Contexto(s): (RH, Autenticação, Relatórios, etc.)
- Perfil(s) afetados: (Usuário RH, Gestor, Administrador)

---

## ❗ 2. PROBLEMA ATUAL

Descreva claramente o problema:

- O que está acontecendo hoje?
- O que está incorreto ou incompleto?
- Existe impacto em produção ou na privacidade dos dados?

---

## 🎯 3. OBJETIVO

Descreva o resultado esperado de forma direta:

- O que deve passar a acontecer?
- Qual comportamento novo deve existir?
- Como a privacidade deve ser garantida no processo?

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

Liste o que PODE ser alterado:

### Possíveis arquivos:
- models.py
- views.py
- forms.py
- templates
- utils/services
- URLs

### Possíveis módulos/apps:
- core
- authentication
- dashboard

---

## 🚫 5. FORA DE ESCOPO

O que NÃO pode ser alterado:

- Não alterar outras funcionalidades não relacionadas
- Não refatorar o sistema inteiro
- Não criar novos apps sem necessidade
- Não salvar ou persistir dados sensíveis de RH sem autorização
- Não utilizar conexões ou CDNs externas para processar dados sensíveis

---

## 📐 6. ARQUITETURA ATUAL AFETADA

Descreva quais partes da arquitetura atual serão alteradas ou criadas:

- Estrutura de URLs afetadas
- Apps afetados
- Componentes de UI afetados

---

## 🔐 7. PRIVACIDADE E SEGURANÇA

⚠️ Esta implementação DEVE seguir princípios rigorosos de segurança e privacidade por padrão:

- **Dados Temporários**: Não persistir no banco ou na sessão dados pessoais/sensíveis dos colaboradores.
- **Processamento em Memória**: Arquivos e dados devem ser processados em memória (`BytesIO` ou similar).
- **Sem Logs Sensíveis**: Não registrar informações sensíveis (nomes, CIDs, dados de saúde) em logs ou stack traces.
- **Cache-Control**: Configurar cabeçalhos de resposta HTTP para impedir cache (`Cache-Control: no-store, private`).

---

## 👥 8. PERFIS E PERMISSÕES

Descreva os perfis que podem acessar a funcionalidade:

- **Perfis Permitidos**: (ex: Grupo ou Permissão `RH` / `RH_ANALISTA`)
- **Bloqueios Obrigatórios**: Usuários não autenticados, autenticados sem permissão específica, is_staff ou is_superuser sem a permissão operacional correspondente.
- **Comportamento Backend**: Validação rigorosa no backend com desvio amigável para página de erro 403.

---

## 📄 9. CONTRATO DOS ARQUIVOS DE ENTRADA

Descreva a estrutura esperada do arquivo de entrada (ex: Planilha Excel):

- Colunas obrigatórias
- Tipos de dados permitidos
- Unidades de medida (ex: dias/horas)
- Regras de tratamento de cabeçalhos (normalização de espaços, maiúsculas, etc.)

---

## 🧼 10. REGRAS DE VALIDAÇÃO

Descreva as validações que devem ser executadas no arquivo:

- Limites de tamanho do arquivo e número de linhas.
- Extensões aceitas (apenas `.xlsx`).
- Detecção de inconsistências (linhas incompletas, datas inválidas).
- Tratamento de duplicidades sem exclusão silenciosa.

---

## ⚙️ 11. REGRAS DE NEGÓCIO

Descrever regras específicas da feature:

- Como os dados devem ser agregados.
- Tratamento de unidades não informadas (dias ou horas).
- Regras para contagem de atestados por colaborador.
- Agrupamentos por CID e tratamento de CIDs ausentes.

---

## 📊 12. REQUISITOS DE INTERFACE E VISUALIZAÇÃO

Descreva os requisitos visuais do dashboard:

- Biblioteca de gráficos local (sem CDNs ou telemetria).
- Tipos de gráficos (barras horizontais, linha, etc.).
- Cards com indicadores obrigatórios.
- Filtros interativos aplicados no frontend (em memória).
- Tabela resumida com paginação e busca, ocultando dados sensíveis.

---

## ❌ 13. TRATAMENTO DE ERROS

Como o sistema deve se comportar perante falhas:

- Arquivo corrompido ou formato incorreto.
- Sem exibição de stack trace para o usuário final.
- Mensagens de erro claras e orientativas.

---

## 🧪 14. CRITÉRIOS DE ACEITAÇÃO

A tarefa só é considerada concluída se:

- [ ] Funcionalidade funciona conforme esperado em memória.
- [ ] Nenhum dado sensível do Excel foi persistido no banco ou disco.
- [ ] Permissões de RH validadas rigidamente no backend.
- [ ] Interface compreensível, sem telemetria ou CDNs externas.
- [ ] Passa em todos os testes automatizados com dados fictícios.

---

## ⚠️ 15. RISCOS

Identifique possíveis riscos:

- Exposição acidental de dados em logs do servidor.
- Consumo de memória elevado para arquivos muito grandes.
- Bypass de segurança por administradores.

---

## 📦 16. DEPENDÊNCIAS

Bibliotecas Python necessárias e sua justificativa de uso:

- ex: `openpyxl` para leitura do Excel.

---

## 🔍 17. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

⚠️ Deve ser definido ANTES de codar

### Passos:

1. Setup do Projeto e Autenticação
2. Implementação do serviço de processamento e validação em memória
3. Criação das views e rotas com proteção de privilégio mínimo
4. Desenvolvimento do frontend (dashboard com biblioteca de gráficos local)
5. Criação de testes unitários e de integração

---

## 🧪 18. TESTES AUTOMATIZADOS

Descreva a estratégia de testes que deve ser codificada:

- Testes de autenticação e permissões (RH vs Outros).
- Testes de importação do arquivo Excel (válidos, inválidos, limites).
- Testes de privacidade (validar que nada é salvo).
- Dados fictícios sempre.

---

## 🧪 19. TESTES MANUAIS

Roteiro passo a passo para validação humana:

1. Acessar como Usuário sem RH
2. Acessar como Usuário com RH
3. Fazer upload de arquivo correto
4. Validar os gráficos e indicadores
5. Atualizar a página e validar que os dados sumiram

---

## 📂 20. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

O agente DEVE informar:

### Arquivos lidos:
- lista de arquivos analisados

### Arquivos criados/alterados:
- lista objetiva e sua finalidade

### Alterações feitas:
- o que mudou em cada arquivo

---

## 🔄 21. ESTRATÉGIA DE REVERSÃO

Como reverter as alterações caso ocorra um problema crítico:

- Desfazer commits ou apagar arquivos criados.

---

## 📝 22. DOCUMENTAÇÃO NECESSÁRIA

Documentos que devem ser gerados ao final:

- `INSTRUCOES_EXECUCAO.txt`

---

## 🤖 23. ORDEM DOS SUBAGENTES

### 1. Arquiteto
- Definição do plano, especificação e aprovação de privacidade.

### 2. Backend
- Implementação das rotas, views, serviços e testes.

### 3. QA
- Auditoria de segurança, privacidade e validação de testes.

---

## 🚨 24. REGRA DE PARADA

Pare imediatamente e corrija o plano se:
- Detectar gravação de dados pessoais.
- Detectar comandos Git executados.
- Detectar arquivos criados fora do projeto raiz.

---

## 🧠 25. PRINCÍPIO FINAL

> "Privacidade por design: dados temporários são processados e esquecidos."
