import datetime
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from django.core.paginator import Paginator
from django.http import JsonResponse

from .forms import *
from .models import *
from .send_mail import AliyunMailSender

User = get_user_model()

email_code_subject = '【爱分享】您的验证码'
email_code_content = '''<p>尊敬的用户：</p>
<p>欢迎使用爱分享服务，您的验证码为：<strong style="font-size: 150%%;">%d</strong></p>
<p>验证码 24 小时内有效，请尽快使用</p>
<p><br/></p>
<p>爱分享团队</p>'''


def ajax(status, msg, data=None, extra=None):
    json_data = {
        'status': status,
        'msg': msg,
    }
    if data is not None:
        json_data['data'] = data
    if extra is not None:
        for item in extra:
            json_data[item] = extra[item]
    json_resp = JsonResponse(json_data)
    json_resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    json_resp['Pragma'] = 'no-cache'
    json_resp['Expires'] = '0'
    return json_resp


def index(request):
    pass
    return ajax('success', '', {
        'title': 'bLue',
        'content': 'UMR',
        'text': 'Ninaye'
    })


def user_login(request):
    if request.user.is_authenticated:
        return ajax('error', '已登录')
    form = LoginForm(request.POST)
    if form.is_valid():
        user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
        if user is not None and user.is_active:
            login(request, user)
            return ajax('success', '登录成功')
        else:
            return ajax('error', '邮箱或密码错误')
    else:
        return ajax('error', '', form.errors.get_json_data())


def user_logout(request):
    logout(request)
    return ajax('success', '注销成功')


def session(request):
    if request.user.is_authenticated:
        return ajax('success', '', {
            'is_logged_in': True,
            'user': request.user.to_dict(lite=False)
        })
    else:
        return ajax('success', '', {
            'is_logged_in': False,
        })


