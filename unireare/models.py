import os
from uuid import uuid4

from django.conf import settings
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils.deconstruct import deconstructible

from .managers import UserManager


@deconstructible
class PathAndRename(object):
    def __init__(self, sub_path):
        self.path = sub_path

    def __call__(self, instance, filename):
        ext = filename.split('.')[-1]
        if instance.pk:
            filename = '{}.{}'.format('{}_{}'.format(instance.pk, uuid4().hex), ext)
        else:
            filename = '{}.{}'.format(uuid4().hex, ext)
        return os.path.join(self.path, filename)


# 用户
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField('邮箱', unique=True)
    nickname = models.CharField('昵称', max_length=16)
    school = models.CharField('学校', max_length=16)
    major = models.CharField('专业', max_length=16)
    tel = models.CharField('电话', max_length=16)
    motto = models.CharField('个性签名', max_length=1024, default='这个用户很懒，什么都没有留下。')
    balance = models.IntegerField('余额', default=0)
    earnings = models.IntegerField('收益', default=0)
    is_vip = models.BooleanField('VIP', default=False)
    following_amount = models.IntegerField('关注量', default=0)
    follower_amount = models.IntegerField('粉丝量', default=0)
    avatar = models.ImageField('头像', upload_to=PathAndRename('avatars'), null=True, blank=True)
    registered_at = models.DateTimeField('注册时间', auto_now_add=True)
    is_active = models.BooleanField('是否激活', default=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'

    def get_full_name(self):
        return self.nickname

    def get_short_name(self):
        return self.nickname

    def to_dict(self, lite=True):
        if lite:
            return {
                'id': self.pk,
                'nickname': self.nickname,
                'school': self.school,
                'major': self.major,
                'motto': self.motto,
                'following_amount': self.following_amount,
                'follower_amount': self.follower_amount,
                'is_vip': self.is_vip,
                'avatar': settings.MEDIA_URL + (self.avatar.name if self.avatar.name else 'avatars/default.png'),
                'registered_at': self.registered_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        return {
            'id': self.pk,
            'email': self.email,
            'nickname': self.nickname,
            'school': self.school,
            'major': self.major,
            'tel': self.tel,
            'motto': self.motto,
            'balance': self.balance,
            'earnings': self.earnings,
            'following_amount': self.following_amount,
            'follower_amount': self.follower_amount,
            'is_vip': self.is_vip,
            'is_superuser': self.is_superuser,
            'avatar': settings.MEDIA_URL + (self.avatar.name if self.avatar.name else 'avatars/default.png'),
            'registered_at': self.registered_at.strftime("%Y-%m-%d %H:%M:%S")
        }


# 邮箱验证码
class EmailCode(models.Model):
    email = models.EmailField('邮箱', primary_key=True)
    code = models.CharField('验证码', max_length=6)
    created_at = models.DateTimeField('生成时间', auto_now=True)


# 图片
class Image(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField('图片', upload_to=PathAndRename('images'))
    uploaded_at = models.DateTimeField('上传时间', auto_now_add=True)


# 站内信
class Message(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_user', on_delete=models.CASCADE)
    content = models.TextField('内容')
    is_read = models.BooleanField('是否已读', default=False)
    sended_at = models.DateTimeField('关注时间', auto_now_add=True)

    def to_dict(self, lite=True):
        if lite:
            return {
                'id': self.id,
                'user': self.from_user.to_dict(),
                'is_read': self.is_read,
                'sended_at': self.sended_at.strftime("%Y-%m-%d %H:%M:%S")
            }
        return {
            'id': self.id,
            'user': self.from_user.to_dict(),
            'content': self.content,
            'is_read': self.is_read,
            'sended_at': self.sended_at.strftime("%Y-%m-%d %H:%M:%S")
        }


# 关注
class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    followed_at = models.DateTimeField('关注时间', auto_now_add=True)


# 科目
class Subject(models.Model):
    name = models.CharField('科目名称', max_length=16)
    note_amount = models.IntegerField('笔记数量', default=0)
    added_at = models.DateTimeField('添加时间', auto_now_add=True)
    last_updated_at = models.DateTimeField('最后更新时间', auto_now=True)
    defunct = models.BooleanField('已弃用', default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'added_at': self.added_at.strftime("%Y-%m-%d %H:%M:%S"),
            'last_updated_at': self.last_updated_at.strftime("%Y-%m-%d %H:%M:%S"),
        }


# 笔记
class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    title = models.CharField('标题', max_length=64)
    content = models.TextField('内容')
    reading_amount = models.IntegerField('阅读量', default=0)
    liking_amount = models.IntegerField('点赞量', default=0)
    collect_amount = models.IntegerField('收藏量', default=0)
    purchase_amount = models.IntegerField('购买量', default=0)
    is_free = models.BooleanField('是否免费', default=True)
    price = models.IntegerField('价格')
    added_at = models.DateTimeField('添加时间', auto_now_add=True)
    last_updated_at = models.DateTimeField('最后更新时间', auto_now=True)
    defunct = models.BooleanField('已弃用', default=False)


# 评论
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    content = models.TextField('内容')
    added_at = models.DateTimeField('添加时间', auto_now_add=True)
    last_updated_at = models.DateTimeField('最后更新时间', auto_now=True)
    defunct = models.BooleanField('已弃用', default=False)


# 点赞
class Liked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    liked_at = models.DateTimeField('点赞时间', auto_now_add=True)


# 收藏
class Collection(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    collected_at = models.DateTimeField('收藏时间', auto_now_add=True)


# 订单
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    added_at = models.DateTimeField('添加时间', auto_now_add=True)


# 购买
class Purchased(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField('购买时间', auto_now_add=True)


# 公告
class Announcement(models.Model):
    content = models.TextField('内容')
    added_at = models.DateTimeField('添加时间', auto_now_add=True)
    last_updated_at = models.DateTimeField('最后更新时间', auto_now=True)
    defunct = models.BooleanField('已弃用', default=False)
