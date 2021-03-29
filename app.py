from flask import Flask, request, jsonify
from scripts import scrape
app = Flask(__name__)


@app.route('/assignments/', methods=['GET', 'POST'])
def get_assignment():
    username = request.args.get("username", None)
    password = request.args.get("password", None)

    # print(f'username: {username} \n password: {password} ')
    if username and password:
        return scrape.main(username, password)
    return {'result': 'Need both the username and password'}


@app.route('/')
def index():
    return "<h1> Welcome to our server!! </h1>"


if __name__ == '__main__':
    app.run(threaded=True, port=5000)
