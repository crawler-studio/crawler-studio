# crawler-studio
## 一款在线监控Scrapy爬虫的软件

- 监控爬虫运行参数
- 监控爬虫日志错误率
- 监控爬虫内存占用
- 分布式爬虫管理
- 爬虫文档管理


## 使用说明

### 1. 安装
```pip install crawler-studio```

### 2. 运行 WEB UI
```
cs makemigrations
cs migrate
cs runserver
```

### 3. 开启Scrapy爬虫扩展
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


## 开发说明
