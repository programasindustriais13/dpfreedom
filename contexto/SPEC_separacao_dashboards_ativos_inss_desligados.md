# 🧠 SPEC — Separação de Dashboards de Colaboradores Ativos, INSS e Desligados

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas**: `/dashboard/`
- **Contexto(s)**: Gestão de Departamento Pessoal, Saúde Ocupacional, Privacidade de Dados.
- **Perfil(s) afetados**: Usuários com permissão operacional de Departamento Pessoal (grupo "Departamento Pessoal" ou permissão `dashboard.view_rh_dashboard`).

---

## ❗ 2. PROBLEMA ATUAL

1. O sistema atual processa todos os colaboradores e atestados juntos em um único dashboard principal.
2. A planilha agora possui uma nova coluna `Ativo/Desligado` que define a situação cadastral do colaborador.
3. Não há separação visual nem lógica entre colaboradores Ativos, afastados pelo INSS e Desligados, o que mistura atestados de períodos distintos e de diferentes status contratuais.
4. O Dashboard de Ativos ainda possui filtros de INSS e gráficos que mostram 100% de uma resposta quando ela é constante por categoria (ex: INSS Sim/Não), o que não agrega valor de informação.

---

## 🎯 3. OBJETIVO

1. Implementar a separação lógica e visual completa dos colaboradores nos três dashboards: **Ativos**, **Afastados pelo INSS** e **Desligados**.
2. Garantir que cada colaborador pertença a apenas uma categoria nas visualizações usando classificação consolidada por colaborador (e não por linha individualmente).
3. Adicionar suporte robusto e flexível para a nova coluna `Ativo/Desligado`.
4. Criar navegação dinâmica e responsiva no frontend sem persistência de dados (mantendo o processamento puramente em memória).
5. Exibir um "Resumo de Qualidade de Dados" detalhado para reportar inconsistências e conflitos (como colaboradores marcados como ativos e desligados simultaneamente).
6. Preservar o design, tipo de gráficos, cálculos aprovados e o Card Inteligente.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Arquivos a serem modificados:
- [MODIFY] [excel_parser.py](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/utils/excel_parser.py):
  - Detectar a coluna `Ativo/Desligado` (com tolerância a maiúsculas, espaços e variações).
  - Normalizar os valores da situação.
  - Classificar cada colaborador em uma categoria exclusiva (ATIVO, INSS, DESLIGADO, ou NÃO CLASSIFICADO) seguindo regras de precedência.
  - Detectar e detalhar conflitos de linhas de uma mesma pessoa.
  - Integrar dados de classificação e métricas de qualidade adicionais no retorno do parser.
- [MODIFY] [dashboard.html](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/templates/dashboard.html):
  - Criar componente de navegação responsivo (Ativos, INSS, Desligados) com contadores.
  - Implementar estado isolado por categoria no Javascript para garantir filtros independentes.
  - Ocultar filtros/gráficos redundantes de INSS para as categorias constantes (Ativos e INSS).
  - Exibir aviso de ausência da coluna `Ativo/Desligado`.
  - Ampliar a seção de qualidade dos dados para exibir os novos contadores e inconsistências.
- [MODIFY] [tests.py](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/tests.py):
  - Escrever testes unitários e de integração validando cabeçalhos, normalização, exclusividade, agrupamento, conflitos, INSS, independência dos cartões/gráficos/tabelas e compatibilidade.
- [MODIFY] [INSTRUCOES_EXECUCAO.txt](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/INSTRUCOES_EXECUCAO.txt):
  - Documentar a nova coluna, regras de classificação, navegação e testes.

---

## 🚫 5. FORA DE ESCOPO

- Persistir dados de planilhas no banco de dados (SQLite), sessão (`session`), cookies ou armazenamento local do navegador (`localStorage`, `IndexedDB`).
- Enviar dados para APIs ou serviços externos.
- Criar novos modelos de banco de dados ou criar novas requisições HTTP para navegar entre dashboards.
- Alterar as configurações globais do sistema ou usar comandos Git.

---

## 📐 6. ARQUITETURA ATUAL AFETADA

- **Camada do Parser**: O retorno do parser `parse_excel_in_memory` incluirá informações de classificação por colaborador, chaves de qualidade estendidas e sinalizador de disponibilidade da coluna `Ativo/Desligado`.
- **Interface e Estado do Frontend**: O template `dashboard.html` utilizará um objeto de estado JavaScript para cada uma das três categorias (`ATIVO`, `INSS`, `DESLIGADO`), atualizando os cards, gráficos, Card Inteligente e tabela dinamicamente conforme a categoria ativa selecionada na navegação, sem realizar novas requisições ou recarregar a página.

---

## 🔐 7. PRIVACIDADE E SEGURANÇA

- **Dados em Memória**: Todos os dados do arquivo importado e as categorizações são temporários, vivendo apenas na memória do servidor e no estado JS enquanto a aba do navegador estiver aberta.
- **Cache-Control**: A resposta HTTP continuará retornando cabeçalhos `Cache-Control: no-store, private`.
- **Logs Limpos**: Nenhuma informação que exponha nomes de colaboradores, CIDs ou dados de saúde será escrita nos logs do servidor.

