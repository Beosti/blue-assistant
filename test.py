from flask import Flask, request, jsonify

app = Flask(__name__)




@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    json_stuff = jsonify(data)
    print(data)
    return jsonify(data), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, ssl_context='adhoc')