import logging

from django.db import models
from django.core.exceptions import MultipleObjectsReturned

logger = logging.getLogger(__name__)


def get_from_db(search_by: str):
    try:
        return Setting.objects.get(controller_name=search_by)
    except Setting.DoesNotExist:
        logger.error(f'Object requested from db: {search_by} does not exist in db')
        return None


def update_or_create(search_by: str, defaults: dict):
    try:
        obj, created = Setting.objects.update_or_create(
            controller_name=search_by,
            defaults=defaults
        )
        obj.save()

        if created:
            logger.info(f'{search_by} controller object was created in db')
        else:
            logger.info(f'{search_by} controller object was updated in db')
        return True
    except MultipleObjectsReturned:
        logger.error(f'Can not update {search_by}.There are several object in db by that key.')
        return False


# Create your models here.
class Setting(models.Model):
    controller_name = models.CharField(max_length=40, unique=True)
    label = models.CharField(max_length=100)
    value = models.IntegerField(default=20)
