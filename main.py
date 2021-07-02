from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import hashlib

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password_hash = db.Column(db.String(120))

    def __repr__(self):
        return '<User %r>' % self.name
    
    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,       
            'username': self.username,       
            'email': self.email       
        }


@app.route('/users', methods=['GET', 'POST'])
def get_users():       

    if request.method == 'POST':
        password = request.form['password']
        phash = hashlib.sha256(password.encode('utf-8')).hexdigest()
        user = User(username=request.form['username'], name=request.form['name'], password_hash=phash)       
        db.session.add(user)       
        db.session.commit()       
        return jsonify({'result': 'success'})

    users = User.query.all()
    return jsonify(users=[u.serialize() for u in users])

@app.route('/auth', methods=['POST'])
def auth():
    if request.method == 'POST':       
        username = request.form['username']       
        password = request.form['password']
        phash = hashlib.sha256(password.encode('utf-8')).hexdigest()  
        user = User.query.filter_by(username=username).first()       
        if user is not None and user.password_hash == phash:       
            return jsonify({'result': 'success', **user.serialize()})       
        else:       
            return jsonify({'result': 'fail'})

@app.route('/users/<id>')
def get_user_by_id(id):       
    return jsonify(User.query.get(id))   



@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':       
    app.run(debug=True)
    db.create_all()