from apps.communication import models
from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from settings.settings import DEBUG
from apps.admin.controller.decorator import postpone

class Email:
  def __init__(self, template_dir=None, data=None, message=None):
    #creates an email using the template and data provided
    if template_dir and data:

      subject_template = "email/%s/subject.txt" % template_dir
      text_body_template = "email/%s/text_body.txt" % template_dir
      html_body_template = "email/%s/html_body.html" % template_dir

      #plaintext_context = Context(autoescape=False)
      context = {'data':data}

      self.subject = render_to_string(subject_template, context)
      self.text_body = render_to_string(text_body_template, context)
      self.html_body = render_to_string(html_body_template, context)

    else:
      message = message if message else 'test email body'
      self.subject = 'notification'
      self.text_body = message
      self.html_body = '<p>%s</p>' % message

  @postpone
  def sendTo(self, to): #sends the email object to the provided email or list of emails
    import threading

    #allow the function to receive a string or a list
    self.to = [to] if isinstance(to, basestring) else to

    if DEBUG: #redirect non-production emails
      self.text_body = "*STAGE* To: %s\n %s" % (','.join(self.to), self.text_body)
      self.html_body = "<h2>*STAGE* To: %s</h2> %s" % (','.join(self.to), self.html_body)
      self.to = ['dev+test@theanou.com']

    try:
      self.mail = EmailMultiAlternatives(
                    subject     = self.subject,
                    body        = self.text_body,
                    from_email  = "hello@theanou.com",
                    to          = self.to
                  )
      #sendgrid settings automatically bcc dump@theanou.com on every email
      self.mail.attach_alternative(self.html_body, "text/html")
      self.mail.send()

    except Exception as e:
      return "error: " + str(e)
    else:
      return self.save()

  def save(self):
    try:
      email = models.Email(
        from_address  = self.mail.from_email,
        to_address    = ','.join(self.mail.to),
        subject       = self.mail.subject,
        text_body     = self.mail.body,
        html_body     = self.mail.alternatives[0][0]
      )
    except Exception as e:
      return "error: " + str(e)
    else:
      email.save()
      return True
