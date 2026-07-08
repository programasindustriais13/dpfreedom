# 🧠 SPEC — Correção de Extensão XLSX Case-Insensitive

---

## 📌 1. CONTEXTO

- URL(s) envolvidas: `/dashboard/`
- Contexto(s): Departamento Pessoal / Importação de Atestados
- Perfil(s) afetados: Usuário com permissão operacional de Departamento Pessoal/RH

---

## ❗ 2. PROBLEMA ATUAL

Atualmente, o sistema de upload rejeita planilhas válidas de atestados se a extensão estiver escrita em letras maiúsculas ou mistas (ex: `.XLSX`, `.Xlsx`, `.xLsX`). Apenas a extensão em letras minúsculas (`.xlsx`) é aceita. Isso ocorre porque o validador do formulário executa uma verificação estrita de sufixo com diferenciação de maiúsculas/minúsculas (`endswith('.xlsx')`).

---

## 🎯 3. OBJETIVO

Permitir o upload de arquivos Excel válidos independentemente da forma como a extensão esteja escrita (case-insensitive), enquanto preserva a integridade de todas as outras validações de segurança e restrições de formato (proibir `.xls`, `.xlsm`, `.csv`, etc. e validar conteúdo de fato).

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Arquivos a serem modificados:
- `dashboard/forms.py`: Normalizar a extensão para minúsculas antes de validar. Atualizar help_text do campo.
- `dashboard/templates/dashboard.html`: Ajustar mensagem de orientação do usuário (upload-subtext) no formulário de upload.
- `dashboard/tests.py`: Adicionar testes de unidade abrangendo variações de maiúsculas/minúsculas, outros formatos e arquivos corrompidos com extensão em caixa alta.

---

## 🚫 5. FORA DE ESCOPO

- Aceitar outros formatos de planilhas/dados como `.xls`, `.xlsm` ou `.csv`.
- Alterar a lógica de negócios de processamento ou os gráficos/indicadores.
- Persistir qualquer informação no banco de dados ou em disco.
- Executar comandos Git.

---

## 📐 6. ARQUITETURA ATUAL AFETADA

Nenhuma mudança estrutural de arquitetura ocorrerá. A alteração está contida na camada de validação do formulário Django (`ExcelUploadForm` em `dashboard/forms.py`) e na interface HTML do template.

---

## 🔐 7. PRIVACIDADE E SEGURANÇA

⚠️ Todas as validações existentes de segurança e privacidade serão mantidas:
- Processamento inteiramente em memória.
- Limite de tamanho de 5 MB.
- Validação real do conteúdo pelo parser openpyxl (um arquivo apenas renomeado mas inválido continuará sendo rejeitado).
- Sem gravação de logs contendo dados pessoais.

---

## 👥 8. PERFIS E PERMISSÕES

- O acesso ao dashboard e ao processamento de arquivos continua restrito a usuários do grupo "Departamento Pessoal" ou "RH" ou com permissão `dashboard.view_rh_dashboard`.

---

## 📄 9. CONTRATO DOS ARQUIVOS DE ENTRADA

Planilha Excel contendo as 5 colunas obrigatórias, com formato de arquivo ZIP/OpenXML válido (conteúdo real de `.xlsx`), porém aceitando nome do arquivo com a extensão em qualquer combinação de maiúsculas/minúsculas (ex: `.XLSX`, `.Xlsx`, `.xLsX`, `.xlsx`).

---

## 🧼 10. REGRAS DE VALIDAÇÃO

- **Tamanho do arquivo**: Limite de 5 MB.
- **Extensão**: `.xlsx` (comparada de forma case-insensitive).
- **Conteúdo**: Processável com sucesso pelo `openpyxl`.

---

## ⚙️ 11. REGRAS DE NEGÓCIO

Não aplicável (sem alterações de negócio).

---

## 📊 12. REQUISITOS DE INTERFACE E VISUALIZAÇÃO

- Atualização da mensagem de ajuda para: "Selecione um arquivo Excel no formato .xlsx. A extensão pode estar escrita em letras maiúsculas ou minúsculas."
- O atributo `accept=".xlsx"` no input HTML pode ser mantido, pois o navegador geralmente lida com isso de forma case-insensitive ou aceita a extensão, mas a validação definitiva é efetuada no backend.

---

## ❌ 13. TRATAMENTO DE ERROS

Erros amigáveis em caso de:
- Extensão inválida (mesma mensagem customizada).
- Arquivo corrompido ou formato incorreto (mesma mensagem amigável sem revelar stack trace).

---

## 🧪 14. CRITÉRIOS DE ACEITAÇÃO

- [ ] Arquivo `atestados.xlsx` aceito.
- [ ] Arquivo `ATESTADOS.XLSX` aceito.
- [ ] Arquivo `Atestados.Xlsx` aceito.
- [ ] Arquivo `atestados.xLsX` aceito.
- [ ] Arquivo `.xls` rejeitado.
- [ ] Arquivo `.xlsm` rejeitado.
- [ ] Arquivo `.csv` rejeitado.
- [ ] Arquivo corrompido nomeado `.XLSX` rejeitado.
- [ ] Todos os testes passando com sucesso.

---

## ⚠️ 15. RISCOS

Nenhum risco adicional de segurança ou privacidade é introduzido por esta correção.

---

## 📦 16. DEPENDÊNCIAS

Nenhuma nova dependência.

---

## 🔍 17. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

### Passos:

1. **Fase do Arquiteto**: Definição da especificação (esta SPEC) e validação da segurança/privacidade.
2. **Fase do Backend**: 
   - Alterar `dashboard/forms.py` para extrair e validar a extensão usando `Path(name).suffix.lower()`.
   - Atualizar os textos de ajuda no formulário e no template HTML.
   - Adicionar casos de testes abrangentes no `dashboard/tests.py`.
3. **Fase do QA**: 
   - Rodar a suíte de testes automatizados (`python manage.py test`).
   - Confirmar ausência de comandos Git ou arquivos criados/alterados fora do escopo.

---

## 🧪 18. TESTES AUTOMATIZADOS

Novos casos de teste em `dashboard/tests.py`:
- `test_upload_xlsx_case_variants`: envia arquivos com extensões `.XLSX`, `.Xlsx`, `.xLsX` e valida o processamento com sucesso.
- `test_upload_invalid_formats_rejected`: envia arquivos `.xls`, `.xlsm`, `.csv` e valida a rejeição pelo formulário.
- `test_upload_corrupted_xlsx_caps_rejected`: envia arquivo corrompido terminado em `.XLSX` e valida a rejeição com mensagem amigável.

---

## 🧪 19. TESTES MANUAIS

Roteiro de validação local:
1. Upload de um arquivo válido `.xlsx`.
2. Upload do mesmo arquivo renomeado para `.XLSX`.
3. Upload do mesmo arquivo renomeado para `.Xlsx`.
4. Upload de um arquivo de texto qualquer renomeado para `.XLSX` (deve falhar).

---

## 📂 20. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

A serem informadas na entrega final.

---

## 🔄 21. ESTRATÉGIA DE REVERSÃO

- Desfazer as alterações de código nos arquivos correspondentes.

---

## 📝 22. DOCUMENTAÇÃO NECESSÁRIA

- `walkthrough.md` documentando as mudanças.

---

## 🤖 23. ORDEM DOS SUBAGENTES

1. Arquiteto
2. Backend
3. QA

---

## 🚨 24. REGRA DE PARADA

- Pare se houver comando Git ou modificação fora da pasta raiz do projeto.

---

## 🧠 25. PRINCÍPIO FINAL

> "Privacidade por design: dados temporários são processados e esquecidos."
