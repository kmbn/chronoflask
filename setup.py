from flask import Flask, session, redirect, url_for, render_template, flash
from flask_bootstrap import Bootstrap


# Create app
app = Flask(__name__)
bootstrap = Bootstrap(app)

# Load default config and override config from an environment variable
app.config.update(dict(
    # DATABASE=os.path.join(app.root_path, 'base.db'),
    DEBUG=True,
    SECRET_KEY='development key',
    # USERNAME='admin',
    # PASSWORD='default'
))
app.config.from_envvar('APP_SETTINGS', silent=True)


if __name__ == '__main__':
    #init_db()
    app.run(debug=True)