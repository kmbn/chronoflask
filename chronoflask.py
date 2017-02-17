from app import app


# Run app
if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])