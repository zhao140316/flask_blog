from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from apps import create_app
from exts import db
from apps.user.models import User, Photo
from apps.article.models import Article, Comment, ArticleType

app = create_app()

manager = Manager(app=app)
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
	manager.run()
