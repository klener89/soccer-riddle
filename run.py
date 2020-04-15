from app import create_app
from app import app

app = create_app('config.development')

if __name__ == '__main__':
    app.run()
