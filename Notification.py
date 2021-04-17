from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr
import smtplib


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


# 邮箱
form_addr = 'zhongsheng.chen@qq.com'
# 不是邮箱密码,而是开启SMTP服务时的授权码
password = 'mlsecrcdozabijjh'
# 收件人的邮箱
to_addr = 'zschen@buct.edu.cn'
# qq邮箱的服务器地址
smpt_server = 'smtp.qq.com'


# 发送邮件

def send_notification(report_info):

    # 设置邮件信息
    msg = MIMEText(report_info, 'plain', 'utf-8')
    msg['From'] = _format_addr('爬虫-DESKTOP-RAAGIMV <%s>' % form_addr)
    msg['To'] = _format_addr('管理员 <%s>' % to_addr)
    msg['Subject'] = Header('爬虫运行状态', charset='utf-8').encode()

    server = smtplib.SMTP(smpt_server, port=25)
    server.set_debuglevel(1)
    server.login(form_addr, password)
    server.sendmail(form_addr, [to_addr], msg.as_string())
    server.quit()
