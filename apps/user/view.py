import os
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, g
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from apps.article.models import ArticleType, Article
from apps.user.models import User, Photo, AboutMe, MessageBoard
from apps.user.smssend import SmsSendAPIDemo
from exts import db, cache
from settings import Config
from utils.util import upload_qiniu, delete_qiniu, send_message

user_bp = Blueprint('user', __name__, url_prefix='/user')

# 权限验证
required_login_list = ['/user/center', '/user/update', '/article/publish', '/user/photo', '/user/myphoto',
					   '/article/comment', '/user/about', '/user/show_about']

# 上传的头像图片支持的格式
ALLOWED_EXTENSIONS = ['jpg', 'png', 'gif', 'bmp']


@user_bp.app_template_filter('cdecode')
def decode(content):
	content = content.decode('utf-8')
	return content[:40]


# 钩子函数，用来做权限验证
@user_bp.before_app_request
def before_app_request():
	url = request.path  # 用户访问的url  /user/center
	print('------')
	print(url)
	if url in required_login_list:
		id = session.get('uid')
		if not id:
			return render_template('user/login.html')
		else:
			user = User.query.get(id)
			# g 是本次请求的一个对象
			g.user = user


# 首页
@user_bp.route('/')
@cache.cached(timeout=60) # 缓存视图函数， 使用户在一分钟之内再次访问首页不用加载
def index():
	# 获取cookie
	# uid = request.cookies.get('uid')
	# user = User.query.get(uid)
	#
	# return render_template('user/index.html', user=user)

	# 获取session
	uid = session.get('uid')
	# 获取page参数
	page = int(request.args.get('page', 1))
	# 获取文章列表
	pagination = Article.query.order_by(-Article.adatetime).paginate(page=page, per_page=3)
	# 获取分类列表
	types = ArticleType.query.all()

	# 获取文章点击量最高的5篇
	love_articles = Article.query.order_by(-Article.click_num).limit(5)

	if uid:
		user = User.query.get(uid)
		return render_template('user/index.html', user=user, pagination=pagination, types=types,
							   love_articles=love_articles)

	else:
		return render_template('user/index.html', pagination=pagination, types=types, love_articles=love_articles)


# 注册
@user_bp.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		# 获取数据
		username = request.form.get('username')
		password = request.form.get('password')
		repassword = request.form.get('repassword')
		phone = request.form.get('phone')
		email = request.form.get('email')

		users = User.query.filter(User.isDelete == False).all()
		for user in users:
			if user.username == username:
				return render_template('user/register.html', errmsg='用户名已存在')

		else:
			if password == repassword:
				user = User()
				user.username = username
				# 使用flask自带的加密
				user.password = generate_password_hash(password)
				user.phone = phone
				user.email = email

				db.session.add(user)
				db.session.commit()
				return redirect(url_for('user.login'))

			else:
				return '两次密码不一样'

	return render_template('user/register.html')


# 验证手机号
@user_bp.route('/check_phone')
def check():
	# 获取ajax参数
	phone = request.args.get('phone')

	user = User.query.filter(User.phone == phone).all()

	if len(user):
		return jsonify(code=1, errmsg='此号码已被注册')

	else:
		return jsonify(code=2, msg='此号码可用')


# 登录
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		f = request.args.get('f')
		if f == '1':
			# 用户名密码登录
			username = request.form.get('username')
			password = request.form.get('password')
			users = User.query.filter(User.username == username)
			for user in users:
				# 使用flask自带的检查加密和未加密的密码，返回布尔类型。
				if check_password_hash(user.password, password):
					# 设置cookie
					# response = redirect(url_for('user.index'))
					# response.set_cookie('uid', str(user.id), max_age=1800)
					# return response

					# 设置session,把session当成字典来用
					session['uid'] = user.id
					return redirect(url_for('user.index'))
			else:
				return render_template('user/login.html', errmsg='用户名或密码错误')

		elif f == '2':
			# 手机号验证码登录
			phone = request.form.get('phone')
			code = cache.get(phone)

			# 判断验证码
			if code == session.get(phone):
				user = User.query.filter(User.phone == phone).first()
				if user:
					# 手机号存在，登录成功
					session['uid'] = user.id  # 设置session
					return redirect(url_for('user.index'))
				else:
					return render_template('user/login.html', msg='手机号未注册')

			else:
				return render_template('user/login.html', msg='验证码错误')

	return render_template('user/login.html')


