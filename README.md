# crawler-studio
## 一款在线监控Scrapy爬虫的软件

- 监控爬虫运行参数
- 监控爬虫日志错误率
- 监控爬虫内存占用
- 分布式爬虫管理
- 爬虫文档管理


## 使用说明

### 1. 安装
```
pip install crawler_studio
pip install cs_sender
```

### 2. 初始化
```
cs migrate
cs init
```

### 3. 注册用户
```
cs createsuperuser                 //注册
cs changepassword [username]       //修改密码
```

### 4. 运行WEB页面
```
cs runserver [ip]:[port]
```

### 5. 开启Scrapy爬虫扩展
在scrapy的settings.py文件中开启下列扩展，其中
- CS_BACKEND    表示WEBUI运行地址
- CS_API_TOKEN  表示注册用户的token

```python
CS_BACKEND = 'http://localhost:8000'
CS_API_TOKEN = '901f2e74fb57e12536dea98fd199aff0eddf0190'
EXTENSIONS = {
    'cs_sender.ScrapyMonitor': 500,
}
```

- 获取用户token的指令
```
cs get_token -u [username] -p [password]
```

## 注意事项：
- 此服务依赖Mysql, Mysql版本需要大于等于5.7