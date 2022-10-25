from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect
from app01 import models
from app01.utils.form import UserModelForm, PrettyModelForm, PrettyEditModelForm
from app01.utils.pagination import Pagination
from app01.utils.encrypt import md5


def depart_list(request):
    '''部门列表'''

    # 从数据库中获取所有的部门列表
    # [对象，对象，对象]
    queryset = models.Department.objects.all()
    return render(request, 'depart_list.html', {'queryset': queryset})


def depart_add(request):
    '''添加部门'''
    if request.method == 'GET':
        return render(request, 'depart_add.html')

    # 获取用户POST提交过来的数据
    title = request.POST.get('title')

    # 将数据保存到数据库中
    models.Department.objects.create(title=title)

    # 重定向回到列表
    return redirect('/depart/list/')


def depart_delete(request):
    '''删除部门'''''
    nid = request.GET.get('nid')
    models.Department.objects.filter(id=nid).delete()
    return redirect('/depart/list/')


def depart_edit(request, nid):
    '''修改部门'''
    if request.method == 'GET':
        row_object = models.Department.objects.filter(id=nid).first()
        return render(request, 'depart_edit.html', {'row_object': row_object})
    # 获取用户提交的标题
    title = request.POST.get('title')
    # 根据ID找到数据库中的数据并进行更新
    models.Department.objects.filter(id=nid).update(title=title)
    return redirect('/depart/list/')


def user_list(request):
    '''用户列表'''
    # i.gender  1 / 2
    # i.get_gender_display() 1-男  2-女      get_字段名称_display()
    # ------------------------------------------------------------------------
    # i.depart_id  #获取数据库中存储的那个字段值
    # i.depart  #根据id自动去关联的表中获取哪一行数据对象
    # i.depart.title  得到对象的title字段
    # -------------------------------------------------------------------------
    # i.create_time.strftime("%Y-%m-%d")   datetime---->字符串
    queryset = models.UserInfo.objects.all()
    '''
    for i in queryset:

        print(i.id,i.name,i.age,i.get_gender_display(),i.create_time.strftime("%Y-%m-%d"))
        print(i.depart.title,i.name)
    '''
    page_object = Pagination(request, queryset, page_size=2)
    context = {
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html(),  # 生成页码
    }
    return render(request, 'user_list.html', context)


# {'queryset': queryset}

def user_add(request):
    '''添加用户(原始方式)'''

    if request.method == 'GET':
        content = {
            'gender_choices': models.UserInfo.gender_choices,
            'depart_list': models.Department.objects.all()
        }
        return render(request, 'user_add.html', content)

    # 获取用户POST提交过来的数据
    user = request.POST.get('user')
    pwd = request.POST.get('pwd')
    age = request.POST.get('age')
    account = request.POST.get('account')
    create_time = request.POST.get('ctime')
    depart_id = request.POST.get('dp')
    gender = request.POST.get('gender')

    # 将数据保存到数据库中
    models.UserInfo.objects.create(name=user, password=pwd, age=age, account=account,
                                   create_time=create_time, depart_id=depart_id, gender=gender)

    # 重定向回到列表
    return redirect('/user/list/')


###################################################### ModelForm


def user_model_form_add(request):
    if request.method == 'GET':
        form = UserModelForm()
        return render(request, 'user_model_form_add.html', {'form': form})

    # 用户POST提交数据，数据校验
    form = UserModelForm(data=request.POST)  # request.POST  数据库所有的数据
    if form.is_valid():
        # 如果数据合法，保存到数据库

        # print(form.cleaned_data)
        # models.UserInfo.objects.create  也可以保存到数据库
        form.save()  # 保存到数据库中
        return redirect('/user/list')
    # 校验失败（在页面上显示错误信息）
    return render(request, 'user_model_form_add.html', {'form': form})


def user_edit(request, nid):
    '''编辑用户'''

    # 根据ID去数据库获取要编辑的那一行数据
    # first 返回第一条记录，也是返回一个具体的对象
    # last  返回最后一条记录，也是返回一个具体的对象
    row_object = models.UserInfo.objects.filter(id=nid).first()
    if request.method == 'GET':
        #  instance=row_object 默认在文本框中填我们要修改的那一行数据
        form = UserModelForm(instance=row_object)
        return render(request, 'user_edit.html', {'form': form})

    form = UserModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 默认保存的是用户输入的所有数据，如果想要在用户输入以外增加一些值
        # form.instance.字段名 = 值
        form.save()
        return redirect('/user/list/')
    return render(request, 'user_edit.html', {'form': form})


