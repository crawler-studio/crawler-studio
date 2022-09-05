"""
@Description: 
@Usage: 
@Author: liuxianglong
@Date: 2022/9/5 下午5:34
"""
import sys
import argparse


def cmd():
    """
    run from cmd
    :return:
    """
    from ..manage import manage
    manage()


# for console debugger
if __name__ == '__main__':
    cmd()