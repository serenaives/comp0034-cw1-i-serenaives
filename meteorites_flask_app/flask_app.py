from meteorites_flask_app import create_app
from meteorites_flask_app.config import DevelopmentConfig

app = create_app(DevelopmentConfig)


@app.route('/')
def index():
    return 'This is the home page for my_flask_app'


if __name__ == '__main__':
    app.run(debug=True)
