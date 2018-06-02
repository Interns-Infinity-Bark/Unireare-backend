from django import forms


class LoginForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
    )
    password = forms.CharField(
        label='密码',
        max_length=64,
    )


class RegisterForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
    )
    code = forms.CharField(
        label='验证码',
        max_length=6,
    )
    password = forms.CharField(
        label='密码',
        max_length=64,
    )
    confirm_password = forms.CharField(
        label='确认密码',
        max_length=64,
    )
    nickname = forms.CharField(
        label='昵称',
        max_length=16,
    )


class EmailCodeForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
    )


class ResetPasswordForm(forms.Form):
    email = forms.EmailField(
        label='邮箱',
    )
    code = forms.CharField(
        label='验证码',
        max_length=6,
    )
    password = forms.CharField(
        label='密码',
        max_length=64,
    )
    confirm_password = forms.CharField(
        label='确认密码',
        max_length=64,
    )


class ModifyUserInfoForm(forms.Form):
    nickname = forms.CharField(
        label='昵称',
        max_length=16,
    )
    school = forms.CharField(
        label='学校',
        max_length=16,
    )
    major = forms.CharField(
        label='专业',
        max_length=16,
    )
    tel = forms.CharField(
        label='电话',
        max_length=16,
    )


class ModifyUserMottoForm(forms.Form):
    motto = forms.CharField(
        label='个性签名',
        max_length=1024,
    )


class ModifyPasswordForm(forms.Form):
    old_password = forms.CharField(
        label='原密码',
        max_length=64,
    )
    password = forms.CharField(
        label='新密码',
        max_length=64,
    )
    confirm_password = forms.CharField(
        label='确认密码',
        max_length=64,
    )


class UploadImageForm(forms.Form):
    image = forms.ImageField()


class MessageForm(forms.Form):
    to_user = forms.IntegerField(
        label='接收方',
    )
    content = forms.CharField(
        label='消息内容',
    )


class FollowForm(forms.Form):
    following = forms.IntegerField(
        label='被操作用户',
    )


class SubjectForm(forms.Form):
    name = forms.CharField(
        label='科目名称',
        max_length=16,
    )
