from flask import Flask
import os

app = Flask(__name__)

@app.route('/')
def hello():
    secret_value = os.environ.get('SECRET_KEY', 'No secret found')
    return f"Hello from K3S! Secret is: {secret_value}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
