from django.shortcuts import render, redirect
from django.utils.deprecation import MiddlewareMixin


class AuthMiddleware(MiddlewareMixin):
    '''中间件'''

    def process_request(self, request):
        # 0 排除那些不需要登陆就能访问的页面
        # request.path_info  获取当前用户请求的 URL
        if request.path_info in ['/login/','/image/code/'] :
            return None
        # 1 读取当前访问的用户的session信息，如果能读到，说明已登录过，就继续向下执行
        info_dict = request.session.get('info')
        if info_dict:
            return
        # 如果没有登录过,回到登录页面
        return redirect('/login/')

        # 如果方法中没有返回值(返回None)，继续向后走
        # 如果方法中有返回值 HttpResponse  render  redirect  则不再继续向后执行


