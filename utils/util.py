# -*- coding: utf-8 -*-
# flake8: noqa
import random

from flask import session, jsonify
from qiniu import Auth, put_file, etag, put_data, BucketManager
from apps.user.smssend import SmsSendAPIDemo
import qiniu.config


# 图片上传qiniu
def upload_qiniu(filestorage):
	# 需要填写你的 Access Key 和 Secret Key
	access_key = 'zndDwEhp_gNhgjpUH-EIxIpk9J3ZLf7uPbrZAHA7'
	secret_key = '9YJn0ru1z_Y7HHPOhWBAzilt6fbwWu_RZTUhbOUK'

	# 构建鉴权对象
	q = Auth(access_key, secret_key)

	# 要上传的空间
	bucket_name = 'myblog0728'

	filename = filestorage.filename
	num = random.randint(1,2999)
	key = filename.rsplit('.')[0] + '_' + str(num) + '.' + filename.rsplit('.')[-1]
	# 上传后保存的文件名
	key = key

	# 生成上传 Token，可以指定过期时间等
	token = q.upload_token(bucket_name, key, 3600)

	# 要上传文件的本地路径
	# localfile = './sync/bbb.jpg'

	# ret, info = put_file(token, key, localfile)
	# print(info)
	# assert ret['key'] == key
	# assert ret['hash'] == etag(localfile)

	# qiniu 中封装的方法
	ret, info = put_data(token, key, filestorage.read())
	return ret, info



# 图片删除
def delete_qiniu(pname):
	access_key = 'zndDwEhp_gNhgjpUH-EIxIpk9J3ZLf7uPbrZAHA7'
	secret_key = '9YJn0ru1z_Y7HHPOhWBAzilt6fbwWu_RZTUhbOUK'

	#初始化Auth状态
	q = Auth(access_key, secret_key)

	#初始化BucketManager
	bucket = BucketManager(q)

	#你要测试的空间， 并且这个key在你空间中存在
	bucket_name = 'myblog0728'
	key = pname

	#删除bucket_name 中的文件 key
	ret, info = bucket.delete(bucket_name, key)
	return info


# 发送短信
def send_message(phone):
	# 手机已注册
	# 调用短信
	SECRET_ID = "dcc535cbfaefa2a24c1e6610035b6586"  # 产品密钥ID，产品标识
	SECRET_KEY = "d28f0ec3bf468baa7a16c16c9474889e"  # 产品私有密钥，服务端生成签名信息使用，请严格保管，避免泄露
	BUSINESS_ID = "748c53c3a363412fa963ed3c1b795c65"  # 业务ID，易盾根据产品业务特点分配
	api = SmsSendAPIDemo(SECRET_ID, SECRET_KEY, BUSINESS_ID)

	code = ''
	for i in range(4):
		ran = random.randint(0,9)
		code += str(ran)

	params = {
		"mobile": phone,
		"templateId": "11732",
		"paramType": "json",
		"params": {"code": code}
		# 国际短信对应的国际编码(非国际短信接入请注释掉该行代码)
		# "internationalCode": "对应的国家编码"
	}
	ret = api.send(params)
	return ret, code



