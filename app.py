from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,date
from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    login_required,
    logout_user,
    current_user
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)
app = Flask(__name__)
app.secret_key = "my_super_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] ="sqlite:///Todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] =False
db=SQLAlchemy(app)
login_manager = LoginManager() #manage your user login
login_manager.init_app(app)  #  by using this flask-login   connect with your flask app  

login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(
        db.String(100),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(200),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(200),
        nullable=False
    )

    todos = db.relationship(
    'Todo',
    backref='owner',
    lazy=True
    )
    
@login_manager.user_loader
def load_user(user_id):
       return User.query.get(int(user_id))

class Todo(db.Model):
    sno=db.Column(db.Integer,primary_key=True)
    title=db.Column(db.String(200),nullable=False)
    desc=db.Column(db.String(500),nullable=False)
    date_created=db.Column(db.DateTime,default=datetime.utcnow)
    due_date = db.Column(db.Date,nullable=True)
    priority = db.Column(db.String(20),default='Medium')


    user_id = db.Column(
    db.Integer,
    db.ForeignKey('user.id'),
    nullable=False
)


    def __repr__(self)-> str:
        return f"{self.sno}-{self.title}"
    


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return "Email already registered"

        hashed_password = generate_password_hash(password)

        user = User(
            username=username,
            email=email,
            password_hash=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')
    
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(
            email=email
        ).first()

        if user and check_password_hash(
            user.password_hash,
            password
        ):
            login_user(user)

            return redirect('/')

        return "Invalid Email or Password"

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')


@app.route("/", methods=['GET', 'POST'])
@login_required
def hello_world():
    if request.method == 'POST':
        title = request.form['title']
        desc = request.form['desc']

        due_date = request.form.get('due_date')
        priority = request.form.get('priority')

        todo = Todo(
        title=title,
        desc=desc,
        due_date=datetime.strptime(
            due_date,
            "%Y-%m-%d"
        ).date() if due_date else None,
        priority=priority,
        user_id=current_user.id
    )

        db.session.add(todo)
        db.session.commit()

    allTodo = Todo.query.filter_by(user_id=current_user.id).all()
    return render_template('index.html', allTodo=allTodo)


@app.route('/show')
def product():
    allTodo= Todo.query.all()
    print(allTodo)
    return 'this is'

@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if request.method=='POST':
        title = request.form['title']
        desc = request.form['desc']
        todo = Todo.query.filter_by(sno=sno,user_id=current_user.id ).first()
        todo.title=title
        todo.desc=desc
        db.session.commit()
        return redirect("/")



    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html', todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno,user_id=current_user.id).first()

    if todo:
        db.session.delete(todo)
        db.session.commit()

    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    print(app.url_map)
    app.run(debug=True, port=8000)