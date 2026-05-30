# TechFlow Task Manager

> Sistema de gerenciamento de tarefas ágeis desenvolvido para a startup de logística LogiFlow. Permite acompanhar o fluxo de trabalho em tempo real, priorizar tarefas críticas e monitorar o desempenho da equipe.

---

## Objetivo do Projeto

A **TechFlow Solutions** foi contratada para desenvolver um sistema que centraliza o gerenciamento de tarefas em equipes que utilizam metodologias ágeis. O sistema oferece:

- Quadro Kanban visual com colunas **A Fazer**, **Em Progresso** e **Concluído**
- CRUD completo de tarefas (criar, listar, editar, excluir)
- Filtragem por status, prioridade e busca textual
- Dashboard de estatísticas em tempo real
- API RESTful para integração com outros sistemas

---

## Metodologia Adotada: Scrum + Kanban (Scrumban)

O projeto utiliza uma abordagem híbrida **Scrumban**:

| Prática         | Origem  | Aplicação no Projeto                            |
|-----------------|---------|------------------------------------------------|
| Sprint Planning | Scrum   | Tarefas planejadas por iterações de 1 semana   |
| Kanban Board    | Kanban  | Visualização do fluxo no GitHub Projects       |
| Daily Standup   | Scrum   | Sincronização diária da equipe via Issues      |
| WIP Limit       | Kanban  | Máximo de 3 tarefas simultâneas em progresso   |
| Retrospectiva   | Scrum   | Revisão ao fim de cada sprint                  |

---

## Estrutura do Repositório

```
techflow-task-manager/
├── src/
│   ├── __init__.py
│   ├── app.py          # Fábrica da aplicação Flask
│   ├── models.py       # Modelo Task (SQLAlchemy)
│   ├── routes.py       # Endpoints da API REST
│   └── templates/
│       └── index.html  # Interface Kanban (HTML/CSS/JS)
├── tests/
│   ├── __init__.py
│   ├── conftest.py     # Fixtures do pytest
│   └── test_tasks.py   # Suite de testes automatizados
├── docs/
│   └── teoria.html     # Documento teórico
├── .github/
│   └── workflows/
│       └── ci.yml      # Pipeline de Integração Contínua
├── run.py              # Ponto de entrada
├── requirements.txt    # Dependências Python
├── pytest.ini          # Configuração do pytest
└── README.md
```

---

## Instalação e Execução

### Pré-requisitos
- Python 3.10+
- pip

### 1. Clonar o repositório

```bash
git clone https://github.com/seu-usuario/techflow-task-manager.git
cd techflow-task-manager
```

### 2. Criar e ativar ambiente virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python -m venv venv
source venv/bin/activate
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Iniciar o servidor

```bash
python run.py
```

