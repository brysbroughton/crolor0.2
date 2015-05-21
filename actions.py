import crol, logs, asana
import smtplib
import email,email.encoders,email.mime.base
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def apply(action, crawljob, log_type):
    """
    Take name of action and a registration object.
    Verify action is defined and execute it on the
    registration object.
    """
    
    if actions.has_key(action):
        if action.endswith('log'):
            actions[action](crawljob)
        elif log_type:
            actions[action](crawljob, log_type)
        else:
            raise Exception("Cannot apply %s without a prior log file." % str(action))
    else:
        raise Exception("actions.apply: %s has not been defined." % str(action))

def buildexcellog(crawljob):
    """
    Use crawl_report from crawljob.crawl to build a log.
    Log type is based on type given.
    """
    
    new_log = logs.ExcelLog({'filename':crawljob.registration.department.name})
    new_log.reporttofile(crawljob.crawl.crawl_report)
    crawljob.logs['excellog'] = new_log
    crawljob.crawl.logs['excellog'] = new_log

def buildweblog(crawljob):
    """
    Use crawl_report from crawljob.crawl to build a log.
    Log type is based on type given.
    """
    
    new_log = logs.WebLog({'filename':crawljob.registration.department.name})
    new_log.reporttofile(crawljob.crawl.crawl_report)
    crawljob.logs['weblog'] = new_log
    crawljob.crawl.logs['weblog'] = new_log

def emailnotify(crawljob, log_type):
    """
    Send email to recipients in registration.
    If registration has no recipients, send
    to web@otc.edu and note this.
    """
    
    if crawljob.logs[log_type]:
        report_location = crawljob.logs[log_type].path + crawljob.logs[log_type].filename + crawljob.logs[log_type].endfilename
        msg = '<h1>Link Report</h1><p>Please review the attached report.</p>'
        subject = 'Crawl Completed'
        to_address = crawljob.registration.department.email_group
        cc_address = ''
        files = [report_location]
        from_address = 'web@otc.edu'
        file_name = crawljob.logs[log_type].filename + crawljob.logs[log_type].endfilename
        email_props = {'files':files, 'filename':file_name, 'cc_address':cc_address, 'to_address':to_address, 'from_address':from_address, 'subject':subject, 'msg_body':msg}
        e = Email(email_props)
        e.send()
    else:
        raise Exception('Cannot send email for non-existant %s file.' % str(log_type))

def asanapush(crawljob, log_type):
    """
    Use Asana API to push a task with the details of
    the crawl. Email web if there is an issue with
    the push.
    """
    
    if crawljob.logs[log_type]:
        task_details = asana.links_task_template
        task_details['name'] = crawljob.registration.department.name + " :: Broken Link Report"
        asana.pushlogtotask(task_details, crawljob.logs[log_type].filename + crawljob.logs[log_type].endfilename)
    else:
        raise Exception('Cannot push Asana for non-existant %s file.' % str(log_type))


class Email(crol.GenericType):
    def __init__(self, kwargs={}):
        self.props = {
            'type' : 'email',
            'msg_body' : '',
            'subject' : '',
            'from_address' : "",
            'to_address' : [],
            'cc_address' : '',
            'files' : [],
            'filename' : '',
            'smtp_server' : 'smtp.otc.edu',
            'mime_type' : "html"
        }
        super(Email, self).__init__(**kwargs)
    
    def send(self):
        has_cc = False
        addresses = []
        for addy in self.to_address:
            addresses.append(addy)
        if self.props['to_address'] == "":
            raise Exception('to_address must be set in class: Email')
        elif self.props['from_address'] == "":
            raise Exception('from_address must be set in class: Email')
        else:
            #composing message using MIMEText
            msg = MIMEMultipart()
            msg['Subject'] = self.subject
            msg['From'] = self.from_address
            msg['To'] = ", ".join(addresses)
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
    'email'    : emailnotify,
    'asana'    : asanapush,
    'excellog' : buildexcellog,
    'weblog'   : buildweblog
}
