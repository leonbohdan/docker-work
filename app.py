from flask import Flask, Response, send_file
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

myEnvVar = os.environ.get("MY_ENV_VAR", "development")

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://app_user:1234@172.17.0.2/app_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Counter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)

with app.app_context():
    db.create_all()
    counter = Counter.query.first()
    if counter is None:
        counter = Counter(value=0)
        db.session.add(counter)
        db.session.commit()

@app.route('/')
def hello():
    counter = Counter.query.first()
    counter.value += 1
    db.session.commit()

    return f'''
    Docker is Awesome! My env var is: <b>{myEnvVar}</b>
    <br/>
    This page was reloaded <b>{counter.value}</b> times
<pre>                  ##        .</pre>
<pre>            ## ## ##       ===</pre>
<pre>        ## ## ## ##      ===</pre>
<pre>    /""""""""""""""""""\___/ ===</pre>
<pre> ~~~ (~~ ~~~~ ~~~ ~~~~ ~~ ~ /  ===-- ~~~</pre>
<pre>    \______ o          __/</pre>
<pre>      \    \        __/</pre>
<pre>       \____\______/</pre>
    '''

@app.route('/logo')
def docker_logo():
    return send_file('docker-logo.jpg', mimetype='image/jpg')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
