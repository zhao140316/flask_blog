from flask import Flask

import settings
from apps.article.view import article_bp
from apps.user.view import user_bp
from exts import db, bootstrap, cache

config = {
	'CACHE_TYPE': 'redis',
	'CACHE_REDIS_HOST': '39.96.39.86',
	'CACHE_REDIS_PORT': 6379
}


def create_app():
	'''工厂函数'''
	app = Flask(__name__, template_folder='../templates', static_folder='../static')
	app.config.from_object(settings.DevelopmentConfig)  # 设置配置文件
	db.init_app(app=app)  # 关联sqlalchemy

	# 注册蓝图
	app.register_blueprint(user_bp)
	app.register_blueprint(article_bp)

	# 注册bootstrap
	bootstrap.init_app(app=app)

	# 初始化flask-cache缓存文件
	cache.init_app(app=app, config=config)

	return app
