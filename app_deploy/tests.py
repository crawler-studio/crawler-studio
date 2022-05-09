import time

from django.test import TestCase

# Create your tests here.
import subprocess


from fabric.operations import local

cmd = "fab -f app_deploy/tools/fabfile.py -H '10.0.4.150' -u root -i  app_deploy/tools/id_rsa.pub pull:/root/platform_data"
out = local(command=cmd, capture=True)
print(out)