# 退出
@user_bp.route('/logout')
def logout():
	# cookie
	# response = redirect(url_for('user.index'))
	# # 清除cookie
	# response.delete_cookie('uid')
	# return response

	# 使用session
	del session['uid']
	return redirect(url_for('user.index'))


# 发送验证码
@user_bp.route('/sent')
def sent():
	# 获取参数
	phone = request.args.get('phone')

	# 判断手机号是否注册
	user = User.query.filter(User.phone == phone).first()

	ret, code = send_message(phone)
	if user:

		if ret is not None:
			if ret["code"] == 200:
				# 使用缓存把验证码保存到redis中
				cache.set(phone, code, timeout=180)
				return jsonify(code=200, msg='成功')
			else:
				print("ERROR: ret.code=%s,msg=%s" % (ret['code'], ret['msg']))
				return jsonify(code=400, msg='成功')

	else:
		return render_template('user/login.html', msg='手机号未注册')


# 用户中心
@user_bp.route('/center')
@cache.cached(timeout=60)
def center():
	id = session.get('uid')
	user = User.query.get(id)
	types = ArticleType.query.all()
	photos = Photo.query.filter(Photo.user_id == id).order_by(-Photo.pdatetime).limit(4)
	return render_template('user/center.html', user=user, types=types, photos=photos)


# 用户修改信息
@user_bp.route('/update', methods=['GET', 'POST'])
def update():
	if request.method == 'POST':
		# 获取参数
		username = request.form.get('username')
		phone = request.form.get('phone')
		email = request.form.get('email')
		# 只要是文件(图片)就用files 获取, icon -----> FileStorage格式
		icon = request.files.get('icon')

		id = session.get('uid')
		user = User.query.get(id)

		# # 校验数据
		# users = User.query.all()
		# for user in users:
		# 	if user.phone == phone:
		# 		# 说明手机号已存在
		# 		return render_template('user/center.html', user=g.user, esg='此手机号已注册')
		# else:
		# 获取上传图片的名字
		icon_name = icon.filename
		# 获取上传头像图片的后缀名
		suffix = icon_name.rsplit('.')[-1]
		if suffix in ALLOWED_EXTENSIONS:
			# 改变文件名，保证文件名复合python的命名规则
			icon_name = secure_filename(icon_name)
			# 把头像保存到本地
			file_path = os.path.join(Config.UPLOAD_ICON_DIR, icon_name)
			icon.save(file_path)

			# 把数据保存到数据库
			# user = g.user
			user.username = username
			user.phone = phone
			user.email = email
			# path = 'upload/icon'
			user.icon = 'upload/icon/' + icon_name
			# 向数据库提交
			db.session.commit()
			return redirect(url_for('user.center'))
		else:
			return render_template('user/center.html', user=user, msg='头像格式不正确')


	else:
		id = session.get('uid')
		user = User.query.get(id)
		return render_template('user/center.html', user=user)


# 相册上传
@user_bp.route('/photo', methods=['GET', 'POST'])
def photo():
	# 获取参数
	photo = request.files.get('photo')

	# 调用封装好的函数， 为了使view中简洁
	ret, info = upload_qiniu(photo)

	if info.status_code == 200:
		# 上传成功时，qiniu会返回200
		id = session.get('uid')
		photo = Photo()
		photo.pname = ret['key']
		photo.user_id = id
		# 保存数据库
		db.session.add(photo)
		db.session.commit()
		return '上传成功'
	else:
		return '上传失败'


