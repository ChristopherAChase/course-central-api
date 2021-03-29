from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from scripts import scrape
app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['CORS_HEADERS'] = 'Content-Type'


@app.route('/assignments/', methods=['GET', 'POST'])
@cross_origin(supports_credentials=True)
def get_assignment():
    username = request.args.get("username", None)
    password = request.args.get("password", None)

    # print(f'username: {username} \n password: {password} ')
    if username and password:
        return jsonify(scrape.main(username, password))
    return jsonify({'result': 'Need both the username and password'})


@app.route('/')
def index():
    return "<h1> Welcome to our server!! </h1>"


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
