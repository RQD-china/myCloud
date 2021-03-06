from django import forms
from django.contrib import auth
from app01.models import UserInfo, Avatars
from django.views import View
from django.shortcuts import redirect, render
from django.http import JsonResponse
import random

# 登录表单验证
class LoginForm(forms.Form):
    name = forms.CharField(error_messages={'required': '请输入用户名'})
    pwd = forms.CharField(error_messages={'required': '请输入密码'})

    # 全局钩子
    def clean(self):
        name = self.cleaned_data.get('name')
        pwd = self.cleaned_data.get('pwd')

        user = auth.authenticate(username = name, password = pwd)

        if not user:
            self.add_error('pwd', '用户名或密码错误')
            return self.cleaned_data
        self.cleaned_data['user'] = user
        return self.cleaned_data

# 注册表单验证
class SignForm(forms.Form):
    name = forms.CharField(error_messages={'required': '请输入用户名'})
    pwd = forms.CharField(error_messages={'required': '请输入密码'})
    re_pwd = forms.CharField(error_messages={'required': '请输入确认密码'})

    # 全局钩子
    def clean(self):
        pwd = self.cleaned_data.get('pwd')
        re_pwd = self.cleaned_data.get('re_pwd')

        if pwd != re_pwd:
            self.add_error('re_pwd', '两次密码不一致')
        return self.cleaned_data
    def clean_name(self):
        name = self.cleaned_data.get('name')
        user_query = UserInfo.objects.filter(username = name)
        if user_query:
            self.add_error('name', '该用户名已注册')
        return self.cleaned_data

# 错误处理
def cleanForm(form):
    # 表单验证
    errorDict: dict = form.errors
    # 获取错误代码
    errorCode = len(list(errorDict.keys()))
    # 拿到第一个错误信息字段名
    errorValid = list(errorDict.keys())[0]
    # 获取第一个错误信息
    errorMsg = errorDict[errorValid][0]

    return errorCode, errorMsg, errorValid
  
# POST api类
class LoginView(View):
    def post(self,request):
        res = {
            'code': 0,
            'msg': "登录成功",
            'self': None
        }
        form = LoginForm(request.data)

        # 登录失败
        if not form.is_valid():
            res['code'], res['msg'], res['self'] = cleanForm(form)
            return JsonResponse(res)
        
        # 登录成功
        user = form.cleaned_data.get('user')
        auth.login(request, user)
        return JsonResponse(res)

class SignView(View):
    def post(self, request):
        res = {
            'code': 0,
            'msg': "注册成功",
            'self': None
        }
        form = SignForm(request.data)

        # 注册失败
        if not form.is_valid():
            res['code'], res['msg'], res['self'] = cleanForm(form)
            return JsonResponse(res)
        
        # 注册成功
        data = request.data
        user = UserInfo.objects.create_user(
            username = data['name'],
            password = data['pwd'])
        
        # 随机选择头像
        avatar_list = [i.nid for i in Avatars.objects.all()]
        user.avatar_id = random.choice(avatar_list)
        user.save()
        return JsonResponse(res)
