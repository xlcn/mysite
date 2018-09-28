from django.shortcuts import render
from django.shortcuts import redirect
from .models import User, ConfirmString
from .forms import UserForm, RegisterForm
import hashlib
from datetime import datetime, timedelta
from django.conf import settings


def index(request):
    pass
    return render(request, 'login/index.html')


def login(request):
    if request.session.get('is_login'):
        return redirect('/index/')
    if request.method == 'POST':
        login_form = UserForm(request.POST)
        message = '请检查填写的内容'
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(name=username)
                if not user.has_confirmed:
                    message = '请先进行邮箱确认'
                    return render(request, 'login/login.html', locals())
                if hash_code(password) == user.password:
                    # set session
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = '密码不正确'
            except:
                message = '用户不存在'
        return render(request, 'login/login.html', locals())
    login_form = UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login'):
        return redirect('/index/')

    if request.method == 'POST':
        register_form = RegisterForm(request.POST)
        message = '请检查填写的内容'
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']

            if password1 != password2:
                message = '两次输入的密码不一致'
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user.exists():
                    message = '用户名重复， 需要重新选择'
                    return render(request, 'login/register.html', locals())
                same_email_user = User.objects.filter(email=email)
                if same_email_user.exists():
                    message = '邮箱重复, 需要重新选择'
                    return render(request, 'login/register.html', locals())

                # all over to save user
                new_user = User()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()

                # generate confirm code and send email
                code = make_confirm_string(new_user)
                send_email(email, code=code)

                return redirect('/login/')

    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())


def logout(request):
    if request.session.get('is_login'):
        request.session.flush()
    return redirect('/index/')


def user_confirm(request):
    code = request.GET.get('code')
    message = ''
    try:
        confirm = ConfirmString.objects.get(code=code)
    except:
        message = '无效的确认请求'
        return render(request, 'login/confirm.html', locals())

    c_time = confirm.c_time
    now = datetime.utcnow() + timedelta(hours=8)
    if now > (c_time + timedelta(days=settings.CONFIRM_DAYS)):
        confirm.user.delete()
        message = '邮件已经过期，请重新注册'
        return render(request, 'login/confirm.html', locals())
    else:
        confirm.user.has_confirmed = True
        confirm.user.save(update_fields=['has_confirmed'])
        confirm.delete()
        message = '感谢确认， 请使用帐号登录'
        return render(request, 'login/confirm.html', locals())


def hash_code(s, salt='mysite'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # should be byte
    return h.hexdigest()


def make_confirm_string(user):
    now = (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d %H:%M:%S')
    code = hash_code(user.name, now)
    ConfirmString.objects.create(code=code, user=user)
    return code


def send_email(email, code):
    from django.core.mail import send_mail
    subject = '登录注册demo注册确认'
    confirm_days = settings.CONFIRM_DAYS
    confirm_url = 'http://{}/confirm?code={}'.format('127.0.0.1:8000', code)
    text_content = '感谢注册，请复制此链接 {} 到地址栏确认注册完成，此链接 {} 天之后过期, 非本人注册可以忽略'.format(confirm_url, confirm_days)
    html_content = '''
                    <p>感谢注册<a href="http://{}/confirm/?code={}" target=blank>注册确认</a>，</p>
                    <p>请点击站点链接完成注册确认！</p>
                    <p>此链接有效期为{}天！</p>
                    '''.format('127.0.0.1:8000', code, confirm_days)
    send_mail(subject=subject,
              message=text_content,
              html_message=html_content,
              from_email=settings.EMAIL_HOST_USER,
              recipient_list=[email])
