# Skill: Auditoria e Refatoração Arquitetural

Uma skill agnóstica de tecnologia que automatiza a análise, auditoria e refatoração de projetos legados para o padrão MVC.

## Objetivo

Executar 3 fases sequenciais:
1. **Fase 1 — Análise**: Detectar stack (linguagem, framework, BD), mapear arquitetura, imprimir resumo
2. **Fase 2 — Auditoria**: Escanear código contra catálogo de anti-patterns, gerar relatório estruturado, solicitar confirmação
3. **Fase 3 — Refatoração**: Reestruturar para MVC, eliminar problemas detectados, validar funcionamento

## Escopo

- Funciona com qualquer stack: Python (Flask, FastAPI, Django), Node.js (Express, NestJS), etc.
- Detecta automaticamente linguagem, framework, banco de dados
- Identifica 10+ anti-patterns com severidade (CRITICAL, HIGH, MEDIUM, LOW)
- Gera relatório estruturado com arquivo:linha exatos
- Refatora automaticamente preservando funcionalidade

---

## FASE 1: PROJECT ANALYSIS

### Objetivo
Detectar a stack do projeto (linguagem, framework, BD), mapear a arquitetura atual e estrutura.

### Procedimento

1. **Detectar linguagem**
   - Procure por extensões: .py (Python), .js/.ts (JavaScript/TypeScript)
   - Leia package.json ou requirements.txt para confirmar

2. **Detectar framework**
   - Python: Procure por imports `flask`, `fastapi`, `django`
   - Node.js: Procure por imports `express`, `nestjs`, `koa`
   - Consulte arquivo de dependências

3. **Detectar banco de dados**
   - Procure por imports: `sqlite3`, `mysql`, `mongodb`, `sqlalchemy`, `prisma`
   - Identifique string de conexão ou configuração

4. **Mapear arquitetura atual**
   - Escaneia estrutura de diretórios
   - Conta quantos arquivos e suas responsabilidades
   - Identifique padrão atual: monolito, modular parcial, etc.

5. **Identificar domínio**
   - Leia comentários, nomes de tabelas, endpoints
   - Descreva em 1-2 linhas o que a aplicação faz

6. **Imprimir relatório**
   ```
   ================================
   PHASE 1: PROJECT ANALYSIS
   ================================
   Language:      [Python|Node.js|...]
   Framework:     [Flask|Express|...]
   Database:      [SQLite|PostgreSQL|...]
   Domain:        [Descrição do domínio]
   Architecture:  [Monolitic|Partially Modular|...]
   Source files:  [N] files analyzed
   ================================
   ```

---

## FASE 2: ARCHITECTURE AUDIT

### Objetivo
Escanear código contra catálogo de anti-patterns, gerar relatório, solicitar confirmação.

### Procedimento

1. **Ler Catálogo de Anti-Patterns**
   - Consultar `antipatterns-catalog.md` para lista completa
   - Para cada anti-pattern, procure pelos sinais de detecção

2. **Escanear Projeto**
   - Leia todos os arquivos .py, .js, .ts
   - Para cada arquivo, verifique contra cada anti-pattern
   - Registre: severidade, arquivo, linha(s), descrição

3. **Gerar Relatório**
   - Usar template de `report-template.md`
   - Ordenar findings por severidade: CRITICAL → HIGH → MEDIUM → LOW
   - Incluir arquivo:linha exatos
   - Incluir descrição, impacto e recomendação

4. **Exemplo de output**
   ```
   ================================
   ARCHITECTURE AUDIT REPORT
   ================================
   Project: [project-name]
   Stack:   [Language] + [Framework]
   Files:   [N] analyzed
   
   ## Summary
   CRITICAL: [N] | HIGH: [N] | MEDIUM: [N] | LOW: [N]
   
   ## Findings
   
   ### [CRITICAL] Hardcoded Credentials
   File: app.py:8
   Description: ...
   Impact: ...
   Recommendation: ...
   
   ...
   
   ## Total Findings
   [N] issues found
   ```

5. **Solicitar Confirmação**
   ```
   ================================
   Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
   > [user input]
   ```
   - Se `n`, abortar
   - Se `y`, prosseguir para Fase 3

---

## FASE 3: REFACTORING

### Objetivo
Reestruturar projeto para padrão MVC, eliminar problemas detectados, validar funcionamento.

### Procedimento

1. **Criar estrutura MVC**
   - Seguir convenções de `mvc-guidelines.md`
   - Criar diretórios:
     ```
     src/
     ├── config/           # Configuração (sem hardcoded)
     ├── models/           # Models (abstração de dados)
     ├── controllers/      # Controllers (lógica de fluxo)
     ├── views/ ou routes/ # Routes/Views (HTTP routes)
     ├── middleware/       # Middleware (logging, error, auth)
     ├── utils/            # Utilitários
     └── app.py            # Entry point
     ```

2. **Refatorar anti-patterns**
   - Para cada finding, aplicar transformação de `refactoring-playbook.md`
   - Exemplos:
     - Hardcoded Credentials → Usar config module + env vars
     - SQL Injection → Usar prepared statements / ORM
     - God Class → Separar em Models/Controllers/Views
     - Callbacks aninhados → Converter para async/await ou Promises
     - Estado global → Usar Injeção de Dependência
     - Duplicação → Extrair em funções/métodos reutilizáveis
     - Magic Strings → Usar constantes

3. **Validar funcionamento**
   - ✅ App inicia sem erros
   - ✅ Endpoints originais respondem (testar com curl)
   - ✅ Sem erros de segurança críticos
   - ✅ BD inicializa corretamente

4. **Salvar resultado**
   - Committar código refatorado
   - Manter backwards compatibility nos endpoints

---

## Como usar esta Skill

### Comando
```bash
codex "/refactor-arch"
```

### O que acontece
1. Executa FASE 1 (análise automática)
2. Executa FASE 2 (auditoria e relatório)
3. Aguarda confirmação do usuário
4. Se confirmado, executa FASE 3 (refatoração)
5. Valida resultado

### Arquivos de Referência

- `analysis-heuristics.md` — Heurísticas para detecção de linguagem/framework/BD
- `antipatterns-catalog.md` — Catálogo de 10+ anti-patterns com sinais de detecção
- `report-template.md` — Formato de relatório de auditoria
- `mvc-guidelines.md` — Padrão MVC alvo (modelos, controllers, views/routes)
- `refactoring-playbook.md` — 8+ padrões de transformação com exemplos antes/depois

---

## Notas Importantes

1. **Agnóstica de Tecnologia**: A skill funciona em Python, Node.js e qualquer outra linguagem com suporte a MVC
2. **Fase 2 é obrigatória**: Sempre pausar para confirmação antes de modificar qualquer arquivo
3. **Validação é crítica**: Testar que aplicação continua funcionando após refatoração
4. **Sem perda de funcionalidade**: Endpoints devem continuar respondendo da mesma forma
5. **Iterativo**: Se primeira execução não detectou todos os problemas, ajuste arquivos de referência e execute novamente
