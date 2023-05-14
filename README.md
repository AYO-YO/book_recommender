# 这本书怎么样

> 📖推荐网站

## 💡功能简介

1. **登录/注册**
    - 注册、登录（如果失败，展示提示）
    - 注销功能
    - 注册时选择一本感兴趣图书
2. **加载主页-书籍列表**
    - 按用户评价历史推荐图书
    - 畅销书推荐
    - 图书搜索
3. **图书详细信息页面**
    - 图书详情
    - 用户评价：
4. **我的页面**
    - 我感兴趣的书
    - 关注与粉丝
5. **“其他用户”页**
    - 其他用户感兴趣的图书
    - 注册其他用户感兴趣的图书兴趣
    - 用户发布的评论

---

## 💡运行说明

### 环境准备

> 本项目使用Python3.11开发，其他版本兼容性可自行测试

使用conda创建并管理虚拟环境：

```bash
conda create -n book_rec python=3.11
conda activate book_rec
```

安装依赖：

```shell
cd django_recommend_book
pip install -r requirements.txt
```

### 数据库准备

> 本项目采用`SQLite3`作为后台数据库，采用其他数据库如mysql可前往`django_book/settings.py`编辑`DATABASE`配置项。

数据库迁移：

```bash
python manage.py makemigrations  # 生成迁移文件
python manage.py migrate  # 迁移
python manage.py showmigrations  # 检查迁移
```

迁移完成以后，创建用于后台管理的admin账号

```bash
python manage.py createsuperuser
```

### 运行项目
:
可直接使用django服务器运行：

```bash
python manage.py runserver 0.0.0.0:8000
```
