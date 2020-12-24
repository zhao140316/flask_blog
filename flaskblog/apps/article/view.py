from flask import Blueprint, request, render_template, g, redirect, url_for, session, jsonify

from apps.article.models import Article, ArticleType, Comment
from apps.user.models import User
from exts import db

article_bp = Blueprint('article', __name__, url_prefix='/article')


@article_bp.app_template_filter('adecode')
def decode(content):
	content = content.decode('utf-8')
	return content


# 发布文章
@article_bp.route('/publish', methods=['GET', 'POST'])
def publish():
	if request.method == 'POST':
		# 获取参数
		title = request.form.get('title')
		type_id = request.form.get('type')
		content = request.form.get('content')
		user_id = session.get('uid')

		article = Article()
		article.title = title
		article.type_id = type_id
		article.user_id = user_id
		article.content = content

		# 在数据库中保存
		db.session.add(article)
		db.session.commit()

		return redirect(url_for('user.index'))

	else:
		return render_template('user/wangeditor.html')



# 展示文章
@article_bp.route('/detail')
def detail():
	# 获取文章的id
	article_id = request.args.get('aid')
	# 通过文章的id获取文章信息
	article = Article.query.get(article_id)

	# 增加点击量
	article.click_num += 1
	db.session.commit()
	# 获取文章分类
	types = ArticleType.query.all()
	id = session.get('uid')
	user = User.query.get(id)

	page = int(request.args.get('page', 1))
	comments = Comment.query.filter(Comment.article_id==article_id).order_by(-Comment.cDatetime).paginate(page=page, per_page=3)

	return render_template('article/detail.html', article=article, types=types, user=user, comments=comments)


# 点赞
@article_bp.route('/love')
def love():
	# 获取被点赞的文章的id
	aid = request.args.get('aid')
	tag = request.args.get('tag')
	# 通过文章查询到该文章的信息
	article = Article.query.get(aid)

	if tag == '1':
		article.love_num -= 1
	else:
		article.love_num += 1
	db.session.commit()

	return jsonify(num=article.love_num)  # ajax必须返回json数据


# 收藏
@article_bp.route('/save')
def save():
	# 获取被点赞的文章的id
	aid = request.args.get('aid')
	tag = request.args.get('tag')
	# 通过文章查询到该文章的信息
	article = Article.query.get(aid)

	if tag == '1':
		article.save_num -= 1
	else:
		article.save_num += 1
	db.session.commit()

	return jsonify(num=article.save_num)  # ajax必须返回json数据


# 评论
@article_bp.route('/comment', methods=['GET', 'POST'])
def comment():
	if request.method == 'POST':
		# 获取评论内容
		comment_content = request.form.get('comment')
		# 获取用户的id
		user_id = g.user.id
		# 获取文章的id
		article_id = request.form.get('aid')

		# 创建Comment对象，向数据库中保存
		comment = Comment()
		comment.comment = comment_content
		comment.user_id = user_id
		comment.article_id = article_id

		db.session.add(comment)
		db.session.commit()

		return redirect(url_for('article.detail') + '?aid=' + article_id)

	return redirect(url_for('user.index'))


# 文章分类展示
@article_bp.route('article_type')
def article_type():
	aid = request.args.get('aid',1)
	# 获取用户信息
	uid = session.get('uid')
	user = None
	if uid:
		user = User.query.get(uid)
	# 获取文章分类
	types = ArticleType.query.all()

	# 通过aid获取此分类
	type = ArticleType.query.get(aid)

	page = int(request.args.get('page', 1))
	articles = Article.query.filter(Article.type_id==aid).paginate(page=page, per_page=3)

	love_articles = Article.query.order_by(-Article.click_num).limit(5)



	return render_template('article/article_type.html', user=user, types=types, type=type, articles=articles, love_articles=love_articles)




