"""
@Description: 使用fabric更新服务器上的代码
@Usage: 
@Author: liuxianglong
@Date: 2021/11/13 下午2:28
"""
import logging
from fabric.api import *

logger = logging.getLogger(__name__)


def pull(code_path):
    with cd(code_path):
        run('git checkout Pipfile')
        run('git checkout Pipfile.lock')
        run('git pull')


def install(code_path):
    with cd(code_path):
        run('pipenv install')
