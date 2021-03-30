from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from scripts import scrape

app = Flask(__name__)
CORS(app)


@app.route('/assignments/', methods=['GET', 'POST', 'OPTIONS'])
def get_assignment():
    if request.method == 'OPTIONS':
        return build_preflight_response()
    else:
        username = request.args.get("username", None)
        password = request.args.get("password", None)
        
        # print(f'username: {username} \n password: {password} ')
        if username and password:
            return jsonify(scrape.main(username, password))
        return jsonify({'result': 'Need both the username and password'})


@app.route('/')
def index():
    return "<h1> Welcome to our server!! </h1>"


def build_preflight_response():
    response = make_response()
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add('Access-Control-Allow-Headers', "*")
    response.headers.add('Access-Control-Allow-Methods', "*")
    return response

def build_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
