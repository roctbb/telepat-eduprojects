import os

from flask import Flask, request, render_template, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
from config import *
import marko

app = Flask(__name__)
db_string = "postgres://{}:{}@{}:{}/{}".format(DB_LOGIN, DB_PASSWORD, DB_HOST, DB_PORT, DB_DATABASE)
app.config['SQLALCHEMY_DATABASE_URI'] = db_string
db = SQLAlchemy(app)
auth = HTTPBasicAuth()


users = {
    ADMIN_LOGIN: generate_password_hash(ADMIN_PASSWORD),
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    title = db.Column(db.String)
    description = db.Column(db.Text, nullable=True)
    tags = db.Column(db.String, default='')
    difficulty = db.Column(db.Integer, default=1)
    created_on = db.Column(db.DateTime, server_default=db.func.now())
    updated_on = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def get_description(self):
        return marko.convert(self.description)

    def get_tags(self):
        return self.tags.split(',')

try:
    db.create_all()
except:
    print('cant create structure')


@app.route('/')
def index():
    projects = Project.query.all()
    return render_template('index.html', projects=projects)

@app.route('/editor')
@auth.login_required
def editor():
    projects = Project.query.all()
    return render_template('editor/index.html', projects=projects)


@app.route('/editor/add')
@auth.login_required
def add_project_page():
    return render_template('editor/create.html', project=Project())


@app.route('/editor/add', methods=['POST'])
@auth.login_required
def add_project():
    project = Project(title=request.form.get('title'), description=request.form.get('description'), tags=request.form.get('tags'), difficulty=request.form.get('difficulty'))

    if project.title and project.description:
        db.session.add(project)
        db.session.commit()
        return redirect('/editor')
    else:
        return render_template('editor/create.html', project=project)


@app.route('/editor/<int:id>/edit')
@auth.login_required
def edit_project_page(id):
    project = Project.query.get(id)
    return render_template('editor/create.html', project=project)


@app.route('/editor/<int:id>/edit', methods=['POST'])
@auth.login_required
def edit_project(id):
    project = Project.query.get(id)
    project.title = request.form.get('title')
    project.description = request.form.get('description')
    project.tags = request.form.get('tags')
    project.difficulty = request.form.get('difficulty')

    if project.title and project.description:
        db.session.commit()
        return redirect('/editor')
    else:
        return render_template('editor/create.html', project=project)


@app.route('/editor/<int:id>/delete')
@auth.login_required
def delete_project(id):
    project = Project.query.get(id)
    db.session.delete(project)
    db.session.commit()
    return redirect('/editor')

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)
