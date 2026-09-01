from flask import Flask, Response, send_file
import os

app = Flask(__name__)

myEnvVar = os.environ.get("MY_ENV_VAR", "development")

counter_file = "data/counter.txt"

def read_counter():
    try:
        with open(counter_file, 'r') as file:
            return int(file.read())
    except FileNotFoundError:
        return 0

def write_counter(counter):
    with open(counter_file, 'w') as file:
        file.write(str(counter))

@app.route('/')
def hello():
    counter = read_counter()
    counter += 1
    write_counter(counter)
    return f'''
    Docker is Awesome! My env var is: <b>{myEnvVar}</b>
    <br/>
    This page was reloaded <b>{counter}</b> times
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