---

## 👥 8. PERFIS E PERMISSÕES

- O acesso é mantido estrito a usuários autenticados pertencentes ao grupo "Departamento Pessoal" ou "RH", ou com a permissão operacional correspondente.
- Superusuários sem grupo continuam sem acesso por padrão.

---

## 📄 9. CONTRATO DOS ARQUIVOS DE ENTRADA

A planilha Excel (.xlsx) pode possuir até sete colunas:
1. `Nome do colaborador` (Obrigatória)
2. `Função do colaborador` (Opcional)
3. `Data inicial do atestado` (Obrigatória)
4. `CID` (Opcional)
5. `Quantidade de dias/ HORAS` (Obrigatória)
6. `Houve Afastamento Pelo INSS?` (Opcional)
7. `Ativo/Desligado` (Opcional - coluna nova)

---

## 🧼 10. REGRAS DE VALIDAÇÃO

### Reconhecimento da coluna `Ativo/Desligado`
Será identificada pela presença dos termos `"ativo"` e `"desligado"` no nome da coluna após conversão para minúsculas, remoção de acentos, caracteres especiais e espaços extras.

### Normalização dos Valores
- **Como ATIVO**: "ATIVO", "Ativo", "ativo", "ATIVA", "Ativa", "ativa" (e variações com espaços extras).
- **Como DESLIGADO**: "DESLIGADO", "Desligado", "desligado", "DESLIGADA", "Desligada", "desligada" (e variações com espaços extras).
- **Como NÃO INFORMADO**: Células vazias, nulas, somente com espaços ou ausência da coluna.
- **Valores inválidos**: Qualquer outro valor gerará inconsistência cadastral na área de qualidade de dados, sendo tratado internamente como NÃO INFORMADO para não quebrar a planilha inteira, mas o colaborador será colocado na categoria NÃO CLASSIFICADO (ficando fora dos dashboards).

---

## ⚙️ 11. REGRAS DE NEGÓCIO

### Classificação do Colaborador (Exclusividade)
A classificação será efetuada consolidando todas as linhas de atestados associadas ao mesmo colaborador (identificado pelo nome normalizado: minúsculas, espaços extras removidos). O colaborador pertencerá a uma única categoria na seguinte ordem de prioridade:

1. **COLABORADOR DESLIGADO**: Se possuir pelo menos uma linha válida com situação `DESLIGADO` (ou `DESLIGADA`) e nenhuma com `ATIVO`. Caso possua alguma linha marcada como `ATIVO` e outra como `DESLIGADO`, será classificado como **CONFLITANTE** (categoria NÃO CLASSIFICADO).
2. **COLABORADOR AFASTADO PELO INSS**: Se todas as suas linhas de situação válidas forem `ATIVO` (ou `ATIVA`), e pelo menos uma linha contiver afastamento pelo INSS = `SIM`.
3. **COLABORADOR ATIVO**: Se todas as suas linhas de situação válidas forem `ATIVO` (ou `ATIVA`), nenhuma contiver INSS = `SIM`, e existir pelo menos um valor válido `NÃO` na coluna do INSS.
4. **NÃO CLASSIFICADO**: Colaborador que possuir situação inválida, ausente, conflito de status (ATIVO vs DESLIGADO) ou ausência de informações de INSS (ex: colaborador Ativo sem nenhuma indicação de INSS SIM ou NÃO).

### Tratamento de Conflitos
Se houver uma linha como ATIVO e outra como DESLIGADO para o mesmo colaborador:
- A classificação do colaborador será `NÃO CLASSIFICADO`.
- Não será exibido em nenhum dos três dashboards.
- Um aviso de conflito será adicionado na área de diagnóstico/qualidade de dados contendo a contagem de linhas conflitantes.

---

## 📊 12. REQUISITOS DE INTERFACE E VISUALIZAÇÃO

### Navegação entre Dashboards
- Navegação por abas ou botões segmentados com estilo da marca (amarelo `#eac532`).
- A navegação apresentará contadores dinâmicos da quantidade de colaboradores em cada dashboard.
- A navegação funcionará inteiramente em frontend (via Javascript), sem recarregamento.

### Isolamento de Dados e Filtros
- Os dados e filtros aplicados serão estritamente isolados por categoria ativa no estado JavaScript.
- Os indicadores de data (período inicial/final) serão recalculados individualmente com base no subconjunto da categoria ativa.
- **Gráficos e Filtro de INSS**:
  - O filtro interativo de INSS será ocultado em todos os dashboards, pois a separação por situação já atende a essa divisão.
  - O gráfico de distribuição de INSS (Gráfico 5) será ocultado nos dashboards de "Ativos" e "INSS", pois seria redundante.

---

## ❌ 13. TRATAMENTO DE ERROS

### Planilhas Antigas (Compatibilidade)
- Se a coluna `Ativo/Desligado` não for encontrada, a planilha continuará sendo processada normalmente.
- Um aviso destacado será exibido: `A coluna “Ativo/Desligado” não foi encontrada. Os colaboradores não puderam ser separados entre Ativos, INSS e Desligados.`
- Todos os colaboradores serão classificados na categoria `NÃO CLASSIFICADO`. Os dashboards principais serão exibidos como vazios (com as devidas mensagens de estado vazio).

