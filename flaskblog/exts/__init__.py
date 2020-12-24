from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

# 创建映射对象
db = SQLAlchemy()

# 创建Bootstrap对象
bootstrap = Bootstrap()

# 创建flask-caching对象
cache = Cache()