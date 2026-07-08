# 🧠 SPEC — Melhorias do Departamento Pessoal: INSS, Tempo de Afastamento e Identidade Visual

---

## 📌 1. CONTEXTO

- **URL(s) envolvidas**:
  - `/` (Página de login)
  - `/dashboard/` (Página principal do painel)
  - `/acesso-negado/` (Página de erro 403)
- **Contexto**: Gestão do Departamento Pessoal, Saúde Ocupacional, Privacidade de Dados.
- **Perfil(s) afetados**: Usuários com permissão operacional de Departamento Pessoal (grupo "Departamento Pessoal" ou permissão `dashboard.view_rh_dashboard`).

---

## ❗ 2. PROBLEMA ATUAL

1. O sistema utiliza a identidade visual e textual antiga de "RH". É necessário alterar a identidade visível para "Departamento Pessoal" mantendo compatibilidade técnica interna.
2. A planilha de atestados passou a contar com uma nova coluna opcional: `Houve Afastamento Pelo INSS?`. O sistema atual não reconhece, normaliza nem gera visualizações para este indicador.
3. Existem dois cards e gráficos separados para "Dias de Afastamento" e "Horas de Afastamento". Isso dificulta a interpretação quando um colaborador possui atestados em ambas as unidades (ex: 2 dias e 4 horas), causando desagregação confusa.
4. O design do sistema precisa ser alinhado com a identidade visual da empresa (cor principal amarelo `#eac532` e logotipo fornecido).

---

## 🎯 3. OBJETIVO

Aprimorar o dashboard de atestados médicos com as seguintes melhorias:
1. Atualizar toda a identidade apresentada ao usuário de "RH" para "Departamento Pessoal".
2. Suportar a coluna opcional do INSS, tratando-a de forma confidencial e aceitando variações de cabeçalho e valores.
3. Substituir os cards de dias/horas por um único **Card Inteligente de Tempo de Afastamento** interativo.
4. Aplicar o novo tema amarelo (`#eac532`) com contraste adequado e integrar o logotipo original de forma responsiva.
5. Garantir compatibilidade com planilhas antigas de 5 colunas.
6. Preservar integralmente as regras rígidas de privacidade por design e não persistência de dados.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Módulos/Arquivos a alterar:
- [MODIFY] [style.css](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/static/css/style.css): Implementar variáveis CSS de cores, botões com contraste ajustado, estilização das barras do card inteligente e logo.
- [MODIFY] [base.html](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/templates/base.html): Renomear "RH" para "Departamento Pessoal" e adicionar a logo no cabeçalho.
- [MODIFY] [login.html](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/templates/login.html): Aplicar identidade visual, incluir a logo centralizada e mudar textos.
- [MODIFY] [acesso_negado.html](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/templates/acesso_negado.html): Renomear referências a "RH" para "Departamento Pessoal".
- [MODIFY] [dashboard.html](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/templates/dashboard.html):
  - Renomear textos de interface.
  - Adicionar o aviso de ausência da coluna do INSS.
  - Inserir o indicador do INSS (card e gráfico).
  - Incluir o filtro do INSS.
  - Remover gráficos separados de dias/horas.
  - Implementar o novo Card Inteligente com abas de modos (Combinado, Dias, Horas), dropdown de ordenação e barras de progresso horizontais personalizadas em HTML/CSS.
  - Adicionar colunas do INSS na tabela consolidada.
- [MODIFY] [excel_parser.py](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/utils/excel_parser.py):
  - Atualizar detecção do cabeçalho da coluna do INSS (opcional).
  - Implementar a leitura e normalização segura dos valores da coluna INSS.
  - Adicionar dados de INSS nas agregações e no dicionário retornado.
  - Preservar compatibilidade com planilhas antigas.
- [MODIFY] [views.py](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/views.py):
  - Ajustar mensagens e verificação do grupo de permissão para aceitar tanto o grupo clássico "RH" quanto o novo grupo "Departamento Pessoal".
- [MODIFY] [tests.py](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/tests.py):
  - Adicionar testes de unidade e integração para validar todas as novas regras de negócio (INSS, agregação de tempo combinada, novos limites e privacidade).
- [MODIFY] [INSTRUCOES_EXECUCAO.txt](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/INSTRUCOES_EXECUCAO.txt):
  - Atualizar documentação e roteiro de testes.
- [NEW] [0001_rename_rh_group.py](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/migrations/0001_rename_rh_group.py):
  - Migração de dados para criar/renomear o grupo de permissões no banco SQLite de forma idempotente e segura.