def register(request):
    if request.user.is_authenticated:
        return ajax('error', '已登录')
    form = RegisterForm(request.POST)
    if form.is_valid():
        if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
            return ajax('error', '', {
                'confirm_password': [{
                    'message': '两次输入的密码不一致',
                    'code': 'invalid',
                }]
            })
        res = User.objects.filter(email=form.cleaned_data['email'])
        if len(res) > 0:
            return ajax('error', '', {
                'email': [{
                    'message': '邮箱已被使用',
                    'code': 'invalid',
                }]
            })
        res = EmailCode.objects.filter(email=form.cleaned_data['email'], code=form.cleaned_data['code'])
        if len(res) == 0:
            return ajax('error', '', {
                'code': [{
                    'message': '邮箱验证码错误',
                    'code': 'invalid',
                }]
            })
        if (datetime.datetime.now() - res[0].created_at).total_seconds() > 3600 * 24:
            return ajax('error', '', {
                'code': [{
                    'message': '邮箱验证码已失效，请重新发送',
                    'code': 'invalid',
                }]
            })
        EmailCode(email=form.cleaned_data['email']).delete()
        user = User.objects.create_user(email=form.cleaned_data['email'], password=form.cleaned_data['password'],
                                        nickname=form.cleaned_data['nickname'])
        login(request, user)
        return ajax('success', '注册成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def register_email_code(request):
    if request.user.is_authenticated:
        return ajax('error', '已登录')
    form = EmailCodeForm(request.POST)
    if form.is_valid():
        res = User.objects.filter(email=form.cleaned_data['email'])
        if len(res) > 0:
            return ajax('error', '', {
                'email': [{
                    'message': '邮箱已被使用',
                    'code': 'invalid',
                }]
            })
        ecode = EmailCode(email=form.cleaned_data['email'], code=random.randint(100000, 999999))
        ecode.save()
        aliyun_mail_sender = AliyunMailSender(settings.MAIL_ACCESS_KEY, settings.MAIL_ACCESS_SECRET)
        aliyun_mail_sender.single_send_mail(settings.MAIL_ACCOUNT, '爱分享', ecode.email, email_code_subject,
                                            email_code_content % ecode.code)
        return ajax('success', '验证码已发送，请查收邮件')
    else:
        return ajax('error', '', form.errors.get_json_data())


def reset_password(request):
    if request.user.is_authenticated:
        return ajax('error', '已登录')
    form = ResetPasswordForm(request.POST)
    if form.is_valid():
        if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
            return ajax('error', '', {
                'confirm_password': [{
                    'message': '两次输入的密码不一致',
                    'code': 'invalid',
                }]
            })
        users = User.objects.filter(email=form.cleaned_data['email'])
        if len(users) == 0:
            return ajax('error', '', {
                'email': [{
                    'message': '电子邮箱不存在',
                    'code': 'invalid',
                }]
            })
        res = EmailCode.objects.filter(email=form.cleaned_data['email'], code=form.cleaned_data['code'])
        if len(res) == 0:
            return ajax('error', '', {
                'code': [{
                    'message': '邮箱验证码错误',
                    'code': 'invalid',
                }]
            })
        if (datetime.datetime.now() - res[0].created_at).total_seconds() > 3600 * 24:
            return ajax('error', '', {
                'code': [{
                    'message': '邮箱验证码已失效，请重新发送',
                    'code': 'invalid',
                }]
            })
        EmailCode(email=form.cleaned_data['email']).delete()
        user = users[0]
        user.set_password(form.cleaned_data['password'])
        user.save()
        return ajax('success', '密码重置成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def reset_password_email_code(request):
    if request.user.is_authenticated:
        return ajax('error', '已登录')
    form = EmailCodeForm(request.POST)
    if form.is_valid():
        res = User.objects.filter(email=form.cleaned_data['email'])
        if len(res) == 0:
            return ajax('error', '', {
                'email': [{
                    'message': '邮箱不存在',
                    'code': 'invalid',
                }]
            })
        ecode = EmailCode(email=form.cleaned_data['email'], code=random.randint(100000, 999999))
        ecode.save()
        aliyun_mail_sender = AliyunMailSender(settings.MAIL_ACCESS_KEY, settings.MAIL_ACCESS_SECRET)
        aliyun_mail_sender.single_send_mail(settings.MAIL_ACCOUNT, '爱分享', ecode.email, email_code_subject,
                                            email_code_content % ecode.code)
        return ajax('success', '验证码已发送，请查收邮件')
    else:
        return ajax('error', '', form.errors.get_json_data())


def user_info(request, pk):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    users = User.objects.filter(pk=pk, is_active=True)
    if len(users) == 0:
        return ajax('error', '用户不存在或未激活')
    return ajax('success', '', users[0].to_dict(lite=request.user.pk != pk))


def disable_user(request, pk):
    if not request.user.is_superuser:
        return ajax('error', '无权访问该页面')
    users = User.objects.filter(pk=pk, is_active=True)
    if len(users) == 0:
        return ajax('error', '用户不存在或未激活')
    if users[0].is_superuser:
        return ajax('error', '无权封禁此用户')
    users[0].is_active = False
    users[0].save()
    return ajax('success', '封禁用户成功')


def enable_user(request, pk):
    if not request.user.is_superuser:
        return ajax('error', '无权访问该页面')
    users = User.objects.filter(pk=pk, is_active=False)
    if len(users) == 0:
        return ajax('error', '用户不存在或已激活')
    if users[0].is_superuser:
        return ajax('error', '无权激活此用户')
    users[0].is_active = True
    users[0].save()
    return ajax('success', '激活用户成功')


def modify_user_info(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    form = ModifyUserInfoForm(request.POST)
    if form.is_valid():
        user = request.user
        user.nickname = form.cleaned_data['nickname']
        user.school = form.cleaned_data['school']
        user.major = form.cleaned_data['major']
        user.tel = form.cleaned_data['tel']
        user.save()
        return ajax('success', '修改成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def modify_user_motto(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    form = ModifyUserMottoForm(request.POST)
    if form.is_valid():
        user = request.user
        user.motto = form.cleaned_data['motto']
        user.save()
        return ajax('success', '修改成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def modify_password(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    form = ModifyPasswordForm(request.POST)
    if form.is_valid():
        user = request.user
        if form.cleaned_data['password'] != form.cleaned_data['confirm_password']:
            return ajax('error', '', {
                'confirm_password': [{
                    'message': '两次输入的密码不一致',
                    'code': 'invalid',
                }]
            })
        if not check_password(form.cleaned_data['old_password'], user.password):
            return ajax('error', '', {
                'old_password': [{
                    'message': '原密码错误',
                    'code': 'invalid',
                }]
            })
        user.set_password(form.cleaned_data['password'])
        user.save()
        login(request, user)
        return ajax('success', '密码修改成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def upload_avatar(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    form = UploadImageForm(request.POST, request.FILES)
    if form.is_valid():
        request.user.avatar = request.FILES['image']
        request.user.save()
        return ajax('success', '上传成功', {
            'avatar': settings.MEDIA_URL + request.user.avatar.name
        })
    else:
        return ajax('error', '', form.errors.get_json_data())


def upload_image(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    form = UploadImageForm(request.POST, request.FILES)
    if form.is_valid():
        img = Image(user=request.user, image=request.FILES['image'])
        img.save()
        return ajax('success', '上传成功', {
            'image': settings.MEDIA_URL + img.image.name
        })
    else:
        return ajax('error', '', form.errors.get_json_data())


def send_message(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    form = MessageForm(request.POST)
    if form.is_valid():
        users = User.objects.filter(pk=form.cleaned_data['to_user'], is_active=True)
        if len(users) == 0:
            return ajax('error', '用户不存在或未激活')
        if users[0] == request.user:
            return ajax('error', '不能给自己发送信息')
        message = Message(from_user=request.user, to_user=users[0], content=form.cleaned_data['content'])
        message.save()
        return ajax('success', '发送成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def message_list(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    messages = Message.objects.filter(to_user=request.user).order_by('-sended_at')
    if request.GET.get('page'):
        try:
            page = int(request.GET.get('page'))
        except (TypeError, ValueError):
            return ajax('error', '页码格式错误')
        paginator = Paginator(messages, 10)
        if page not in range(1, paginator.num_pages + 1):
            return ajax('error', '页码范围错误')
        messages = paginator.get_page(page)
        return ajax('success', '', {
            'page': page,
            'num_pages': messages.paginator.num_pages,
            'messages': [message.to_dict() for message in messages]
        })
    return ajax('success', '', {
        'messages': [message.to_dict() for message in messages]
    })


def message_view(request, pk):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    messages = Message.objects.filter(pk=pk)
    if len(messages) == 0:
        return ajax('error', '站内信不存在')
    if messages[0].to_user != request.user and not request.user.is_superuser:
        return ajax('error', '无权访问该页面')
    if messages[0].to_user == request.user:
        messages[0].is_read = True
        messages[0].save()
    return ajax('success', '', messages[0].to_dict(lite=False))


def follow(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    form = FollowForm(request.POST)
    if form.is_valid():
        users = User.objects.filter(pk=form.cleaned_data['following'], is_active=True)
        if len(users) == 0:
            return ajax('error', '用户不存在或未激活')
        if users[0] == request.user:
            return ajax('error', '不能关注自己')
        user = request.user
        follows = Follow.objects.filter(follower=user, following=users[0])
        if len(follows) > 0:
            user.following_amount -= 1
            user.save()
            users[0].follower_amount -= 1
            users[0].save()
            follows[0].delete()
            return ajax('success', '取消关注成功')
        user.following_amount += 1
        user.save()
        users[0].follower_amount += 1
        users[0].save()
        new_follow = Follow(follower=user, following=users[0])
        new_follow.save()
        return ajax('success', '关注成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def following(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    follows = Follow.objects.filter(follower=request.user).order_by('-followed_at')
    if request.GET.get('page'):
        try:
            page = int(request.GET.get('page'))
        except (TypeError, ValueError):
            return ajax('error', '页码格式错误')
        paginator = Paginator(follows, 10)
        if page not in range(1, paginator.num_pages + 1):
            return ajax('error', '页码范围错误')
        follows = paginator.get_page(page)
        return ajax('success', '', {
            'page': page,
            'num_pages': follows.paginator.num_pages,
            'follows': [{
                'user': follow_item.following.to_dict(),
                'followed_at': follow_item.followed_at.strftime("%Y-%m-%d %H:%M:%S")
            } for follow_item in follows]
        })
    return ajax('success', '', {
        'follows': [{
            'user': follow_item.following.to_dict(),
            'followed_at': follow_item.followed_at.strftime("%Y-%m-%d %H:%M:%S")
        } for follow_item in follows]
    })


def followers(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    follows = Follow.objects.filter(following=request.user).order_by('-followed_at')
    if request.GET.get('page'):
        try:
            page = int(request.GET.get('page'))
        except (TypeError, ValueError):
            return ajax('error', '页码格式错误')
        paginator = Paginator(follows, 10)
        if page not in range(1, paginator.num_pages + 1):
            return ajax('error', '页码范围错误')
        follows = paginator.get_page(page)
        return ajax('success', '', {
            'page': page,
            'num_pages': follows.paginator.num_pages,
            'follows': [{
                'user': follow_item.follower.to_dict(),
                'followed_at': follow_item.followed_at.strftime("%Y-%m-%d %H:%M:%S")
            } for follow_item in follows]
        })
    return ajax('success', '', {
        'follows': [{
            'user': follow_item.follower.to_dict(),
            'followed_at': follow_item.followed_at.strftime("%Y-%m-%d %H:%M:%S")
        } for follow_item in follows]
    })


def subject_list(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    subjects = Subject.objects.filter(defunct=False).order_by('-added_at')
    if request.GET.get('name'):
        subjects = subjects.filter(name__icontains=request.GET.get('name'))
    if request.GET.get('page'):
        try:
            page = int(request.GET.get('page'))
        except (TypeError, ValueError):
            return ajax('error', '页码格式错误')
        paginator = Paginator(subjects, 10)
        if page not in range(1, paginator.num_pages + 1):
            return ajax('error', '页码范围错误')
        subjects = paginator.get_page(page)
        return ajax('success', '', {
            'page': page,
            'num_pages': subjects.paginator.num_pages,
            'subjects': [subject.to_dict() for subject in subjects]
        })
    return ajax('success', '', {
        'subjects': [subject.to_dict() for subject in subjects]
    })


def add_subject(request):
    if not request.user.is_superuser:
        return ajax('error', '无权访问该页面')
    form = SubjectForm(request.POST)
    if form.is_valid():
        subjects = Subject.objects.filter(name=form.cleaned_data['name'])
        if len(subjects) > 0:
            if subjects[0].defunct:
                subjects[0].defunct = False
                subjects[0].save()
                return ajax('success', '添加成功')
            return ajax('error', '科目已存在')
        subject = Subject(name=form.cleaned_data['name'])
        subject.save()
        return ajax('success', '添加成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def modify_subject(request, pk):
    if not request.user.is_superuser:
        return ajax('error', '无权访问该页面')
    form = SubjectForm(request.POST)
    if form.is_valid():
        subjects = Subject.objects.filter(pk=pk, defunct=False)
        if len(subjects) == 0:
            return ajax('error', '科目不存在')
        subjects[0].name = form.cleaned_data['name']
        subjects[0].save()
        return ajax('success', '修改成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def delete_subject(request, pk):
    if not request.user.is_superuser:
        return ajax('error', '无权访问该页面')
    subjects = Subject.objects.filter(pk=pk, defunct=False)
    if len(subjects) == 0:
        return ajax('error', '科目不存在')
    subjects[0].defunct = True
    subjects[0].save()
    return ajax('success', '删除成功')


def note_list(request):
    pass


def note_view(request, pk):
    pass


def add_note(request):
    if not request.user.is_authenticated:
        return ajax('error', '请先登录')
    form = AddNoteForm(request.POST)
    if form.is_valid():
        subjects = Subject.objects.filter(pk=form.cleaned_data['subject'], defunct=False)
        if len(subjects) == 0:
            return ajax('error', '科目不存在')
        note = Note(user=request.user, subject=subjects[0], title=form.cleaned_data['title'],
                    content=form.cleaned_data['content'], is_free=form.cleaned_data['is_free'])
        if not note.is_free:
            if not form.cleaned_data['price']:
                return ajax('error', '', {
                    'price': [{
                        'message': '价格不能为空',
                        'code': 'invalid',
                    }]
                })
        note.price = form.cleaned_data['price']
        note.save()
        return ajax('success', '添加成功')
    else:
        return ajax('error', '', form.errors.get_json_data())


def modify_note(request, pk):
    pass


def delete_note(request, pk):
    pass
