from src.app import create_app
from src.config.database import get_db
from src.config.settings import Settings

app = create_app()

if __name__ == '__main__':
    get_db()
    app.run(host=Settings.HOST, port=Settings.PORT, debug=Settings.DEBUG)
