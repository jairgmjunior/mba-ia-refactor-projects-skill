from datetime import datetime, timedelta
from database import db
from models.category import Category
from models.task import Task
from models.user import User

def summary_report():
    all_tasks = Task.query.all()
    users = User.query.all()
    overdue = [task for task in all_tasks if task.is_overdue()]
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    return {
        'generated_at': str(datetime.utcnow()),
        'overview': {'total_tasks': len(all_tasks), 'total_users': len(users), 'total_categories': Category.query.count()},
        'tasks_by_status': {status: len([task for task in all_tasks if task.status == status]) for status in ['pending', 'in_progress', 'done', 'cancelled']},
        'tasks_by_priority': {'critical': len([task for task in all_tasks if task.priority == 1]), 'high': len([task for task in all_tasks if task.priority == 2]), 'medium': len([task for task in all_tasks if task.priority == 3]), 'low': len([task for task in all_tasks if task.priority == 4]), 'minimal': len([task for task in all_tasks if task.priority == 5])},
        'overdue': {'count': len(overdue), 'tasks': [{'id': task.id, 'title': task.title, 'due_date': str(task.due_date), 'days_overdue': (datetime.utcnow() - task.due_date).days} for task in overdue]},
        'recent_activity': {'tasks_created_last_7_days': Task.query.filter(Task.created_at >= seven_days_ago).count(), 'tasks_completed_last_7_days': Task.query.filter(Task.status == 'done', Task.updated_at >= seven_days_ago).count()},
        'user_productivity': [{'user_id': user.id, 'user_name': user.name, 'total_tasks': len(user.tasks), 'completed_tasks': len([task for task in user.tasks if task.status == 'done']), 'completion_rate': round((len([task for task in user.tasks if task.status == 'done']) / len(user.tasks)) * 100, 2) if user.tasks else 0} for user in users],
    }

def user_report(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return None
    tasks = Task.query.filter_by(user_id=user_id).all()
    done = len([task for task in tasks if task.status == 'done'])
    return {'user': {'id': user.id, 'name': user.name, 'email': user.email}, 'statistics': {'total_tasks': len(tasks), 'done': done, 'pending': len([task for task in tasks if task.status == 'pending']), 'in_progress': len([task for task in tasks if task.status == 'in_progress']), 'cancelled': len([task for task in tasks if task.status == 'cancelled']), 'overdue': len([task for task in tasks if task.is_overdue()]), 'high_priority': len([task for task in tasks if task.priority <= 2]), 'completion_rate': round((done / len(tasks)) * 100, 2) if tasks else 0}}

def list_categories():
    return [{**category.to_dict(), 'task_count': Task.query.filter_by(category_id=category.id).count()} for category in Category.query.all()]

def create_category(data):
    if not data or not data.get('name'):
        return None, 'Nome é obrigatório', 400
    category = Category(name=data['name'], description=data.get('description', ''), color=data.get('color', '#000000'))
    db.session.add(category)
    db.session.commit()
    return category.to_dict(), None, 201

def update_category(category_id, data):
    category = db.session.get(Category, category_id)
    if not category:
        return None, 'Categoria não encontrada', 404
    for field in ('name', 'description', 'color'):
        if field in data:
            setattr(category, field, data[field])
    db.session.commit()
    return category.to_dict(), None, 200

def delete_category(category_id):
    category = db.session.get(Category, category_id)
    if not category:
        return 'Categoria não encontrada', 404
    db.session.delete(category)
    db.session.commit()
    return None, 200