def user_delete(request, nid):
    models.UserInfo.objects.filter(id=nid).delete()
    return redirect('/user/list/')


def pretty_list(request):
    '''靓号列表'''
    # for i in range(500):
    #     models.PrettyNum.objects.create(mobile='18122222222',price=10,level=1,status=1)
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict['mobile__contains'] = search_data

    queryset = models.PrettyNum.objects.filter(**data_dict).order_by("-level")

    '''
    # 根据用户想要访问的页码，计算出起始位置
    page = int(request.GET.get('page', 1))  # 当前页
    page_size = 10  # 每页显示10条数据
    start = (page - 1) * page_size
    end = page * page_size
    # desc
    queryset = models.PrettyNum.objects.filter(**data_dict).order_by('-level')[start:end]
    # 数据总条数
    total_count = models.PrettyNum.objects.filter(**data_dict).order_by('-level').count()
    # 总页码
    total_page_count, div = divmod(total_count, page_size)
    if div:
        total_page_count += 1

    # 计算出，显示当前页的前5页，后5页
    plus = 5
    if total_page_count <= 2 * plus + 1:
        # 数据库中的数据比较少，都没有达到11页
        start_page = 1
        end_page = total_page_count
    else:
        # 数据库中的数据比较多，大于11页
        # 当前页<5时（小极值）
        if page <= plus:
            start_page = 1
            end_page = 2 * plus
        else:
            # 当前页>5
            # 当前页+5 > 总页码
            if (page + plus) > total_page_count:
                start_page = total_page_count - 2 * plus
                end_page = total_page_count
            else:
                start_page = page - plus
                end_page = page + plus
    # 页码
    page_str_list = []
    # 首页
    page_str_list.append('<li><a href="?page={}">首页</a></li>'.format(1))
    # 上一页
    if page > 1:
        prev = '<li><a href="?page={}">上一页</a></li>'.format(page - 1)
    else:
        prev = '<li><a href="?page={}">上一页</a></li>'.format(1)
    page_str_list.append(prev)

    for i in range(start_page, end_page + 1):
        if i == page:
            ele = '<li class="active"><a href="?page={}">{}</a></li>'.format(i, i)
        else:
            ele = '<li><a href="?page={}">{}</a></li>'.format(i, i)
        page_str_list.append(ele)
        # 下一页
    if page < total_page_count:
        prev = '<li><a href="?page={}">下一页</a></li>'.format(page + 1)
    else:
        prev = '<li><a href="?page={}">下一页</a></li>'.format(total_page_count)
    page_str_list.append(prev)
    # 尾页
    page_str_list.append('<li><a href="?page={}">尾页</a></li>'.format(total_page_count))

    search_string = """
                <li>
                    <form style="float: left;margin-left: -1px" method="get">
                        <input name="page"
                               style="position: relative;float:left;display: inline-block;width: 80px;border-radius: 0;"
                               type="text" class="form-control" placeholder="页码">
                        <button style="border-radius: 0" class="btn btn-default" type="submit">跳转</button>
                    </form>
                </li>
                """

    page_str_list.append(search_string)
    page_string = mark_safe("".join(page_str_list))
    '''
    page_object = Pagination(request, queryset)
    context = {
        "search_data": search_data,

        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html()  # 页码
    }
    return render(request, 'pretty_list.html', context)


def pretty_add(request):
    '''添加靓号'''
    if request.method == 'GET':
        form = PrettyModelForm()
        return render(request, 'pretty_add.html', {'form': form})
    form = PrettyModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect('/pretty/list')
    return render(request, 'pretty_add.html', {'form': form})


