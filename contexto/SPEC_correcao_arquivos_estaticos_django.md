# 🧠 SPEC — Correção da Configuração de Arquivos Estáticos Django

---

## 📌 1. CONTEXTO

- URL(s) envolvidas: `/static/*`, `/`, `/login/`, `/admin/*`
- Contexto(s): Infraestrutura Django / Arquivos Estáticos (CSS, JS, Imagens, Admin)
- Perfil(s) afetados: Todos os usuários (Usuário DP/RH, Gestor, Administrador)

---

## ❗ 2. PROBLEMA ATUAL

Ao implantar a aplicação no servidor Windows via Git, o comando `python manage.py collectstatic` falha com a exceção:
`django.core.exceptions.ImproperlyConfigured: You're using the staticfiles app without having set the STATIC_ROOT setting to a filesystem path.`

Como consequência:
- A configuração `STATIC_ROOT` não está definida em `rh_dashboard/settings.py`.
- `STATIC_URL` está configurado como `"static/"` (sem barra inicial padronizada `"/static/"`).
- O servidor de aplicação Django no Windows não serve os arquivos estáticos quando `DEBUG=False` ou quando executado via WSGI sem servidor web (Nginx/IIS) configurado especificamente para a rota `/static/`.
- As páginas da aplicação e do Django Admin aparecem sem estilização CSS, sem carregamento de imagens e sem JavaScript.

---

## 🎯 3. OBJETIVO

Configurar de forma definitiva, segura e portátil a gestão de arquivos estáticos no Django:
1. Definir `STATIC_URL = "/static/"` e `STATIC_ROOT = BASE_DIR / "staticfiles"`.
2. Integrar o middleware WhiteNoise (`whitenoise.middleware.WhiteNoiseMiddleware`) para permitir o envio eficiente dos arquivos estáticos diretamente pelo Django em qualquer ambiente (Windows server ou local).
3. Adicionar `whitenoise` ao `requirements.txt`.
4. Garantir que `python manage.py collectstatic --noinput` e `python manage.py check` executem com sucesso sem exceções.
5. Manter os arquivos de origem (`dashboard/static/`) versionados e garantir que a pasta de destino (`staticfiles/`) seja ignorada pelo Git.
6. Garantir compatibilidade com o Python 3.14 / Django 4.2 no ambiente de execução.

---

## 🧩 4. ESCOPO DA ALTERAÇÃO

### Arquivos a serem modificados:
- `rh_dashboard/settings.py`: Configurar `STATIC_URL`, `STATIC_ROOT`, adicionar `WhiteNoiseMiddleware`, definir `STORAGES` (ou `STATICFILES_STORAGE`) e adicionar compatibilidade de cópia de contexto para Python 3.14.
- `requirements.txt`: Adicionar a dependência `whitenoise>=6.0.0`.
- `INSTRUCOES_EXECUCAO.txt`: Atualizar instruções para inclusão do comando `collectstatic --noinput` e informações sobre a pasta `staticfiles/`.

### Arquivos a serem criados:
- `contexto/SPEC_correcao_arquivos_estaticos_django.md`: Esta especificação técnica.

---

## 🚫 5. FORA DE ESCOPO

- Não criar novo projeto ou ambiente virtual.
- Não alterar banco de dados ou criar migrations.
- Não alterar regras de negócio, formulários ou parsers de planilhas.
- Não remover nem mover arquivos estáticos de origem em `dashboard/static/`.
- Não inserir caminhos absolutos do servidor ou máquina local.
- Não executar comandos Git.

---

## 📐 6. ARQUITETURA ATUAL AFETADA

- **Configurações Django (`rh_dashboard/settings.py`)**: Camada de assets e middlewares.
- **Servidor WSGI/ASGI**: Integração do WhiteNoise no pipeline de middlewares do Django.
- **Arquivos Coletados (`staticfiles/`)**: Pasta de saída gerada pelo `collectstatic`.

---

## 🔐 7. PRIVACIDADE E SEGURANÇA

⚠️ Nenhuma regra de privacidade é alterada ou comprometida:
- O WhiteNoise serve estritamente arquivos estáticos públicos (CSS, JS, imagens do tema/logo).
- Dados de saúde e atestados não são afetados nem armazenados no disco/estáticos.
- Os cabeçalhos `Cache-Control: no-store, private` nas views do dashboard continuam preservados.

---

## 👥 8. PERFIS E PERMISSÕES

Não aplicável (arquivos estáticos públicos do tema e estáticos do Django Admin).

---

## 📄 9. CONTRATO DOS ARQUIVOS DE ENTRADA

Não aplicável a esta funcionalidade.

---

## 🧼 10. REGRAS DE VALIDAÇÃO

