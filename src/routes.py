from flask import Blueprint, request, jsonify, render_template
from datetime import datetime, timezone
from .models import db, Task

tasks_bp = Blueprint('tasks', __name__)


@tasks_bp.route('/')
def index():
    """Página principal do sistema."""
    return render_template('index.html')


@tasks_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Retorna lista de tarefas com filtros opcionais."""
    status = request.args.get('status')
    priority = request.args.get('priority')
    search = request.args.get('search', '').strip()

    stmt = db.select(Task).order_by(Task.created_at.desc())

    if status and status in Task.VALID_STATUSES:
        stmt = stmt.where(Task.status == status)
    if priority and priority in Task.VALID_PRIORITIES:
        stmt = stmt.where(Task.priority == priority)
    if search:
        stmt = stmt.where(Task.title.ilike(f'%{search}%'))

    tasks = db.session.execute(stmt).scalars().all()
    return jsonify([t.to_dict() for t in tasks])


@tasks_bp.route('/api/tasks', methods=['POST'])
def create_task():
    """Cria uma nova tarefa."""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos ou ausentes'}), 400

    title = (data.get('title') or '').strip()
    if not title:
        return jsonify({'error': 'O título é obrigatório'}), 400
    if len(title) < 3:
        return jsonify({'error': 'Título deve ter pelo menos 3 caracteres'}), 400
    if len(title) > 200:
        return jsonify({'error': 'Título deve ter no máximo 200 caracteres'}), 400

    status = data.get('status', 'todo')
    priority = data.get('priority', 'medium')

    if status not in Task.VALID_STATUSES:
        return jsonify({'error': f'Status inválido. Use: {Task.VALID_STATUSES}'}), 400
    if priority not in Task.VALID_PRIORITIES:
        return jsonify({'error': f'Prioridade inválida. Use: {Task.VALID_PRIORITIES}'}), 400

    task = Task(
        title=title,
        description=(data.get('description') or '').strip(),
        status=status,
        priority=priority,
        assignee=(data.get('assignee') or '').strip(),
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(task.to_dict()), 201


@tasks_bp.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """Retorna uma tarefa específica pelo ID."""
    task = db.get_or_404(Task, task_id)
    return jsonify(task.to_dict())


@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    """Atualiza uma tarefa existente."""
    task = db.get_or_404(Task, task_id)
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Dados inválidos ou ausentes'}), 400

    if 'title' in data:
        title = (data['title'] or '').strip()
        if len(title) < 3:
            return jsonify({'error': 'Título deve ter pelo menos 3 caracteres'}), 400
        if len(title) > 200:
            return jsonify({'error': 'Título deve ter no máximo 200 caracteres'}), 400
        task.title = title

    if 'description' in data:
        task.description = (data['description'] or '').strip()

    if 'status' in data:
        if data['status'] not in Task.VALID_STATUSES:
            return jsonify({'error': f'Status inválido. Use: {Task.VALID_STATUSES}'}), 400
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] not in Task.VALID_PRIORITIES:
            return jsonify({'error': f'Prioridade inválida. Use: {Task.VALID_PRIORITIES}'}), 400
        task.priority = data['priority']

    if 'assignee' in data:
        task.assignee = (data['assignee'] or '').strip()

    task.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return jsonify(task.to_dict())


@tasks_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    """Exclui uma tarefa pelo ID."""
    task = db.get_or_404(Task, task_id)
    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Tarefa excluída com sucesso', 'id': task_id})


@tasks_bp.route('/api/stats', methods=['GET'])
def get_stats():
    """Retorna estatísticas consolidadas das tarefas."""
    all_tasks = db.session.execute(db.select(Task)).scalars().all()

    total = len(all_tasks)
    todo = sum(1 for t in all_tasks if t.status == 'todo')
    in_progress = sum(1 for t in all_tasks if t.status == 'in_progress')
    done = sum(1 for t in all_tasks if t.status == 'done')
    high = sum(1 for t in all_tasks if t.priority == 'high')
    completion_rate = round((done / total * 100), 1) if total > 0 else 0

    return jsonify({
        'total': total,
        'todo': todo,
        'in_progress': in_progress,
        'done': done,
        'high_priority': high,
        'completion_rate': completion_rate,
    })
