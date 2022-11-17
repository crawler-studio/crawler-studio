# 使用

## 初始化及运行WEBUI
初始化数据表到本地sqlite
```
cs migrate
cs init
```

运行WEB页面
```
cs runserver [ip]:[port]
```

注册用户用于登陆WEBUI
```
cs createsuperuser                 //注册
cs changepassword [username]       //修改密码
```

## 登陆WEBTUI后的设置
使用注册用户登陆 crawler-studio后，需要在 Settings-General 界面设置Scrapyd服务器地址、系统邮件发件人、监控收件人

![](https://tva1.sinaimg.cn/large/008vxvgGgy1h88eq428kbj325v0u0wgx.jpg)

设置Scrapyd服务器

![](https://tva1.sinaimg.cn/large/008vxvgGgy1h88eot4x9zj30u00urt9j.jpg)

设置系统邮件发件人

![](https://tva1.sinaimg.cn/large/008vxvgGgy1h88epc9u8cj30pw0i8q3t.jpg)

设置监控收件人

![](https://tva1.sinaimg.cn/large/008vxvgGgy1h88g21kfurj31340n6758.jpg)

## Scrapy爬虫设置
在scrapy项目的settings.py文件中开启扩展用于上传运行数据，其中
- CS_BACKEND    表示 crawler-studio 的运行地址
- CS_API_TOKEN  表示注册用户的token

```
CS_BACKEND = 'http://localhost:8000'
CS_API_TOKEN = '901f2e74fb57e12536dea98fd199aff0eddf0190'
EXTENSIONS = {
    'cs_sender.ScrapyMonitor': 500,
}
```

获取注册用户的token
```
cs get_token -u [username] -p [password]
```

## 完成
完成以上设置后，就可以开始正常使用Crawler-Studio了，后续每次在Start界面启动爬虫后，都会自动启动监控规则以及上传爬虫运行数据。
