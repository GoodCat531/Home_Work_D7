from django.apps import AppConfig
import redis


class NewspostConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'newspost'



red = redis.Redis(
    host='redis-18862.c8.us-east-1-4.ec2.cloud.redislabs.com',
    port=18862,
    password='41VL6MlC4tmYaTbaDmWdsNsbihkJX2Kw'
)
