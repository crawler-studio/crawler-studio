from django.test import TestCase

# Create your tests here.



import re

def to_snake_case(x):
    """转下划线命名"""
    return re.sub('(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])', '_\g<0>', x).upper()


print(to_snake_case('sourceID'))