"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/1/24 下午6:33
"""


class ItemExistedException(Exception):

    def __str__(self):
        return '项目已存在'


