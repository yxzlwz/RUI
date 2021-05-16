import random
import time
import zmail

def send_mail(from_address, from_password, to_address,
              title="RBSI发送的问候", content="这是来自RBSI程序发送的问候。",
              from_name="RBSI"):
    mail_content = {
        "subject": title,
        "content_html": "<p>%s</p><br /><p>本次发信识别码：%s %s</p>" % (content, random.random(), time.time()),
        "from": "%s <%s>" % (from_name, from_address)
    }

    server = zmail.server(from_address, from_password)
    try:
        server.send_mail([to_address], mail_content)
        return True
    except:
        return False