---

## 🧪 14. CRITÉRIOS DE ACEITAÇÃO

- [ ] A coluna `Ativo/Desligado` é reconhecida e normalizada corretamente.
- [ ] A classificação ocorre por colaborador, respeitando a precedência e gerando exclusividade nos dashboards.
- [ ] Conflitos (ATIVO e DESLIGADO na mesma pessoa) geram alertas e desclassificam o colaborador dos dashboards.
- [ ] O visual e cálculos dos gráficos aprovados são preservados.
- [ ] A navegação principal funciona instantaneamente sem recarregamento ou novas requisições.
- [ ] Filtros, períodos, totais e tabelas são completamente independentes por categoria.
- [ ] Arquivos sem a coluna de situação apresentam aviso claro e não classificam colaboradores nos dashboards.
- [ ] Todos os testes automatizados passam com sucesso.

---

## ⚠️ 15. RISCOS

- **Volume de Dados**: Processar planilhas gigantes em memória pode consumir RAM do servidor. Mitigado pelo limite estrito de 1000 linhas por arquivo.
- **Redesenho do Gráfico**: Alterar a lógica do Chart.js pode introduzir bugs de renderização. Mitigado pelo uso de um único conjunto de canvas onde apenas os dados dos datasets são atualizados via `update()`.

---

## 📦 16. DEPENDÊNCIAS

- Nenhuma dependência extra (usa as já instaladas: `Django`, `openpyxl`).

---

## 🔍 17. PLANO DE IMPLEMENTAÇÃO

1. **Especificação (SPEC)**: Criação desta SPEC e aprovação técnica.
2. **Atualização do Backend**:
   - Atualizar `excel_parser.py` para mapear, extrair e normalizar a nova coluna `Ativo/Desligado`.
   - Executar o agrupamento por colaborador, realizar a classificação prioritária e a checagem de conflitos.
   - Adicionar informações de categoria e métricas de qualidade ao dicionário final retornado para a view.
3. **Desenvolvimento Frontend**:
   - Inserir os componentes de abas/navegação no topo de `dashboard.html`.
   - Implementar o controle de estados e redesenho dinâmico de gráficos, filtros e tabelas no Javascript do template.
   - Tratar estados vazios, avisos de coluna ausente e conflitos de dados.
4. **Testes Automatizados**:
   - Atualizar e expandir a classe de testes em `dashboard/tests.py` cobrindo todos os cenários obrigatórios e compatibilidades.
5. **Revisão e QA**: Executar testes locais e validar critérios.

---

## 🧪 18. TESTES AUTOMATIZADOS

- `test_excel_header_variants`: Valida as variações de escrita e espaços da nova coluna.
- `test_excel_value_normalization`: Valida normalização de Ativo, Desligado e inválidos.
- `test_collaborator_classification_and_exclusivity`: Valida regras de exclusividade e prioridades.
- `test_collaborator_grouping_and_conflits`: Valida agrupamento de linhas e tratamento de conflito ATIVO/DESLIGADO.
- `test_absence_inss_precedence`: Verifica prioridade de Desligado e classificação de INSS vs Ativos.
- `test_compatibility_old_sheets`: Valida processamento seguro de 5 e 6 colunas sem a coluna de status.

---

## 🧪 19. TESTES MANUAIS

1. Fazer upload de planilha com 7 colunas contendo colaboradores ativos, INSS, desligados, inválidos e conflitos.
2. Conferir os contadores de cada aba na navegação.
3. Clicar em cada aba e confirmar a exibição correta dos respectivos atestados, cards, gráficos e tabelas isoladas.
4. Aplicar filtros na aba Ativos e alternar para a aba INSS, garantindo que o filtro de INSS esteja limpo e não contaminado.
5. Upload de arquivo antigo (sem a coluna situação) e validar a exibição do aviso de ausência da coluna.

---

## 📂 20. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

- Arquivos alterados, criados e excluídos com suas justificativas.
- Comandos e logs dos testes executados localmente.

---

## 🔄 21. ESTRATÉGIA DE REVERSÃO

- Desfazer alterações nos arquivos modificados.

---

## 📝 22. DOCUMENTAÇÃO NECESSÁRIA

- Atualização de `INSTRUCOES_EXECUCAO.txt` com as especificações da nova coluna.

---

## 🤖 23. ORDEM DOS SUBAGENTES

1. Arquiteto (Fase de Planejamento e SPEC)
2. Backend (Codificação, validação e testes)
3. QA (Homologação, verificação de logs e aderência às regras)

---

## 🚨 24. REGRA DE PARADA

- Interromper se houver tentativa de persistir dados cadastrais/médicos.
- Interromper se comandos Git forem disparados pelo agente.
- Interromper se arquivos forem gravados fora do projeto raiz.

---

## 🧠 25. PRINCÍPIO FINAL

> "Cada colaborador em seu devido lugar: dados limpos, dashboards isolados."
