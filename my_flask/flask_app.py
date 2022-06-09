from my_flask import create_app

app = create_app()


@app.route('/')
def index():
    return 'This is the home page for my_flask_app'


if __name__ == '__main__':
    app.run(debug=True)