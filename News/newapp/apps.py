from django.apps import AppConfig
import redis


class NewappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newapp'


    def ready(self):
        import newapp.signals

red = redis.Redis(
    host='redis-18862.c8.us-east-1-4.ec2.cloud.redislabs.com',
    port=18862,
    password='41VL6MlC4tmYaTbaDmWdsNsbihkJX2Kw'
)
