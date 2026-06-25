from datetime import datetime
from database import db
from models.category import Category
from models.task import Task
from models.user import User
from utils.validators import validate_task_data

def serialize_task(task, include_relations=False):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    if include_relations:
        data['user_name'] = task.user.name if task.user else None
        data['category_name'] = task.category.name if task.category else None
    return data

def list_tasks():
    return [serialize_task(task, include_relations=True) for task in Task.query.all()]

def get_task(task_id):
    task = db.session.get(Task, task_id)
    return serialize_task(task, include_relations=True) if task else None

def create_task(data):
    error = validate_task_data(data)
    if error:
        return None, error, 400
    if data.get('user_id') and not db.session.get(User, data['user_id']):
        return None, 'Usuário não encontrado', 404
    if data.get('category_id') and not db.session.get(Category, data['category_id']):
        return None, 'Categoria não encontrada', 404
    task = Task(title=data['title'], description=data.get('description', ''), status=data.get('status', 'pending'), priority=data.get('priority', 3), user_id=data.get('user_id'), category_id=data.get('category_id'))
    if data.get('due_date'):
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags
    db.session.add(task)
    db.session.commit()
    return serialize_task(task), None, 201

def update_task(task_id, data):
    task = db.session.get(Task, task_id)
    if not task:
        return None, 'Task não encontrada', 404
    error = validate_task_data(data, partial=True)
    if error:
        return None, error, 400
    for field in ('title', 'description', 'status', 'priority', 'user_id', 'category_id'):
        if field in data:
            setattr(task, field, data[field])
    if 'due_date' in data:
        task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d') if data['due_date'] else None
    if 'tags' in data:
        task.tags = ','.join(data['tags']) if isinstance(data['tags'], list) else data['tags']
    task.updated_at = datetime.utcnow()
    db.session.commit()
    return serialize_task(task), None, 200

def delete_task(task_id):
    task = db.session.get(Task, task_id)
    if not task:
        return 'Task não encontrada', 404
    db.session.delete(task)
    db.session.commit()
    return None, 200

def search_tasks(args):
    query = Task.query
    if args.get('q'):
        term = f"%{args.get('q')}%"
        query = query.filter((Task.title.like(term)) | (Task.description.like(term)))
    if args.get('status'):
        query = query.filter_by(status=args.get('status'))
    if args.get('priority'):
        query = query.filter_by(priority=int(args.get('priority')))
    return [serialize_task(task, include_relations=True) for task in query.all()]
