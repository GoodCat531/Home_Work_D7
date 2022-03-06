import logging
from datetime import datetime

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution

from datetime import datetime

from newapp.models import Category, Post
from newapp.tasks import send_mail_for_sub_every_week


logger = logging.getLogger(__name__)


def news_sender():
    print()
    print()
    print()
    print()
    print('===================================ПРОВЕРКА СЕНДЕРА===================================')
    print()
    print()

    for category in Category.objects.all():
        news_from_each_category = []
        week_number_last = datetime.now().isocalendar()[1] - 1

        for news in Post.objects.filter(category_id=category.id,
                                        dateCreation__week=week_number_last).values('pk',
                                                                                    'title',
                                                                                    'dateCreation',
                                                                                    'category_id__name'):
            date_format = news.get("dateCreation").strftime("%m/%d/%Y")
            new = (f' http://127.0.0.1:8000/news/{news.get("pk")}, {news.get("title")}, '
                   f'Категория: {news.get("category_id__name")}, Дата создания: {date_format}')
            news_from_each_category.append(new)


        print()
        print('+++++++++++++++++++++++++++++', category.name, '++++++++++++++++++++++++++++++++++++++++++++')
        print()
        print("Письма будут отправлены подписчикам категории:", category.name, '( id:', category.id, ')')

        subscribers = category.subscribers.all()
        print('по следующим адресам email: ')
        for qaz in subscribers:
            print(qaz.email)

        print()
        print()

        for subscriber in subscribers:
            print('____________________________', subscriber.email, '___________________________________')
            print()
            print('Письмо, отправленное по адресу: ', subscriber.email)
            html_content = render_to_string(
                'mail_sender.html', {'user': subscriber,
                                     'text': news_from_each_category,
                                     'category_name': category.name,
                                     'week_number_last': week_number_last})

            sub_username = subscriber.username
            sub_useremail = subscriber.email

            send_mail_for_sub_every_week(sub_username, sub_useremail, html_content)

            print()

            print(html_content)


    def delete_old_job_executions(max_age=604_800):
        DjangoJobExecution.objects.delete_old_job_executions(max_age)

    class Command(BaseCommand):
        help = "Runs apscheduler."

        def handle(self, *args, **options):
            scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
            scheduler.add_jobstore(DjangoJobStore(), "default")


            scheduler.add_job(
                news_sender,

                trigger=CronTrigger(second="*/10"),


                id="news_sender",
                max_instances=1,
                replace_existing=True,
            )
            logger.info("Добавлена работка 'news_sender'.")

            scheduler.add_job(
                delete_old_job_executions,
                trigger=CronTrigger(
                    day_of_week="mon", hour="00", minute="00"
                ),
                id="delete_old_job_executions",
                max_instances=1,
                replace_existing=True,
            )
            logger.info(
                "Added weekly job: 'delete_old_job_executions'."
            )

            try:
                logger.info("Задачник запущен")
                print('Задачник запущен')
                scheduler.start()
            except KeyboardInterrupt:
                logger.info("Задачник остановлен")
                scheduler.shutdown()
                print('Задачник остановлен')
                logger.info("Задачник остановлен успешно!")
