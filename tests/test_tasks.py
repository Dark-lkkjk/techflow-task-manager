"""
Suite de testes automatizados — TechFlow Task Manager
Cobre: modelo Task, todas as rotas CRUD, filtros, validações e estatísticas.
"""
import json
from src.models import Task


# ── Helpers ───────────────────────────────────────────────────────────────────

def post_task(client, title='Tarefa de Teste', **kwargs):
    """Cria uma tarefa via API e retorna a resposta."""
    payload = {'title': title, **kwargs}
    return client.post('/api/tasks', json=payload)


def get_json(response):
    return json.loads(response.data)


# ── Modelo Task ───────────────────────────────────────────────────────────────

class TestTaskModel:
    """Testes unitários do modelo Task (persistência e serialização)."""

    def test_criar_e_persistir_tarefa(self, db, app):
        """Tarefa deve ser persistida com todos os campos corretos."""
        with app.app_context():
            task = Task(title='Minha Tarefa', description='Descrição', status='todo', priority='high')
            db.session.add(task)
            db.session.commit()

            salva = db.session.get(Task, task.id)
            assert salva is not None
            assert salva.title == 'Minha Tarefa'
            assert salva.priority == 'high'
            assert salva.status == 'todo'

    def test_valores_padrao(self, db, app):
        """Status e prioridade devem ter valores padrão."""
        with app.app_context():
            task = Task(title='Padrões')
            db.session.add(task)
            db.session.commit()
            assert task.status == 'todo'
            assert task.priority == 'medium'
            assert task.description == ''
            assert task.assignee == ''

    def test_to_dict_retorna_campos_obrigatorios(self, db, app):
        """to_dict() deve conter todos os campos necessários para a API."""
        with app.app_context():
            task = Task(title='Dict Test', status='in_progress', priority='low')
            db.session.add(task)
            db.session.commit()
            d = task.to_dict()

            campos = ['id', 'title', 'description', 'status', 'priority', 'assignee', 'created_at', 'updated_at']
            for campo in campos:
                assert campo in d, f"Campo '{campo}' ausente em to_dict()"

    def test_repr_contem_titulo(self, db, app):
        """__repr__ deve incluir o título e o status da tarefa."""
        with app.app_context():
            task = Task(title='Repr Test', status='done')
            db.session.add(task)
            db.session.commit()
            assert 'Repr Test' in repr(task)
            assert 'done' in repr(task)


# ── API — Criação ─────────────────────────────────────────────────────────────

class TestCriarTarefa:
    """Testes para POST /api/tasks."""

    def test_criar_tarefa_valida(self, client):
        """Deve criar tarefa e retornar 201 com os dados corretos."""
        resp = post_task(client, 'Implementar login', description='Usar JWT', priority='high', status='todo')
        assert resp.status_code == 201
        data = get_json(resp)
        assert data['title'] == 'Implementar login'
        assert data['priority'] == 'high'
        assert data['id'] is not None

    def test_criar_sem_titulo_retorna_400(self, client):
        """Tarefa sem título deve retornar 400."""
        resp = client.post('/api/tasks', json={'description': 'Sem título'})
        assert resp.status_code == 400

    def test_criar_titulo_vazio_retorna_400(self, client):
        """Título vazio (espaços) deve retornar 400."""
        resp = client.post('/api/tasks', json={'title': '   '})
        assert resp.status_code == 400

    def test_criar_titulo_muito_curto_retorna_400(self, client):
        """Título com menos de 3 chars deve retornar 400."""
        resp = post_task(client, 'ab')
        assert resp.status_code == 400
        assert 'caracteres' in get_json(resp)['error'].lower()

    def test_criar_titulo_muito_longo_retorna_400(self, client):
        """Título acima de 200 chars deve retornar 400."""
        resp = post_task(client, 'x' * 201)
        assert resp.status_code == 400

    def test_criar_status_invalido_retorna_400(self, client):
        """Status inválido deve retornar 400."""
        resp = post_task(client, 'Tarefa', status='invalido')
        assert resp.status_code == 400

    def test_criar_prioridade_invalida_retorna_400(self, client):
        """Prioridade inválida deve retornar 400."""
        resp = post_task(client, 'Tarefa', priority='urgente')
        assert resp.status_code == 400

    def test_criar_body_invalido_retorna_400(self, client):
        """Body não-JSON deve retornar 400."""
        resp = client.post('/api/tasks', data='texto puro', content_type='text/plain')
        assert resp.status_code == 400

    def test_criar_com_todos_os_campos(self, client):
        """Tarefa com todos os campos deve ser criada corretamente."""
        resp = post_task(client, 'Tarefa Completa',
                         description='Desc completa',
                         priority='high',
                         status='in_progress',
                         assignee='João Silva')
        assert resp.status_code == 201
        data = get_json(resp)
        assert data['assignee'] == 'João Silva'
        assert data['status'] == 'in_progress'


