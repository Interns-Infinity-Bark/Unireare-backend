from django.urls import path

from . import views

urlpatterns = [
    path('login', views.user_login),  # POST 登录
    path('logout', views.user_logout),  # GET 注销
    path('session', views.session),  # GET 获取在线状态以及个人信息
    path('register', views.register),  # POST 注册
    path('register_email_code', views.register_email_code),  # POST 发送注册验证码
    path('reset_password', views.reset_password),  # POST 重置密码
    path('reset_password_email_code', views.reset_password_email_code),  # POST 发送重置密码验证码
    path('user_info/<int:pk>', views.user_info),  # GET 获取特定用户信息
    path('disable_user/<int:pk>', views.disable_user),  # GET 封禁特定用户(管理员)
    path('enable_user/<int:pk>', views.enable_user),  # GET 激活特定用户(管理员)
    path('modify_user_info', views.modify_user_info),  # POST 修改用户信息
    path('modify_user_motto', views.modify_user_motto),  # POST 修改个性签名
    path('modify_password', views.modify_password),  # POST 修改密码
    path('upload_avatar', views.upload_avatar),  # POST 上传头像
    path('upload_image', views.upload_image),  # POST 上传图片
    path('send_message', views.send_message),  # POST 发送站内信
    path('message_list', views.message_list),  # GET 获取站内信列表 可选参数: page(int)
    path('message/<int:pk>', views.message_view),  # GET 站内信详情
    path('follow', views.follow),  # POST 关注/取消关注
    path('following', views.following),  # GET 我关注的 可选参数: page(int)
    path('followers', views.followers),  # GET 关注我的 可选参数: page(int)
    path('subject_list', views.subject_list),  # GET 获取科目列表 可选参数: name(str), page(int)
    path('add_subject', views.add_subject),  # POST 添加科目(管理员)
    path('modify_subject/<int:pk>', views.modify_subject),  # POST 修改特定科目名称(管理员)
    path('delete_subject/<int:pk>', views.delete_subject),  # GET 删除特定科目(管理员)
    path('note_list', views.note_list),  # GET 获取笔记列表 可选参数: subject(int), title(str), user(int), page(int)
    path('draft_list', views.draft_list),  # GET 获取草稿列表 可选参数: subject(int), title(str), page(int)
    path('note/<int:pk>', views.note_view),  # GET 查看笔记详情
    path('add_note', views.add_note),  # POST 添加笔记/草稿
    path('modify_note/<int:pk>', views.modify_note),  # POST 修改特定笔记/草稿
    path('delete_note/<int:pk>', views.delete_note),  # GET 删除特定笔记(管理员)/草稿
    path('comment/<int:pk>', views.comment_view),  # GET 查看特定评论
    path('add_comment', views.add_comment),  # POST 添加评论
    path('modify_comment/<int:pk>', views.modify_comment),  # POST 修改特定评论(评论者/管理员)
    path('delete_comment/<int:pk>', views.delete_comment),  # GET 删除特定评论(评论者/管理员)
]
