import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import email.header
from imap_tools import MailBox, AND

import time
import smtplib

class Mail(MIMEMultipart):
    def __init__(self, to_addr, subject, date, body) -> None:
        assert isinstance(to_addr, str) and isinstance(subject, str) and isinstance(date, str) and isinstance(body, str), "Mail.__init__(): Invalid type"
        super().__init__()
        self['To'] = to_addr
        self['Subject'] = subject
        self['Date'] = date
        self.attach(MIMEText(body, 'plain'))
    
    @staticmethod
    def new(to_addr, subject, body) -> "Mail":
        return Mail(
            to_addr=to_addr, 
            subject=subject, 
            date=time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime()),
            body=body
        )
    
    @staticmethod
    def from_imap_tools(imap_tools_mail: email.message.EmailMessage) -> "Mail":
        mail = Mail(
            to_addr=", ".join(imap_tools_mail.to),
            subject=imap_tools_mail.subject,
            date=imap_tools_mail.date_str,
            body=imap_tools_mail.text
        )
        mail['Message-ID'] = imap_tools_mail.uid
        mail['From'] = imap_tools_mail.from_
        if imap_tools_mail.cc:
            mail['Cc'] = ", ".join(imap_tools_mail.cc)
        if imap_tools_mail.bcc:
            mail['Bcc'] = ", ".join(imap_tools_mail.bcc)
        if imap_tools_mail.reply_to:
            mail['Reply-To'] = ", ".join(imap_tools_mail.reply_to)
        return mail
    
    def add_attachment(self, file_path):
        attachment = open(file_path, 'rb')
        p = MIMEBase('application', 'octet-stream')
        p.set_payload((attachment).read())
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % file_path)
        self.attach(p)


class MailApp():
    def __init__(self, username, password, email_adress, imap_server_adress, smtp_server_adress) -> None:
        self.imap_server_adress = imap_server_adress
        self.smtp_server_adress = smtp_server_adress

        self.username = username
        self.password = password
        self.email_adress = email_adress
        
        self.cc_functionality_on = False
    
    def send(self, mail: Mail):
        assert not mail['From'] or mail['From'] == self.email_adress or mail['From'] == ''
        mail['From'] = self.email_adress

        server = smtplib.SMTP(self.smtp_server_adress)
        server.starttls()
        server.login(self.username, self.password)
        server.sendmail(self.email_adress, mail['To'], mail.as_string())

        if self.cc_functionality_on:
            time.sleep(20)
            for addr in mail['Cc'].split(';'):
                server.sendmail(self.email_adress, addr, mail.as_string())
                time.sleep(20)

        server.quit()
    
    def reply(self, mail_to_reply_to: Mail, reply_text: str):
        mail = Mail.new(
            to_addr=mail_to_reply_to['From'], 
            subject="RE: "+ mail_to_reply_to["Subject"].replace("Re: ", "").replace("RE: ", ""),
            body=reply_text
        )
        mail['In-Reply-To'] = mail_to_reply_to['Message-ID']
        mail['References'] = mail_to_reply_to['Message-ID']
        mail['Reply-To'] = mail_to_reply_to['From']
        self.send(mail)

    def receive(self, search_criteria=AND(seen=False), ask_for_download=False) -> "list[Mail]":
        # https://github.com/ikvk/imap_tools#search-criteria
        # Get date, subject and body len of all emails from INBOX folder
        emails_ = []
        with MailBox(self.imap_server_adress).login(self.username, self.password) as mailbox:
            for msg in mailbox.fetch(criteria=search_criteria, reverse=True): # AND(seen=False), "SINCE 02-Feb-2023", AND(from_="lina.wilske@student.hpi.uni-potsdam.de")
                emails_.append(Mail.from_imap_tools(msg))
                if ask_for_download:
                    print(f"{msg.subject}, attachments: {len(msg.attachments)}")
                    if input("Download? (y/n)") == "y":
                        for att in msg.attachments:
                            with open(att.filename, "wb") as f:
                                f.write(att.payload)
        return emails_  