# ── API — Leitura ─────────────────────────────────────────────────────────────

class TestListarTarefas:
    """Testes para GET /api/tasks e GET /api/tasks/:id."""

    def test_listar_banco_vazio(self, client):
        """Banco vazio deve retornar lista vazia."""
        resp = client.get('/api/tasks')
        assert resp.status_code == 200
        assert get_json(resp) == []

    def test_listar_retorna_todas_tarefas(self, client):
        """Deve retornar todas as tarefas criadas."""
        post_task(client, 'Tarefa 1')
        post_task(client, 'Tarefa 2')
        post_task(client, 'Tarefa 3')
        data = get_json(client.get('/api/tasks'))
        assert len(data) == 3

    def test_obter_por_id_existente(self, client):
        """GET por ID válido deve retornar a tarefa."""
        task_id = get_json(post_task(client, 'Tarefa Específica'))['id']
        resp = client.get(f'/api/tasks/{task_id}')
        assert resp.status_code == 200
        assert get_json(resp)['title'] == 'Tarefa Específica'

    def test_obter_id_inexistente_retorna_404(self, client):
        """GET por ID inexistente deve retornar 404."""
        resp = client.get('/api/tasks/99999')
        assert resp.status_code == 404

    def test_filtrar_por_status(self, client):
        """Filtro por status deve retornar apenas tarefas daquele status."""
        post_task(client, 'A Fazer',    status='todo')
        post_task(client, 'Em Curso',   status='in_progress')
        post_task(client, 'Concluída',  status='done')

        data = get_json(client.get('/api/tasks?status=todo'))
        assert all(t['status'] == 'todo' for t in data)
        assert len(data) == 1

    def test_filtrar_por_prioridade(self, client):
        """Filtro por prioridade deve retornar apenas tarefas com aquela prioridade."""
        post_task(client, 'Alta',  priority='high')
        post_task(client, 'Baixa', priority='low')
        data = get_json(client.get('/api/tasks?priority=high'))
        assert all(t['priority'] == 'high' for t in data)

    def test_busca_por_titulo(self, client):
        """Busca textual deve filtrar por título."""
        post_task(client, 'Implementar autenticação')
        post_task(client, 'Corrigir bug no login')
        post_task(client, 'Refatorar banco de dados')

        data = get_json(client.get('/api/tasks?search=login'))
        assert len(data) == 1
        assert 'login' in data[0]['title'].lower()


# ── API — Atualização ─────────────────────────────────────────────────────────

