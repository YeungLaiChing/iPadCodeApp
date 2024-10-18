import os
from flask import Flask
from flask import render_template
from flask import json

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

@app.route("/apiTestMain")
def testmain():
    return render_template('main.html', **locals())

app.run(port=5000, debug=True, host="0.0.0.0")
