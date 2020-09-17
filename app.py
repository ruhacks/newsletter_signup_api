from flask import Flask
import credentials
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World'
