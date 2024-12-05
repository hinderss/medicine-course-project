from flask import Flask, render_template, jsonify, flash
from requests import HTTPError

from app import app
from app.exceptions import HttpException, HttpJson


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404


@app.errorhandler(HttpJson)
def handle_http_json_exception(error: HttpJson):
    return jsonify(error.to_dict()), error.status_code


# @app.errorhandler(Exception)
# def handle_exception(e):
#     return render_template('error.html', error=str(e)), 500


@app.errorhandler(HttpException)
def handle_http_exception(e):
    return render_template('error.html', error=str(e)), e.status_code


@app.errorhandler(HTTPError)
def handle_http_error(e):
    flash(str(e), 'error')


@app.route('/raise_error')
def raise_error():
    raise Exception("Произошла ошибка!")


# if __name__ == '__main__':
#     app.run(debug=True)