Acesse [http://localhost:5000](http://localhost:5000) no navegador.

---

## API REST — Endpoints

| Método   | Rota                  | Descrição                          |
|----------|-----------------------|------------------------------------|
| `GET`    | `/api/tasks`          | Listar tarefas (com filtros)        |
| `POST`   | `/api/tasks`          | Criar nova tarefa                   |
| `GET`    | `/api/tasks/:id`      | Obter tarefa por ID                 |
| `PUT`    | `/api/tasks/:id`      | Atualizar tarefa                    |
| `DELETE` | `/api/tasks/:id`      | Excluir tarefa                      |
| `GET`    | `/api/stats`          | Estatísticas das tarefas            |

### Filtros disponíveis em `GET /api/tasks`

| Parâmetro  | Valores                        | Exemplo                          |
|------------|-------------------------------|----------------------------------|
| `status`   | `todo`, `in_progress`, `done` | `?status=todo`                   |
| `priority` | `low`, `medium`, `high`       | `?priority=high`                 |
| `search`   | qualquer texto                | `?search=autenticação`           |

### Exemplo de payload para criação:

```json
{
  "title": "Implementar autenticação JWT",
  "description": "Usar Flask-JWT-Extended para proteger as rotas da API",
  "status": "todo",
  "priority": "high",
  "assignee": "João Silva"
}
```

---

## Testes Automatizados

O projeto utiliza **pytest** com **pytest-flask** e cobertura de 100% das rotas da API.

```bash
# Executar todos os testes
pytest tests/ -v

# Com relatório de cobertura
pytest tests/ --cov=src --cov-report=term-missing
```

### Casos de teste cobertos:
- ✅ Criação com dados válidos e retorno HTTP 201
- ✅ Validação de campos obrigatórios e limites de tamanho
- ✅ Listagem, filtragem por status/prioridade e busca textual
- ✅ Atualização parcial e completa de tarefas
- ✅ Exclusão e verificação de remoção do banco
- ✅ Estatísticas: contadores e taxa de conclusão
- ✅ Retorno HTTP 404 para recursos inexistentes

---

## Integração Contínua (GitHub Actions)

O pipeline em `.github/workflows/ci.yml` executa automaticamente em cada `push` ou `pull request`:

1. **Instala** as dependências do projeto
2. **Verifica qualidade** do código com `flake8`
3. **Executa** todos os testes com `pytest`
4. **Gera** relatório de cobertura e envia ao Codecov

---

## Gestão de Mudanças — Alteração de Escopo

### Escopo Original
O escopo inicial previa apenas um CRUD básico de tarefas com os campos: título, descrição, status e prioridade.

### Mudança Implementada (Sprint 2)
**Feature: Dashboard de Estatísticas em Tempo Real**

Após feedback do cliente (LogiFlow), ficou identificado que gestores precisavam visualizar métricas consolidadas para acompanhar a produtividade da equipe sem navegar tarefa por tarefa.

**Justificativa:** A visibilidade do fluxo de trabalho é um pilar central do Kanban. Sem métricas, o gerente não consegue identificar gargalos, distribuir carga ou reportar progresso.

**Implementação:**
- Campo `assignee` adicionado ao modelo `Task`
- Endpoint `GET /api/stats` com contadores por status, prioridade e taxa de conclusão
- Cards de estatísticas no topo do dashboard
- Filtro por responsável (preparado para Sprint 3)

**Atualização no Kanban:** Card "Dashboard de Estatísticas" criado, movido de *To Do* → *In Progress* → *Done* com commits associados.

---

## Questões Norteadoras

### Principais causas de falhas em projetos ágeis e como o GitHub mitiga:
As principais causas incluem má gestão de tarefas, falta de visibilidade do progresso e comunicação deficiente. O GitHub mitiga com o **Projects (Kanban)** para visualização de fluxo, **Issues** para rastreamento de bugs e melhorias, **Pull Requests** para revisão de código, e **Actions** para CI/CD que previne regressões.

### Beneficiados pelo sistema:
- **Gerentes de projeto:** visibilidade do progresso em tempo real via dashboard
- **Desenvolvedores:** clareza sobre o que priorizar e o estado atual do trabalho
- **Cliente (LogiFlow):** entrega previsível e rastreável de funcionalidades

### Como o GitHub Actions garante software confiável:
Testes automatizados executados em cada commit garantem que novas mudanças não quebram funcionalidades existentes (regressão). A análise estática com `flake8` mantém o padrão de qualidade do código.

---

## Tecnologias

| Tecnologia       | Versão | Uso                          |
|------------------|--------|------------------------------|
| Python           | 3.10+  | Linguagem principal          |
| Flask            | 3.1    | Framework web / API REST     |
| Flask-SQLAlchemy | 3.1    | ORM e persistência (SQLite)  |
| pytest           | 8.x    | Framework de testes          |
| flake8           | 7.x    | Linter / qualidade de código |
| GitHub Actions   | —      | CI/CD                        |

---

*Desenvolvido por Gabriel Telles — TechFlow Solutions · 2026*