### Recursos Estáticos adicionados:
- [NEW] `logo.png` copiado para [dashboard/static/images/logo.png](file:///c:/Users/Unicompo/Documents/03_PYTHON1/08%20-%20RH_Grafico/dashboard/static/images/logo.png) a partir do arquivo original do projeto `Untitled-2.png`.

---

## 🚫 5. FORA DE ESCOPO

- **Mudança de nomes técnicos**: Não alterar o nome do app (`dashboard`), das URLs internas (`/dashboard/`), das tabelas internas ou das variáveis técnicas principais do Django para não gerar instabilidades ou quebrar dependências do sistema.
- **Persistência de dados**: É terminantemente proibido salvar os dados das planilhas em banco de dados ou arquivos de mídia persistentes.
- **Uso de Git pelo agente**: Proibido executar qualquer comando `git`.

---

## 📐 6. ARQUITETURA ATUAL AFETADA

- **Fluxo do Parser**: A função `parse_excel_in_memory` do arquivo `excel_parser.py` adicionará novas chaves ao dicionário retornado, incluindo `inss_available`, dados agregados do INSS e novas chaves de agregação por colaborador para o card inteligente.
- **Lógica de Autenticação**: A função `is_rh_member` será atualizada para aceitar o grupo `Departamento Pessoal` além do grupo legado `RH`, preservando compatibilidade.
- **Visualização do Dashboard**: Substituição dos gráficos Chart.js de dias e horas de afastamento por uma seção interativa dinâmica HTML/CSS renderizada via JavaScript local no frontend.

---

## 🔐 7. PRIVACIDADE E SEGURANÇA

- **Dados Temporários**: Os dados de afastamento pelo INSS serão processados estritamente em memória e descartados assim que a sessão terminar.
- **Tratamento de Logs**: Nenhuma associação direta entre colaborador e CID/INSS será gerada nos logs do servidor.
- **Sem CDNs Externas**: Todas as bibliotecas de gráficos e logos permanecem locais.

---

## 👥 8. PERFIS E PERMISSÕES

- **Grupo Principal**: "Departamento Pessoal" (e "RH" como fallback).
- **Validação**: Validação no backend com o decorator de permissão e desvio seguro para a view `acesso_negado`.
- **Bloqueio de Administrador**: Mantido o bloqueio para administradores e superusuários que não pertençam explicitamente ao grupo.

---

## 📄 9. CONTRATO DOS ARQUIVOS DE ENTRADA

A planilha deve ser `.xlsx`. O sistema passa a aceitar 5 ou 6 colunas:
1. `Nome do colaborador` (Obrigatória)
2. `Função do colaborador` (Opcional)
3. `Data inicial do atestado` (Obrigatória)
4. `CID` (Opcional)
5. `Quantidade de dias/ HORAS` (Obrigatória)
6. `Houve Afastamento Pelo INSS?` (Opcional)

---

## 🧼 10. REGRAS DE VALIDAÇÃO DO INSS

### Reconhecimento do Cabeçalho:
O sistema reconhecerá a coluna baseando-se na presença de `"inss"` no nome da coluna normalizado (conversão para minúsculas, remoção de acentos e espaços extras). Equivalentes aceitos:
- `Houve Afastamento Pelo INSS?`
- `Houve afastamento pelo INSS`
- `HOUVE AFASTAMENTO PELO INSS?`
- `Houve Afastamento Pelo INSS ?`

### Normalização dos Valores:
- **Como SIM**: "SIM", "Sim", "sim", "s" (após remoção de espaços extras).
- **Como NÃO**: "NÃO", "Não", "não", "NAO", "Nao", "nao", "n" (após remoção de acentos e espaços).
- **Como NÃO INFORMADO**: Valores em branco ou vazios.
- **Valores Inválidos**: Qualquer valor diferente de Sim ou Não gerará uma inconsistência registrada no painel de qualidade, sendo exibido no dashboard como `NÃO INFORMADO` sem quebrar o processamento do resto do atestado.

---

## ⚙️ 11. REGRAS DE NEGÓCIO DO CARD COMBINADO

### Agregação de Tempo:
- Não é permitida a conversão entre dias e horas (ex: assumir que 8 horas equivalem a 1 dia).
- O acumulador por colaborador deve computar os dias e as horas separadamente.
- Formato de exibição textual:
  - Se possuir apenas dias: `X dias` (ou `X dia`)
  - Se possuir apenas horas: `Y horas` (ou `Y hora`)
  - Se possuir ambos: `X dias e Y horas` (ou singular apropriado)
  - Se possuir zero de ambos: omitido da visualização.

### Modos de Visualização:
- **Combinado (Padrão)**: Apresenta o nome do colaborador, o texto descritivo e duas barras de progresso horizontais paralelas (uma amarela para dias e uma azul/indigo para horas).
- **Dias**: Mostra apenas a barra de dias e o total correspondente, ocultando registros com zero dias.
- **Horas**: Mostra apenas a barra de horas e o total correspondente, ocultando registros com zero horas.

### Escalas das Barras:
- A barra de dias é normalizada com base no valor máximo de dias acumulados entre todos os colaboradores no conjunto filtrado.
- A barra de horas é normalizada de forma independente, com base no valor máximo de horas acumulados entre todos os colaboradores.
- Rótulos com os valores exatos são exibidos ao lado das barras.

### Ordenação:
Disponível um dropdown com ordenação explícita:
- `Mais atestados` (padrão): contagem total de atestados decrescente.
- `Mais dias`: total de dias acumulados decrescente.
- `Mais horas`: total de horas acumuladas decrescente.
- `Ordem alfabética`: nome do colaborador crescente.

---

## 📊 12. REQUISITOS DE INTERFACE E VISUALIZAÇÃO

### Cores e Contraste:
- **Cor Primária**: Amarelo `#eac532`.
- **Botões e Componentes de Destaque**: Usar texto grafite escuro (`#0f172a` ou `#1e293b`) sobre botões amarelos para garantir contraste de leitura.
- **Indicadores do INSS**:
  - Exibido apenas se a coluna estiver presente na planilha.
  - Card principal: `Atestados com afastamento pelo INSS` exibindo quantidade de registros `SIM` e percentual de incidência calculated sobre o total de respostas válidas (Sim + Não).
  - Tooltip explicativa sobre a exclusão de "Não informados" do percentual.
  - Gráfico de distribuição (rosca ou barras) agregando `SIM`, `NÃO` e `NÃO INFORMADO`.
- **Warning Banner**: Se a planilha for do formato antigo de 5 colunas, exibir um banner de aviso discreto e amigável: `A coluna "Houve Afastamento Pelo INSS?" não foi encontrada. Os indicadores de INSS não estão disponíveis para este arquivo.`

---

## 🧪 13. CRITÉRIOS DE ACEITAÇÃO

- [ ] Identidade textual atualizada de "RH" para "Departamento Pessoal" nas telas visíveis.
- [ ] Logotipo integrado nas telas de Login, Cabeçalho e Painel com proporção mantida.
- [ ] A cor principal do sistema é `#eac532` com contraste legível.
- [ ] A coluna do INSS é detectada de forma flexível e normalizada corretamente.
- [ ] O percentual do INSS ignora registros "Não informados" no denominador.
- [ ] Planilhas de 5 colunas continuam sendo processadas normalmente com aviso adequado.
- [ ] O novo Card Inteligente de Tempo exibe dias e horas de forma integrada e sem conversões.
- [ ] Os modos de visualização (Combinado, Dias, Horas) e ordenação funcionam de forma responsiva.
- [ ] A tabela resumida exibe informações de INSS quando disponíveis.
- [ ] Todos os testes automatizados passam sem falha.
- [ ] Nenhum dado confidencial é persistido ou enviado a APIs externas.
- [ ] Nenhum comando Git foi executado.

---

## 🔍 14. PLANO DE IMPLEMENTAÇÃO

1. **Migração do Banco**: Criar a migração `dashboard/migrations/0001_rename_rh_group.py` para criar ou renomear o grupo `RH` para `Departamento Pessoal` no banco SQLite de forma idempotente.
2. **Atualização do Parser**: Atualizar `excel_parser.py` para ler a nova coluna INSS (se presente), normalizar seus valores e calcular as métricas agregadas.
3. **Ajustes de Autenticação**: Atualizar `is_rh_member` em `views.py` para aceitar ambos os grupos de segurança.
4. **Tema e Logo**: Copiar `Untitled-2.png` para a pasta static como `logo.png` e atualizar as variáveis de cores e botões no arquivo `style.css`.
5. **Ajustes de Templates**: Atualizar os templates de login, acesso negado, base e dashboard para refletir o novo nome, carregar a logo e implementar o novo card inteligente interativo, os filtros e gráficos do INSS.
6. **Escrita e Execução de Testes**: Escrever testes no `tests.py` e executá-los para garantir o funcionamento correto de toda a especificação.

---

## 🚨 15. REGRA DE PARADA

Pare imediatamente e ajuste se ocorrer:
- Persistência física de dados sensíveis ou planilha.
- Uso de CDN externo.
- Qualquer comando `git`.
- Acesso indevido de administradores sem o respectivo grupo.
