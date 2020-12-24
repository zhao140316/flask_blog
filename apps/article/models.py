from exts import db
from datetime import datetime


class ArticleType(db.Model):
	# 数据库中把名字改为article_type
	'''文章分类模型类'''
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	type_name = db.Column(db.String(20), nullable=False)
	articles = db.relationship('Article', backref='articletype')


class Article(db.Model):
	'''文章模型类'''
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # 主键
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 外键--->用户的id
	type_id = db.Column(db.Integer, db.ForeignKey('article_type.id'), nullable=False)
	title = db.Column(db.String(50), nullable=False)  # 标题
	content = db.Column(db.Text, nullable=False)  # 文章内容
	adatetime = db.Column(db.DateTime, default=datetime.now)  # 文章创建时间
	click_num = db.Column(db.Integer, default=0)  # 阅读量
	save_num = db.Column(db.Integer, default=0)  # 收藏
	love_num = db.Column(db.Integer, default=0)  # 点赞
	comments = db.relationship('Comment', backref='article')


class Comment(db.Model):
	'''评论模型类'''
	# __tablename__ = 'comment'  自定义表的名字，默认就是类名小写
	id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
	article_id = db.Column(db.Integer, db.ForeignKey('article.id'))
	comment = db.Column(db.String(256), nullable=False)
	cDatetime = db.Column(db.DateTime, default=datetime.now)

	def __str__(self):
		return self.comment
