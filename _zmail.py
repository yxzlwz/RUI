import zmail

def send_mail(from_address, from_password, to_address,
              title="RBSI发送的问候", content="这是来自RBSI程序发送的问候。",
              from_name="RBSI"):
    mail_content = {
        "subject": title,
        "content_html": "<h1>%s</h1>" % content,
        "from": "%s <%s>" % (from_name, from_address)
    }

    server = zmail.server(from_address, from_password)
    try:
        server.send_mail([to_address], mail_content)
        return True
    except:
        return False
