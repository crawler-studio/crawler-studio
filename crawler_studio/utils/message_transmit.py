# -*- coding: utf-8 -*-
"""
@Description: 发送钉钉消息, 邮件的模块
钉钉机器人使用方法参考：https://developers.dingtalk.com/document/app/custom-robot-access
@Usage:
@Author: liuxianglong
"""
import os
import requests
import logging
from email.mime.text import MIMEText  # 专门发送正文
from email.mime.multipart import MIMEMultipart  # 发送多个部分
from email.mime.application import MIMEApplication  # 发送附件
import smtplib  # 发送邮件
from crawler_studio.app_settings.models import MailSender


logger = logging.getLogger(__name__)


def send_ding_message(title, content, ding_addr):
    """
    发送钉钉报警
    useage: send_ding_message('虎博爬虫预警', '测试')
    :return:
    """
    data = {
        'msgtype': 'markdown',
        'markdown': {
            'title': '{}'.format(title),
            'text': '### {}\n{}'.format(title, content),
        },
        'at': {
            'isAtAll': True
        }
    }

    res = requests.post(ding_addr, json=data)
    if res.json()['errcode'] == 0:
        logger.info('发送钉钉消息成功')
    else:
        logger.error(f'发送钉钉消息失败, {res.text}')


def send_mail(receiver: str, subject: str = "", content: str = "",
              attach=''):
    """
    发送带附件的邮件
    :param attach: 附件全路径
    :param receiver: 收件人
    :param subject: 主题
    :param content: 正文
    :param sender:  发件人，可在系统设置中设置默认值
    :param auth_code:   授权码，可在系统设置中设置默认值
    :param server_addr: 邮箱服务器，可在系统设置中设置默认值
    :param server_port: 邮件发送端口
    :return:
    """
    mail_sender = MailSender.objects.first()
    if not mail_sender:
        logger.info(f'系统邮件发件人不存在')
        return

    sender = mail_sender.mail_addr
    auth_code = mail_sender.auth_code
    server_addr = mail_sender.server_addr
    server_port = mail_sender.mail_port

    # 构造一个邮件体：正文 附件
    msg = MIMEMultipart()
    msg['Subject'] = subject  # 主题
    msg['From'] = sender  # 发件人
    msg['To'] = receiver  # 收件人

    # 构建正文
    part_text = MIMEText(content)
    msg.attach(part_text)  # 把正文加到邮件体里面去

    # 构建邮件附件
    if attach:
        part_attach = MIMEApplication(open(attach, 'rb').read())  # 打开附件
        part_attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attach))  # 为附件命名
        msg.attach(part_attach)  # 添加附件

    # 发送邮件 SMTP
    smtp = smtplib.SMTP_SSL(server_addr, server_port)  # 连接服务器，SMTP_SSL是安全传输

    smtp.login(sender, auth_code)
    smtp.sendmail(sender, receiver, msg.as_string())  # 发送邮件
    smtp.quit()
    logger.info('邮件发送成功！')
    logger.info('收件人: %s' % msg['To'])
    logger.info('主题: %s' % subject)
    logger.info('正文: %s' % content)
    if attach:
        logger.info('附件名称: %s' % os.path.basename(attach))


if __name__ == '__main__':
    # send_ding_message('虎博爬虫预警', '测试')
    send_mail(receiver='862187570@qq.com', subject='爬虫测试', content='测试内容哦～')
