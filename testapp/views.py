import os
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

# from django.core import send_mail, send_mass_mail
from django.core.mail import EmailMessage, get_connection, send_mail
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from samplesite.settings import BASE_DIR
from testapp.forms import ImgForm

FILES_ROOT = BASE_DIR / 'files'


def index(request):

    if 'counter' in request.COOKIES:
        print('COOKIES: counter =', request.COOKIES['counter'])
        cnt = int(request.COOKIES['counter']) + 1
    else:
        cnt = 1


    if 'counter' in request.sessions:
        print('SESSION: counter =', request.sessions['counter'])
        cnt = int(request.sessions['counter']) + 1
    else:
        cnt = 1

    imgs = []

    for entry in os.scandir(FILES_ROOT):
        imgs.append(os.path.basename(entry))

    context = {'imgs': imgs}
    response = render(request, 'testapp/index.html', context)
    response.set_cookie('counter', cnt)
    response.sessions['counter'] = cnt

    return response


def get(request, filename):
    fn = os.path.join(FILES_ROOT, filename)
    return FileResponse(open(fn, 'rb'), context_type='application/octet-stream')


def add(request):
    if request.method == 'POST':
        form = ImgForm(request.POST, request.FILES)
        if form.is_valid():
            upload_file = request.FILES['img']
            fn = '%s%s' % (datetime.now().timestamp(),
                           os.path.splitext(upload_file.name)[1])
            fn = os.path.join(FILES_ROOT, fn)
            with open(fn, 'wb+') as destination:
                for chunk in upload_file.chunks():
                    destination.write(chunk)
            form.save()
            return redirect('testapp:index')
    else:
        form = ImgForm()

    context = {'form': form}
    return render(request, 'testapp/add.html', context)


def test_cookie(request):
    if request.method == 'POST':
        if request.session.test_cookie_worked():
            request.session.delete_test_cookie()
    else:
        pass

    request.session.set_test_cookie()
    return render(request, 'testapp/test_cookie.html')


def test_email(request):
    # em = EmailMessage(subject='Test', body='Test', to=['user@supersite.ru'])
    # em.send()
    #
    # em = EmailMessage(subject='Ваш новый пароль',
    #                   body='Ваш новый пароль находится во вложении',
    #                   attachments=[('password.txt', '1234567890', 'text/plain')],
    #                   to=['user@supersite.ru'])
    # em.attach_file(r'requirements.txt')
    # em.send()
    #
    # context = {'user': 'vasya_lox'}
    # s = render_to_string('email/letter.txt', context)
    # em = EmailMessage(subject='Оповещение', body=s, to=['user@supersite.ru'])
    # em.send()

    con = get_connection()
    con.open()

    email1 = EmailMessage(..., connection=con)
    email1.send()
    email2 = EmailMessage(..., connection=con)
    email2.send()
    email3 = EmailMessage(..., connection=con)
    email3.send()

    con.close()

    email1 = EmailMessage(...)
    email2 = EmailMessage(...)
    email3 = EmailMessage(...)

    con.send_message([email1, email2, email3])
    con.close()

    #Высокоуровневый
    # send_mail('Test email', 'Test!!!', 'webmaster@localhost', ['user@othersite.kz'],
    #           html_message='<h1>Test!!!</h1>')
    #
    # msg1 = ('Подписка', 'Подтвердите, пожалуйста, подпиську', 'subscribe@supersite.kz',
    #         ['user@othersite.kz', 'user2@thirdsite.kz']),
    # msg2 = ('Подписка', 'Поздравляем, ваша подписька подтверждена', 'subscribe@supersite.kz',
    #         ['megauser@othersite.kz'])
    # send_mass_mail((msg1, msg2))


# def practice_email(message):
#     # em = EmailMessage(subject='Приветсвие', body=f'Доброго времени суток, дружище!', to=['ustricus@gmail.com'])
#     # em.send()
#
#     sender = "ustricus@gmail.com"
#     password = os.getenv("EMAIL PASSWORD")
#
#     server = smtplib.SMTP('smtp.gmail.com', 587)
#     server.starttls()
#
#     try:
#         server.login(sender, password)
#         msg = MIMEText(message)
#         msg["Subject"] = "CLICK ME PLEASE!"
#         server.sendmail(sender, password, msg.as_string())
#
#         return "The message is sent."
#     except Exception as _ex:
#         return f"{_ex}\nCheck your login or password please!"
#
#
# def main():
#     message = input("Enter your message:")
#     print(practice_email(message=message))
#
#
# if __name__ == '__main__':
#     main()

def send_test_email(request):
    send_mail(
        'Тема: отправка электронных писем',
        'Это тестовое сообщение для проверки их отправки',
        'TestEmail@gmail.com',  # Отправитель
        ['TestEmail2@example.com'],  # Получатель
        fail_silently=False,
    )
    return HttpResponse("Письмо отправлено успешно.")
