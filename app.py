from flask_app import flask_app as app

from worker import page_bp, user_bp, auth_bp

app.register_blueprint(page_bp)
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(auth_bp, url_prefix='/auth')

if __name__ == '__main__':
    app.run(host='0.0.0.0')
