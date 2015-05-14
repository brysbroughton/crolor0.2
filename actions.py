import crol, asana
import smtplib
import email,email.encoders,email.mime.base
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def apply(action, registration, log):
    """
    Take name of action and a registration object.
    Verify action is defined and execute it on the
    registration object.
    """
    if actions.has_key(action):
        actions[action](registration, log)
    else:
        raise Exception("actions.apply: %s has not been defined." % str(action))
    
def emailnotify(registration, log):
    """
    Send email to recipients in registration.
    If registration has no recipients, send
    to web@otc.edu and note this.
    """
    report_location = log.path+log.filename+log.endfilename
    msg = '<h1>Link Report</h1><p>Please review the attached report.</p>'
    subject = 'Crawl Completed'
    to_address = registration.department.main_email
    cc_address = ''
    files = [report_location]
    from_address = 'web@otc.edu'
    file_name = log.filename + log.endfilename
    email_props = {'files':files, 'filename':file_name, 'cc_address':cc_address, 'to_address':to_address, 'from_address':from_address, 'subject':subject, 'msg_body':msg}
    e = Email(email_props)
    e.send()
    
def asanapush(registration, log):
    """
    use Asana API to push a task with the details of
    the crawl. Email web if there is an issue with
    the push.
    """
    task_details = asana.links_task_template
    task_details['name'] = registration.department.name + " :: Broken Link Report"
    asana.pushlogtotask(task_details, log.filename + log.endfilename)

    
class Email(crol.GenericType):
    def __init__(self, kwargs={}):
        self.props = {
        'type' : 'email',
        'msg_body' : '',
        'subject' : '',
        'from_address' : "",
        'to_address' : "",
        'cc_address' : '',
        'files' : [],
        'filename' : '',
        'smtp_server' : 'smtp.otc.edu',
        'mime_type' : "html"
        }
        super(Email, self).__init__(**kwargs)
        
    def send(self):
        has_cc = False
        addresses = [self.to_address]
        if self.props['to_address'] == "":
            raise Exception('to_address must be set in class: Email')
        elif self.props['from_address'] == "":
            raise Exception('from_address must be set in class: Email')
        else:
            #composing message using MIMEText
            msg = MIMEMultipart()
            msg['Subject'] = self.subject
            msg['From'] = self.from_address
            msg['To'] = self.to_address
            if self.cc_address != "":
                msg['CC'] = self.cc_address
                has_cc = True
                addresses.append(self.cc_address)
            if self.props['mime_type'] == "plain":
                message = MIMEText(self.msg_body, 'plain')
                msg.attach(message)
            else:
                message = MIMEText(self.msg_body, 'html')
                msg.attach(message)
            for f in self.files:
                fileMsg = email.mime.base.MIMEBase('application','octet-stream')
                fileMsg.set_payload(open(f, 'rb').read())
                email.encoders.encode_base64(fileMsg)
                fileMsg.add_header('Content-Disposition','attachment;filename=%s' % self.filename)
                msg.attach(fileMsg)
            #Email transmission with smtplib and OTC servers
            s = smtplib.SMTP(self.smtp_server)
            s.sendmail(self.from_address, addresses, msg.as_string())
            s.quit()
 
   
       
actions = {
    'email' : emailnotify,
    'asana' : asanapush
}
