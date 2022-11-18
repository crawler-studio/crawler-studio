# Crawler-Studio

## Scrapy爬虫监控平台

- 使用简单，无需ELK及复杂的配置也能实现爬虫监控
- 大屏展示scrapy爬虫运行状况
- 可视化实时读取爬虫运行数据、错误日志
- 监控爬虫日志错误率、内存占用以及掉线通知
- 可视化分布式爬虫管理

![](https://tva1.sinaimg.cn/large/008vxvgGgy1h88cfhw9qbj31h20u00wi.jpg)

----
## 文档
https://crawler-studio.readthedocs.io/en/latest/

----
## 使用
安装crawler_studio
```
pip install crawler_studio
```

初始化数据库
```
cs migrate
cs init
```

注册WEBUI用户
```
cs createsuperuser                 //注册
cs changepassword [username]       //修改密码
```

运行WEB页面
```
cs runserver [ip]:[port]
```

爬虫项目安装 cs_sender
```
pip install cs_sender
```
在Scrapy项目的settings.py文件中开启扩展，其中
- CS_BACKEND    表示 crawler-studio 的运行地址
- CS_API_TOKEN  表示注册用户的token

```
CS_BACKEND = 'http://localhost:8000'
CS_API_TOKEN = '901f2e74fb57e12536dea98fd199aff0eddf0190'
EXTENSIONS = {
    'cs_sender.ScrapyMonitor': 500,
}
```

- 获取注册用户端token
```
cs get_token -u [username] -p [password]
```
