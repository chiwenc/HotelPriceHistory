from flask import Flask, render_template, request, url_for, redirect, jsonify

app = Flask(__name__)




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