# 相册照片删除
@user_bp.route('/delete')
def delete():
	pid = request.args.get('pid')
	photo = Photo.query.get(pid)
	pname = photo.pname

	# 调用封装好的删除照片对象
	info = delete_qiniu(pname)

	if info.status_code == 200:
		# qiniu云存储删除成功
		# 删除数据库中的数据
		db.session.delete(photo)
		db.session.commit()
		# 重定向到用户中心
		return redirect(url_for('user.center'))
	else:
		return render_template('user/center.html', errmsg='删除失败')


# 我的相册
@user_bp.route('/myphoto')
@cache.cached(timeout=60)
def myphoto():
	id = g.user.id
	user = User.query.get(id)
	# 文章分类
	types = ArticleType.query.all()
	# 默认是str类型
	page = int(request.args.get('page', 1))
	# photos是一个pagination类型
	photos = Photo.query.filter(Photo.user_id == id).order_by(-Photo.pdatetime).paginate(page=page, per_page=3)

	return render_template('user/myphoto.html', photos=photos, user=user, types=types)


# 展示关于我的信息
@user_bp.route('/show_about')
@cache.cached(timeout=60)
def show_about_me():
	uid = session.get('uid')
	user = User.query.get(uid)
	types = ArticleType.query.all()
	return render_template('user/about.html', user=user, types=types)


# 修改关于我的信息
@user_bp.route('/about', methods=['GET', 'POST'])
def about():
	uid = session.get('uid')
	user = User.query.get(uid)
	
	types = ArticleType.query.all()

	if request.method == 'POST':
		# 获取参数
		content = request.form.get('content')
		user_id = g.user.id

		about_me = AboutMe()
		about_me.content = content.encode('utf-8')
		about_me.user_id = user_id
		db.session.add(about_me)
		db.session.commit()

		return redirect(url_for('user.show_about_me'))

	return render_template('user/update_about_me.html', types=types, user=user)


# 我的留言
@user_bp.route('/message', methods=['GET', 'POST'])
@cache.cached(timeout=60)
def message():
	# 获取用户信息
	uid = session.get('uid')
	user = None
	if uid:
		user = User.query.get(uid)

	types = ArticleType.query.all()

	page = int(request.args.get('page', 1))  # 一定要转换成int类型

	# 查询留言内容
	boards = MessageBoard.query.order_by(-MessageBoard.mDatetime).paginate(page=page, per_page=3)

	if request.method == 'POST':
		content = request.form.get('content')
		msg_board = MessageBoard()
		if user != None:
			msg_board.user_id = uid
		else:
			msg_board.user_id = None

		msg_board.content = content
		# 提交数据库
		db.session.add(msg_board)
		db.session.commit()

		return redirect(url_for('user.message'))

	return render_template('user/board.html', user=user, boards=boards, types=types)


# 删除留言
@user_bp.route('del_board')
def del_board():
	# 获取要删除的留言id
	bid = request.args.get('bid')
	# 通过bid获取留言信息
	msg_board = MessageBoard.query.get(bid)
	# 数据库删除此留言
	db.session.delete(msg_board)
	db.session.commit()

	return redirect(url_for('user.center'))


# 搜索
@user_bp.route('/search')
def search():
	# 获取用户信息
	uid = session.get('uid')
	user = None
	if uid:
		user = User.query.get(uid)

	types = ArticleType.query.all()
	# 获取文章点击量最高的5篇
	love_articles = Article.query.order_by(-Article.click_num).limit(5)
	page = int(request.args.get('page', 1))

	# 获取关键字get参数
	keyword = request.args.get('keyword')
	result = Article.query.filter(or_(Article.title.contains(keyword),
									  Article.content.contains(keyword),
									  )).paginate(page=page, per_page=3)

	print('-----', result)

	if result.items:
		return render_template('user/search.html', result=result, types=types, love_articles=love_articles,
							   keyword=keyword, user=user)

	else:
		return render_template('user/warn.html', user=user)


@user_bp.route('/fabiao', methods=['GET', 'POST'])
def fabiao():
	if request.method == 'GET':
	
		return render_template('user/wangeditor.html')
	else:
		pass
