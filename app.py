from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///thoughts.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Модели БД
class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    comments = db.Column(db.Text, nullable=True)
    tag = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    tag = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Главная страница — перенаправляем на todo
@app.route('/')
def index():
    return redirect(url_for('todo'))

# TODO
@app.route('/todo', methods=['GET', 'POST'])
def todo():
    if request.method == 'POST':
        title = request.form['title'].strip()
        comments = request.form.get('comments', '').strip()
        tag = request.form.get('tag', '').strip()
        if title:
            new_todo = Todo(title=title, comments=comments, tag=tag)
            db.session.add(new_todo)
            db.session.commit()
        return redirect(url_for('todo'))

    # Получаем фильтры из GET параметров
    filter_tag = request.args.get('tag', '')
    search_query = request.args.get('search', '').strip()
    sort_order = request.args.get('sort', 'asc')

    # Запрос и фильтрация
    query = Todo.query
    if filter_tag:
        query = query.filter(Todo.tag == filter_tag)
    if search_query:
        query = query.filter(Todo.title.ilike(f'%{search_query}%'))
    if sort_order == 'desc':
        query = query.order_by(Todo.created_at.desc())
    else:
        query = query.order_by(Todo.created_at.asc())

    todos = query.all()

    # Собираем уникальные теги для фильтра
    tags = sorted(set(t.tag for t in Todo.query.with_entities(Todo.tag).distinct() if t.tag))

    return render_template('todo.html', todos=todos, tags=tags,
                           filter_tag=filter_tag, search_query=search_query,
                           sort_order=sort_order)

# Редактирование Todo
@app.route('/todo/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if request.method == 'POST':
        title = request.form['title'].strip()
        comments = request.form.get('comments', '').strip()
        tag = request.form.get('tag', '').strip()
        if title:
            todo.title = title
            todo.comments = comments
            todo.tag = tag
            db.session.commit()
            return redirect(url_for('todo'))
    return render_template('edit_todo.html', todo=todo)

# Удаление Todo
@app.route('/todo/delete/<int:todo_id>', methods=['POST'])
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect(url_for('todo'))

# NOTES
@app.route('/notes', methods=['GET', 'POST'])
def notes():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        tag = request.form.get('tag', '').strip()
        if title:
            new_note = Note(title=title, description=description, tag=tag)
            db.session.add(new_note)
            db.session.commit()
        return redirect(url_for('notes'))

    filter_tag = request.args.get('tag', '')
    search_query = request.args.get('search', '').strip()
    sort_order = request.args.get('sort', 'asc')

    query = Note.query
    if filter_tag:
        query = query.filter(Note.tag == filter_tag)
    if search_query:
        query = query.filter(Note.title.ilike(f'%{search_query}%'))
    if sort_order == 'desc':
        query = query.order_by(Note.created_at.desc())
    else:
        query = query.order_by(Note.created_at.asc())

    notes = query.all()

    tags = sorted(set(t.tag for t in Note.query.with_entities(Note.tag).distinct() if t.tag))

    return render_template('notes.html', notes=notes, tags=tags,
                           filter_tag=filter_tag, search_query=search_query,
                           sort_order=sort_order)

# Редактирование Notes
@app.route('/notes/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        tag = request.form.get('tag', '').strip()
        if title:
            note.title = title
            note.description = description
            note.tag = tag
            db.session.commit()
            return redirect(url_for('notes'))
    return render_template('edit_note.html', note=note)

# Удаление Notes
@app.route('/notes/delete/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('notes'))

# API для автопоиска (если хотите)
@app.route('/api/search_todo')
def api_search_todo():
    q = request.args.get('q', '').strip()
    results = []
    if q:
        todos = Todo.query.filter(Todo.title.ilike(f'%{q}%')).order_by(Todo.created_at.asc()).all()
        for t in todos:
            results.append({'id': t.id, 'title': t.title})
    return jsonify(results)

@app.route('/api/search_notes')
def api_search_notes():
    q = request.args.get('q', '').strip()
    results = []
    if q:
        notes = Note.query.filter(Note.title.ilike(f'%{q}%')).order_by(Note.created_at.asc()).all()
        for n in notes:
            results.append({'id': n.id, 'title': n.title})
    return jsonify(results)

if __name__ == '__main__':
    with app.app_context():  # Создаем контекст приложения
        db.create_all()  # Создаем таблицы в базе данных
    app.run(debug=True)
