# -*- coding: utf-8 -*-

from .environment import prepare_environment
import os
__version__ = "0.1.4"

def _main(**kwargs):
    # pylint: disable=unused-variable
    import sys
    from django.core.management import execute_from_command_line
    prepare_environment(**kwargs)
    execute_from_command_line(sys.argv)


def get_app(**kwargs):
    """
    polemarch tên mo-dun main ,được sử dụng làm prefix tự động gen task nam
    
    
    :param kwargs: 
    :return: 
    """
    from celery import Celery
    prepare_environment(**kwargs)
    celery_app = Celery('polemarch')

    # tải config từ setting, dấu hiệu nhận biết là 'CELERY'
    celery_app.config_from_object('django.conf:settings', namespace='CELERY')
    # tải tất cả các module task từ đăng ký djanfgo app
    celery_app.autodiscover_tasks()
    return celery_app
