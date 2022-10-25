from app01 import models
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django import forms
from app01.utils.bootstrap import BootStrapModelForm


class UserModelForm(BootStrapModelForm):
    name = forms.CharField(
        min_length=3,
        label="用户名111",
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    class Meta:
        model = models.UserInfo
        fields = ['name', 'password', 'age', 'account', 'create_time', 'gender', 'depart']


class PrettyModelForm(BootStrapModelForm):
    # 验证  方式1-给字段加正则
    mobile = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1\d{10}$', '数字必须以1开头')],
    )

    class Meta:
        model = models.PrettyNum
        # __all__  表示所有字段
        # fields = '__all__'
        fields = ['mobile', 'price', 'level', 'status']

        # 除去 level 字段
        # exclude = ['level']

    # 验证 方式2-钩子方法
    def clean_mobile(self):
        txt_mobile = self.cleaned_data['mobile']
        # if len(txt_mobile)!= 11:
        #     #验证不通过
        #     raise ValidationError('格式错误')
        # #验证通过，用户输入的值返回
        # return txt_mobile
        exists = models.PrettyNum.objects.filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError('手机号已存在')
        return txt_mobile


class PrettyEditModelForm(BootStrapModelForm):
    # 验证  方式1-给字段加正则
    mobile = forms.CharField(
        label='手机号',
        validators=[RegexValidator(r'^1\d{10}$', '数字必须以1开头')],
    )

    # 手机号不可以修改
    # mobile = forms.CharField(disabled=True, label='手机号')

    class Meta:
        model = models.PrettyNum
        fields = ['mobile', 'price', 'level', 'status']

    def clean_mobile(self):
        # 当前编辑的哪一行的ID
        # self.instance.pk

        txt_mobile = self.cleaned_data['mobile']
        exists = models.PrettyNum.objects.exclude(id=self.instance.pk).filter(mobile=txt_mobile).exists()
        if exists:
            raise ValidationError('手机号已存在')
        return txt_mobile
