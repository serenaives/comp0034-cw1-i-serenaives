from coursework_2 import create_app

from coursework_2.config import DevelopmentConfig


app = create_app(DevelopmentConfig)

if __name__ == '__main__':
    app.run(debug=True)