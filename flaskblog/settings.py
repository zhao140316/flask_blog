import os


class Config:
	DEBUG = True
	# 配置使用的数据库
	# 什么数据库+驱动://用户名:密码@ip:端口/数据库名
	SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:melo140316@39.96.39.86:3306/flaskblog'
	SQLALCHEMY_TRACK_MODIFICATIONS = False  # 如果设置成True(默认)，Flask_SQLAlchemy将会追踪对象的修改并发送信号，这就需要额外的内存。
	SQLALCHEMY_ECHO = True  # 调试设置为true
	SECRET_KEY = 'suibianxiejiuxing'  # session的配置文件，使用session必须配置

	# 项目路径
	BASE_DIR = os.path.dirname(os.path.abspath(__file__))
	# 静态文件夹的路径
	STATIC_DIR = os.path.join(BASE_DIR, 'static')
	TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
	# 头像的上传目录
	UPLOAD_ICON_DIR = os.path.join(STATIC_DIR, 'upload/icon')
	# 相册的上传目录
	UPLOAD_PHOTO_DIR = os.path.join(STATIC_DIR, 'upload/photo')


class DevelopmentConfig(Config):
	'''开发环境'''
	ENV = 'development'


class ProductionConfig(Config):
	'''生产环境'''
	ENV = 'production'