def pretty_edit(request, nid):
    '''编辑靓号'''
    row_object = models.PrettyNum.objects.filter(id=nid).first()
    if request.method == 'GET':
        #  instance=row_object 默认在文本框中填我们要修改的那一行数据
        form = PrettyEditModelForm(instance=row_object)
        return render(request, 'pretty_edit.html', {'form': form})

    form = PrettyEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        # 默认保存的是用户输入的所有数据，如果想要在用户输入以外增加一些值
        # form.instance.字段名 = 值
        form.save()
        return redirect('/pretty/list/')
    return render(request, 'pretty_edit.html', {'form': form})


def pretty_delete(request, nid):
    '''删除靓号'''
    models.PrettyNum.objects.filter(id=nid).delete()
    return redirect('/pretty/list/')


def admin_list(request):
    '''管理员'''
    # 构造搜索
    data_dict = {}
    search_data = request.GET.get('q', "")
    if search_data:
        data_dict['username__contains'] = search_data

    # 根据搜索条件去数据库获取
    queryset = models.Admin.objects.filter(**data_dict)
    # 分页
    page_object = Pagination(request, queryset)
    context = {
        "queryset": page_object.page_queryset,  # 分完页的数据
        "page_string": page_object.html(),  # 生成页码
        'search_data': search_data
    }

    return render(request, 'admin_list.html', context)


from django import forms
from app01.utils.bootstrap import BootStrapModelForm


class AdminModelForm(BootStrapModelForm):
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput
    )

    class Meta:
        model = models.Admin
        fields = ['username', 'password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput
        }

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm = md5(self.cleaned_data.get('confirm_password'))
        if confirm != pwd:
            raise ValidationError('密码错误')
        # 返回什么，此字段以后保存到数据库就是什么
        return confirm


class AdminEditModelForm(BootStrapModelForm):
    # 只允许有  username  一个字段
    class Meta:
        model = models.Admin
        fields = ['username']


class AdminResetModelForm(BootStrapModelForm):
    # widget=forms.PasswordInput(render_value=True)   密码错误不会消息在密码框
    confirm_password = forms.CharField(
        label='确认密码',
        widget=forms.PasswordInput
    )

    class Meta:
        model = models.Admin
        fields = ['password', 'confirm_password']
        widgets = {
            'password': forms.PasswordInput
        }

    def clean_password(self):
        pwd = self.cleaned_data.get('password')
        md5_pwd = md5(pwd)
        #去数据库校验当前密码和新输入的是否一致
        exists = models.Admin.objects.filter(id=self.instance.pk,password=md5_pwd).exists()
        if exists:
            raise ValidationError('不能与以前的密码相同')
        return md5(pwd)

    def clean_confirm_password(self):
        pwd = self.cleaned_data.get('password')
        confirm = md5(self.cleaned_data.get('confirm_password'))
        if confirm != pwd:
            raise ValidationError('密码不一致')
        # 返回什么，此字段以后保存到数据库就是什么
        return confirm


def admin_add(request):
    '''添加管理员'''
    title = '新建管理员'
    if request.method == 'GET':
        form = AdminModelForm()
        return render(request, 'change.html', {'form': form, 'title': title})
    form = AdminModelForm(data=request.POST)
    if form.is_valid():
        # form.cleaned_data  会把所有提交的数据放在一个字典里边
        form.save()
        return redirect('/admin/list/')
    return render(request, 'change.html', {'form': form, 'title': title})


def admin_edit(request, nid):
    '''编辑管理员'''
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect('/admin/list/')

    title = '编辑管理员'
    if request.method == 'GET':
        form = AdminEditModelForm(instance=row_object)
        return render(request, 'change.html', {'form': form, 'title': title})

    form = AdminEditModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/admin/list/')
    return render(request, 'change.html', {'form': form, 'title': title})


def admin_delete(request, nid):
    '''删除管理员'''
    models.Admin.objects.filter(id=nid).delete()
    return redirect('/admin/list/')


def admin_reset(request, nid):
    '''重置密码'''
    row_object = models.Admin.objects.filter(id=nid).first()
    if not row_object:
        return redirect('/admin/list/')
    title = '重置密码 - {}'.format(row_object.username)
    if request.method == 'GET':
        form = AdminResetModelForm()
        return render(request, 'change.html', {'title': title, 'form': form})
    form = AdminResetModelForm(data=request.POST, instance=row_object)
    if form.is_valid():
        form.save()
        return redirect('/admin/list/')
    return render(request, 'change.html', {'form': form, 'title': title})