- `findstatic` deve ser capaz de localizar os estáticos do app (`css/style.css`, `images/logo.png`, `js/chart.min.js`).
- `collectstatic --noinput` deve coletar com sucesso todos os estáticos do app e do Django Admin para `STATIC_ROOT`.
- `check` deve reportar 0 erros.

---

## ⚙️ 11. REGRAS DE NEGÓCIO

Não aplicável.

---

## 📊 12. REQUISITOS DE INTERFACE E VISUALIZAÇÃO

- As páginas de Login, Dashboard, Acesso Negado e Django Admin devem renderizar com estilos CSS aplicados, logo visível e scripts executando corretamente.

---

## ❌ 13. TRATAMENTO DE ERROS

- Prevenir a exceção `ImproperlyConfigured` definindo um caminho válido utilizando `BASE_DIR / "staticfiles"`.
- Garantir que manifestos de estáticos não quebrem a aplicação caso falte algum arquivo opcional.

---

## 🧪 14. CRITÉRIOS DE ACEITAÇÃO

- [ ] `STATIC_ROOT = BASE_DIR / "staticfiles"` configurado em `settings.py`.
- [ ] `STATIC_URL = "/static/"` configurado com barra inicial.
- [ ] `whitenoise` adicionado ao `requirements.txt` e middleware configurado em `MIDDLEWARE`.
- [ ] `python manage.py check` executa sem erros.
- [ ] `python manage.py collectstatic --noinput` executa com sucesso copiando os arquivos para `staticfiles/`.
- [ ] `python manage.py test dashboard` executa e passa em todos os testes.
- [ ] Pasta `staticfiles/` permanece no `.gitignore`.
- [ ] Arquivos estáticos de origem (`dashboard/static/`) permanecem intactos e versionados.
- [ ] Nenhuns caminhos absolutos de máquinas específicas foram introduzidos.

---

## ⚠️ 15. RISCOS

- **Incompatibilidade de armazenamento com manifesto**: Mitigado utilizando `CompressedManifestStaticFilesStorage` ou `CompressedStaticFilesStorage` e verificando a ausência de `url()` quebrados.

---

## 📦 16. DEPENDÊNCIAS

- `whitenoise>=6.0.0`: Para servir arquivos estáticos de forma integrada e otimizada pelo servidor WSGI/Django no Windows.

---

## 🔍 17. PLANO DE IMPLEMENTAÇÃO (OBRIGATÓRIO)

### Passos:
1. **Fase do Arquiteto**:
   - Criação da SPEC (`contexto/SPEC_correcao_arquivos_estaticos_django.md`).
   - Mapeamento e decisão da arquitetura (WhiteNoise + `STATIC_ROOT`).
2. **Fase do Backend**:
   - Adicionar `whitenoise` ao `requirements.txt`.
   - Atualizar `rh_dashboard/settings.py` (Middlewares, `STATIC_ROOT`, `STATIC_URL`, `STORAGES`).
   - Atualizar `INSTRUCOES_EXECUCAO.txt`.
3. **Fase do QA**:
   - Executar `python manage.py check`.
   - Executar `python manage.py findstatic images/logo.png`.
   - Executar `python manage.py findstatic css/style.css`.
   - Executar `python manage.py collectstatic --noinput`.
   - Executar `python manage.py test dashboard`.

---

## 🧪 18. TESTES AUTOMATIZADOS

- Rodar a suíte existente de testes (`python manage.py test dashboard`).

---

## 🧪 19. TESTES MANUAIS

1. Executar `python manage.py collectstatic --noinput` e verificar se a pasta `staticfiles/` é criada com o conteúdo.
2. Iniciar o servidor com `python manage.py runserver` e acessar `/login`, `/dashboard`, `/admin` para validar o carregamento visual dos assets.

---

## 📂 20. EVIDÊNCIAS OBRIGATÓRIAS DO AGENTE

A serem fornecidas na entrega final.

---

## 🔄 21. ESTRATÉGIA DE REVERSÃO

- Desfazer alterações em `settings.py`, `requirements.txt` e `INSTRUCOES_EXECUCAO.txt`.
- Apagar a pasta gerada `staticfiles/`.

---

## 📝 22. DOCUMENTAÇÃO NECESSÁRIA

- Atualização em `INSTRUCOES_EXECUCAO.txt`.

---

## 🤖 23. ORDEM DOS SUBAGENTES

1. Arquiteto: Mapeamento, decisão técnica e elaboração da SPEC.
2. Backend: Alterações em `settings.py`, `requirements.txt` e instruções.
3. QA: Execução e validação dos comandos `check`, `findstatic`, `collectstatic` e `test`.

---

## 🚨 24. REGRA DE PARADA

- Pare se houver gravação de dados sensíveis ou execução de comandos Git.

---

## 🧠 25. PRINCÍPIO FINAL

> "Arquivos estáticos servidos com portabilidade, alta performance e zero caminhos absolutos."
