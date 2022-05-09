#coding=utf-8
from django import forms
from django.forms import widgets
from django.forms import fields
from app_user import models
from django.core.exceptions import ValidationError
from django.shortcuts import redirect


# 验证用户名是否存在
def username_validators(value):
    count = models.UserInfo.objects.filter(username=value).count()
    if not count == 0:
        print(value)
        raise ValidationError('用户名已经存在', 'invalid')
    return value


# 注册验证
class registerVerify(forms.Form):
    # 自定义字段验证，验证不需要数据库
    username=fields.CharField(validators=[username_validators,],)
    password = fields.CharField(
                validators=[],
                min_length=4,
                max_length=16,
                error_messages={
                    'required': '密码不能为空',
                    'mim_length': '密码不能小于4',
                    'max_length': '密码不能大于16'
                    }
    )
    email = fields.EmailField()


# 登陆验证
class loginVerigy(forms.Form):
    username= fields.CharField(
        error_messages={'required':'用户名不能为空'},
                              widget=widgets.TextInput(attrs={'class':'name_input','placeholder':"请输入用户名"})
                              )
    password = fields.CharField(error_messages={'required':'密码不能为空'},
                              widget = widgets.PasswordInput(attrs={'class': 'pass_input','placeholder':"请输入密码"})
                              )


# 验证Session
def auth(func):
    def inner(reqeust,*args,**kwargs):
        v = reqeust.session.get('status')
        if not v:
            print('未取到session')
            return redirect('/user/login/')
        print('用户%s状态正常'%(reqeust.session.get('user_info').get('username')))
        return func(reqeust, *args,**kwargs)
    return inner
