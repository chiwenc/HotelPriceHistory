from flask import Flask, render_template, jsonify 
import requests 
import json 
import os

app = Flask(__name__)
app.config['WTF_CSRF_EXEMPT_LIST'] = ['localhost', '127.0.0.1']
# @app.after_request
# def add_x_frame_options(response):
#     response.headers['X-Frame-Options'] = 'ALLOW-FROM http://localhost:8088/'
#     return response

@app.route('/')
def hello():
    return "hello"

@app.route('/dashboard') 
def superset_dashboard():
    return render_template('superset_dashboard.html')

@app.route("/guest-token", methods=["GET"])
def guest_token():
    url = "http://localhost:8088/api/v1/security/login" 
    payload = json.dumps({ "password": "861019", "provider": "db", "refresh": "true", "username": "Adam" })
    headers = { 'Content-Type': 'application/json', 'Accept': 'application/json' }

    responsel = requests.request("POST", url, headers=headers, data=payload) 
    print(responsel.text)
    superset_access_token = json.loads(responsel.text)['access_token']
    payload = json.dumps ({ 
        "user": {
            "username": "Adam",
            "first_name":"Adam", 
            "last_name":"Adam"
        },
        
        "resources": [{
            "type": "dashboard",
            "id": "33757d10-61a5-4e81-a917-5e6307789969"
        }],
        "rls": []
    })
               
    bearer_token = "Bearer " + superset_access_token
    print(bearer_token)
    response2 = requests.post(
         "http://localhost:8088/api/v1/security/guest_token", 
         data = payload,
         headers = { "Authorization": bearer_token, 'Accept': 'application/json', 'Content-Type': 'application/json' }) 
    print(response2.json())
    return jsonify(response2.json()['token'])

if __name__ == "__main__":
    # app.run(host="0.0.0.0", port=5000, debug=True)
    app.run(host="127.0.0.1", debug=True)