from datetime import datetime
from exts import db


class User(db.Model):
	'''用户模型类'''
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	username = db.Column(db.String(15), nullable=False)
	password = db.Column(db.String(64), nullable=False)
	phone = db.Column(db.String(11), unique=True)
	email = db.Column(db.String(50))
	icon = db.Column(db.String(100))  # 头像，保存的是图片的地址
	isDelete = db.Column(db.Boolean, default=False)
	rdatetime = db.Column(db.DateTime, default=datetime.now)
	# relationship()的作用主要是在view和template中体现，用于一对多和多对一的查询
	articles = db.relationship('Article', backref='user',
							   lazy='dynamic')  # backref：反向引用。 lazy：决定了SQLAlchemy什么时候从数据库中加载数据
	comments = db.relationship('Comment', backref='user')

	def __str__(self):
		return self.username


class Photo(db.Model):
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	pname = db.Column(db.String(100), nullable=False)
	pdatetime = db.Column(db.DateTime, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __str__(self):
		return self.pname


class AboutMe(db.Model):
	'''关于我的信息类'''
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	content = db.Column(db.BLOB, nullable=False)
	aDatetime = db.Column(db.DateTime, default=datetime.now)
	user = db.relationship('User', backref='aboutme')


class MessageBoard(db.Model):
	'''我的留言'''
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	content = db.Column(db.String(255), nullable=False)
	mDatetime = db.Column(db.DateTime, default=datetime.now)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	user = db.relationship('User', backref='messages')




