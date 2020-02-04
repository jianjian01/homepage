from flask_app import flask_app as app
from util.tool import log_request, static_url

from worker import page_bp, user_bp, auth_bp


@app.context_processor
def static_url_processor():
    return dict(static_url=static_url)


app.after_request(log_request)
app.register_blueprint(page_bp)
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
