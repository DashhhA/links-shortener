import random
from flask import Flask, request, jsonify, redirect
from string import ascii_letters, digits

from google.cloud import datastore

ALPHABET = ascii_letters + digits


app = Flask(__name__)


ds = datastore.Client(project='shortener19')


@app.route('/api/create')
def create_url():
    link = request.args.get('link')
    code = generate_code()

    key = datastore.Key('ShortUrl', code, project='shortener19')
    entity = datastore.Entity(key)
    entity['link'] = link
    entity['code'] = code
    entity['total_hits'] = 0
    ds.put(entity)

    response = {
        'long_link': link,
        'code': code
    }
    return jsonify(response)


@app.route('/<code>')
def resolve_code(code):
    query = ds.query(kind='ShortUrl')
    query.add_filter('code', '=', code)

    link = []

    for l in query.fetch():
        link.append(l['link'])
        l['total_hits'] = l['total_hits'] + 1
        ds.put(l)

    return redirect(link[0])


def generate_code(length=5):
    code = random.sample(ALPHABET, length)
    return ''.join(code)


if __name__ == '__main__':
    app.run()