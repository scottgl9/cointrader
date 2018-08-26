from trader.config import EMAIL_USER, EMAIL_PASS
import smtplib

class Email(object):
    def __init__(self):
        pass

    def send(self, subject, text):
        if EMAIL_USER == None or EMAIL_PASS == None:
            return
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        msg = 'Subject: {}\n\n{}'.format(subject, text)
        server.sendmail(EMAIL_USER, EMAIL_USER, msg)
        server.quit()
