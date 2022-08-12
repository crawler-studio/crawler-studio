# crawler-studio
## 一款在线爬虫监控软件

- 监控爬虫运行参数
- 监控爬虫日志错误率
- 监控爬虫内存占用
- 分布式爬虫管理
- 爬虫文档管理

## 安装
```pip install crawler-studio```

## 运行 WEB UI
```
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

## 使用说明
在scrapy的settings.py文件中开启下列扩展，其中
- CS_BACKEND    表示WEBUI运行地址
- CS_API_TOKEN  表示WEBUI访问token

```python
CS_BACKEND = 'http://localhost:8000'
CS_API_TOKEN = '901f2e74fb57e12536dea98fd199aff0eddf0190'
EXTENSIONS = {
    'crawler_studio.ScrapyMonitor': 500,
}
```

