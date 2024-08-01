import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

email_text = f"""
Hi! This is the report from our script.

We have added 1 + 2 and gotten the answer {1+2}.

Bye!
"""
GMAIL_USERNAME = "yeunglaiching"
GMAIL_APP_PASSWORD = ""
recipients = ["eg_ylc@yahoo.com.hk"]
msg = MIMEMultipart()
mail_msg='''
<p>this is a html  中文 email</p>
<a href="https://www.google.com"> go to link </a>
'''
msg.attach(MIMEText(mail_msg,'html','utf-8'))

att1=MIMEText(open('/Users/yeunglaiching/Workspace/iPadCodeApp/Python/Test/graph.py','rb').read(),'base64','utf-8')
att1["Content-Type"]='application/octet-stream'
att1["Content-Disposition"]='attachment;filename="test.txt"'
msg.attach(att1)


msg["Subject"] = "Email report: a simple sum"
msg["To"] = ", ".join(recipients)
msg["From"] = f"{GMAIL_USERNAME}@gmail.com"
smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
smtp_server.login(GMAIL_USERNAME, GMAIL_APP_PASSWORD)
smtp_server.sendmail(msg["From"], recipients, msg.as_string())
smtp_server.quit()