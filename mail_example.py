import smtplib
from email.mime.text import MIMEText

#composing message using MIMEText
msg = MIMEText("The body of the message as dictated by python smtplib and MIMEText")
msg['Subject'] = 'Look what Python can do!'
msg['From'] = 'web@otc.edu'
msg['to'] = 'broughtb@otc.edu'

#Email transmission with smtplib and OTC servers
s = smtplib.SMTP('smtp.otc.edu')
s.sendmail('web@otc.edu', 'broughtb@otc.edu', msg.as_string())
s.quit()
