import logging
import os
from fabric.operations import local
from scrapyd_api import ScrapydAPI
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import DeployParams

logger = logging.getLogger()


def pull(request):
    """
    更新服务器代码
    http://localhost:8000/api/v1/deploy/pull?addr=http://10.0.4.150:6800
    """
    addr = request.GET['addr']
    deployer = DeployParams.objects.filter(deploy_scrapyd_addr=addr).first()
    if deployer:
        fab_cmd = "fab -f app_deploy/tools/fabfile.py " \
                  f"-H '{deployer.fabric_host}' " \
                  f"-u {deployer.fabric_user} " \
                  f"-i  {deployer.fabric_ssh_key_path} " \
                  f"pull:{deployer.fabric_code_path}"
        logger.info(fab_cmd)
        out = local(command=fab_cmd, capture=True)
        print(out)
        if 'Done.' in out and 'Abort' not in out:
            return JsonResponse({'status': 0, 'msg': '代码更新成功！'}, safe=False)
        else:
            return JsonResponse({'status': -1, 'msg': '代码更新失败哦～'}, safe=False)
    else:
        logger.warning('代码名称不存在！')
        return JsonResponse({'status': -1, 'msg': '找不到哦～'}, safe=False)


def add_deploy():
    pass


def get_deploy():
    pass
