from . import api
from flask import jsonify

@api.route('/test/')
def test():
    return jsonify({'a': 'test123'})