class TestAtualizarTarefa:
    """Testes para PUT /api/tasks/:id."""

    def test_atualizar_titulo(self, client):
        """Deve atualizar o título da tarefa."""
        task_id = get_json(post_task(client, 'Título Original'))['id']
        resp = client.put(f'/api/tasks/{task_id}', json={'title': 'Título Atualizado'})
        assert resp.status_code == 200
        assert get_json(resp)['title'] == 'Título Atualizado'

    def test_atualizar_status(self, client):
        """Deve atualizar o status da tarefa."""
        task_id = get_json(post_task(client, 'Mover Tarefa', status='todo'))['id']
        resp = client.put(f'/api/tasks/{task_id}', json={'status': 'in_progress'})
        assert resp.status_code == 200
        assert get_json(resp)['status'] == 'in_progress'

    def test_atualizar_todos_campos(self, client):
        """Deve atualizar todos os campos simultaneamente."""
        task_id = get_json(post_task(client, 'Original'))['id']
        resp = client.put(f'/api/tasks/{task_id}', json={
            'title': 'Novo Título',
            'description': 'Nova descrição',
            'status': 'done',
            'priority': 'low',
            'assignee': 'Maria Souza',
        })
        data = get_json(resp)
        assert data['title'] == 'Novo Título'
        assert data['status'] == 'done'
        assert data['priority'] == 'low'
        assert data['assignee'] == 'Maria Souza'

    def test_atualizar_id_inexistente_retorna_404(self, client):
        """PUT em ID inexistente deve retornar 404."""
        resp = client.put('/api/tasks/99999', json={'title': 'Não existe'})
        assert resp.status_code == 404

    def test_atualizar_titulo_invalido_retorna_400(self, client):
        """Título inválido em update deve retornar 400."""
        task_id = get_json(post_task(client, 'Válida'))['id']
        resp = client.put(f'/api/tasks/{task_id}', json={'title': 'ab'})
        assert resp.status_code == 400

    def test_atualizar_sem_body_retorna_400(self, client):
        """PUT sem body JSON deve retornar 400."""
        task_id = get_json(post_task(client, 'Sem Body'))['id']
        resp = client.put(f'/api/tasks/{task_id}', data='', content_type='text/plain')
        assert resp.status_code == 400


# ── API — Exclusão ────────────────────────────────────────────────────────────

class TestExcluirTarefa:
    """Testes para DELETE /api/tasks/:id."""

    def test_excluir_tarefa_existente(self, client):
        """Tarefa existente deve ser excluída com sucesso."""
        task_id = get_json(post_task(client, 'Para Excluir'))['id']
        resp = client.delete(f'/api/tasks/{task_id}')
        assert resp.status_code == 200
        assert get_json(resp)['id'] == task_id

    def test_tarefa_nao_existe_apos_exclusao(self, client):
        """Tarefa excluída não deve mais existir no banco."""
        task_id = get_json(post_task(client, 'Será Excluída'))['id']
        client.delete(f'/api/tasks/{task_id}')
        assert client.get(f'/api/tasks/{task_id}').status_code == 404

    def test_excluir_id_inexistente_retorna_404(self, client):
        """DELETE em ID inexistente deve retornar 404."""
        resp = client.delete('/api/tasks/99999')
        assert resp.status_code == 404


# ── API — Estatísticas ────────────────────────────────────────────────────────

class TestEstatisticas:
    """Testes para GET /api/stats."""

    def test_stats_banco_vazio(self, client):
        """Estatísticas com banco vazio devem ter zeros."""
        data = get_json(client.get('/api/stats'))
        assert data['total'] == 0
        assert data['completion_rate'] == 0

    def test_stats_contagem_correta(self, client):
        """Contadores devem refletir o estado real das tarefas."""
        post_task(client, 'Task Alta 1',    status='todo',        priority='high')
        post_task(client, 'Task Baixa 2',   status='todo',        priority='low')
        post_task(client, 'Task Progresso', status='in_progress', priority='medium')
        post_task(client, 'Task Concluida', status='done',        priority='high')

        data = get_json(client.get('/api/stats'))
        assert data['total'] == 4
        assert data['todo'] == 2
        assert data['in_progress'] == 1
        assert data['done'] == 1
        assert data['high_priority'] == 2

    def test_taxa_conclusao(self, client):
        """Taxa de conclusão deve ser calculada corretamente."""
        post_task(client, 'Concluida A', status='done')
        post_task(client, 'Concluida B', status='done')
        post_task(client, 'Pendente C',  status='todo')
        post_task(client, 'Pendente D',  status='todo')

        data = get_json(client.get('/api/stats'))
        assert data['completion_rate'] == 50.0


# ── Frontend ──────────────────────────────────────────────────────────────────

class TestFrontend:
    """Testes de integração: rotas que servem a interface web."""

    def test_pagina_inicial_retorna_200(self, client):
        """A rota raiz deve retornar HTTP 200."""
        resp = client.get('/')
        assert resp.status_code == 200

    def test_pagina_inicial_contem_html(self, client):
        """Resposta da rota raiz deve conter HTML válido."""
        resp = client.get('/')
        assert b'TechFlow' in resp.data
        assert b'<!DOCTYPE html>' in resp.data
