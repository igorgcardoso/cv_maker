from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .signals import cv_generated


@receiver(cv_generated)
def send_cv_by_email(sender, cv, *args, **kwargs):
  # with get_connection() as connection:
  #   email = EmailMessage(
  #     subject=_('Your cv is awaiting for you'),
  #     body='',
  #     from_email='igorgcardoso@live.com',
  #     to=[sender.email],
  #     connection=connection
  #   )
  #   for arg in cv:
  #     email.attach_file(arg, 'application/pdf')
  #   email.send()
  pass
