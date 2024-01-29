import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json
import requests


def wx_send(title, body, key="SCT236279TU7QP2eKj6JCEmpCa8oiryxSJ"):  # serve酱微信推送
    text_title = title
    text_content = body
    sendKey = key  # key

    url = f"https://sctapi.ftqq.com/{sendKey}.send"
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'text': f"{text_title}",
        'content': f"{text_content}"
    }

    response = requests.post(url, data=data)

    if json.loads(response.text)["data"]['error'] == 'SUCCESS':
        return True
    else:
        return False


"""

微信公众号推送

"""


def wx_get_access_token(appid="wx423b935179621230", secret="84901feb2960838c5a04acac4b1a6d40"):  # 微信公众号获取token
    """
    获取微信全局接口的凭证(默认有效期俩个小时)
    如果不每天请求次数过多, 通过设置缓存即可
    """
    result = requests.get(
        url="https://api.weixin.qq.com/cgi-bin/token",
        params={
            "grant_type": "client_credential",
            "appid": appid,
            "secret": secret,
        }
    ).json()

    if result.get("access_token"):
        access_token = result.get('access_token')
    else:
        access_token = None
    return access_token


def sendmsg(openid, msg):
    access_token = wx_get_access_token()

    body = {
        "touser": openid,
        "msgtype": "text",
        "text": {
            "content": msg
        }
    }
    response = requests.post(
        url="https://api.weixin.qq.com/cgi-bin/message/custom/send",
        params={
            'access_token': access_token
        },
        data=bytes(json.dumps(body, ensure_ascii=False), encoding='utf-8')
    )
    # 这里可根据回执code进行判定是否发送成功(也可以根据code根据错误信息)
    result = response.json()
    print(result)




class QQ_EMAIL:
    from_email = None  # 发送者的邮箱
    to_email = None  # 接收者的邮箱
    key_email = None  # 发送者的邮箱授权码
    subject_email = None  # 欲发送邮箱的主题
    body_text = None  # 欲发送邮箱的文本内容

    def __init__(self, from_email, to_email, key_email, subject_email, body_text):
        self.from_email = from_email  # 发送者的邮箱
        self.to_email = to_email  # 接收者的邮箱
        self.key_email = key_email  # 发送者的邮箱授权码
        self.subject_email = subject_email  # 欲发送邮箱的主题
        self.body_text = body_text  # 欲发送邮箱的文本内容

    def send_email(self):
        msg = MIMEMultipart()  # 创建一个MIMEMultipart对象
        # 设置邮箱的主要内容
        msg['From'] = self.from_email
        msg['To'] = self.to_email
        msg['Subject'] = self.subject_email  # 注意这里应该是'Subject'而不是'subject'
        msg.attach(MIMEText(self.body_text, 'plain'))
        # 邮件服务器设置，使用QQ SMTP服务器
        server = smtplib.SMTP('smtp.qq.com', 587)  # 注意这里改动的地方
        server.starttls()
        server.login(self.from_email, self.key_email)
        text = msg.as_string()
        result = server.sendmail(self.from_email, self.to_email, text)  # 注意这里改动的地方，添加了发件人和收件人参数。
        server.quit()  # 注意这里改动的地方，关闭SMTP连接。
        # 检查邮件是否发送成功
        if result:
            print("邮件发送失败")
            return False
        else:
            print("邮件发送成功")
            return True
