from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route("/")
def home():
    return "hola Docker y WSL2 tu api esta funcionando"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)