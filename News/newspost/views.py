import instance
from django.http import HttpResponse
from django.views import View

from .tasks import hello, printer, send_mail_for_sub_test


class IndexView(View):
    def get(self, request):
        # printer.apply_async([10], countdown=10)
        # hello.delay()
        send_mail_for_sub_test.delay()
        return HttpResponse('Hello!')
