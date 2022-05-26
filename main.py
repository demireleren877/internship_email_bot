
import smtplib
from email.message import EmailMessage
import imaplib
import email.message
from email import policy
import os
import boto3
import shutil
from secrets import email_password, aws_acccess_key_id, aws_secret_access_key

def login(server):
    server.login("demireleren1903@gmail.com", email_password)


def logMails(email_msg):
    print("\n----- MESSAGE START -----\n")
    print("From: %s\nTo: %s\nDate: %s\nSubject: %s\n\n" % (
        str(email_msg['From']),
        str(email_msg['To']),
        str(email_msg['Date']),
        str(email_msg['Subject'])))

def saveAttachements(email_msg):
    for part in email_msg.walk():
      if part.get_content_maintype() != 'multipart' and part.get('Content-Disposition') is not None:
          attendant_name = email_msg['From'].split("<")[
              1].split(">")[0]                    
          if not os.path.exists(attendant_name):
              os.makedirs(attendant_name)
          open(attendant_name + '/' + part.get_filename(),
               'wb').write(part.get_payload(decode=True))
          s3 = boto3.client('s3',aws_access_key_id=aws_acccess_key_id,aws_secret_access_key=aws_secret_access_key)
          s3.upload_file(attendant_name+"/"+part.get_filename(), "internship-applies", attendant_name+"/"+ part.get_filename())
          shutil.rmtree(attendant_name)


def sendResponse(to):
    msg = EmailMessage()
    msg["Subject"] = "Staj Başvurusu Hakkında"
    msg["From"] = "demireleren1903@gmail.com"
    msg["To"] = to
    msg.set_content(
        "Merhabalar, Staj başvurunuz başarıyla alındı.")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        login(server)
        server.send_message(msg)


def readEmails():
    server = imaplib.IMAP4_SSL("imap.gmail.com", 993)
    login(server)
    server.select('INBOX')
    status, data = server.search(None, "(UNSEEN)")
    for num in data[0].split():
        status, data = server.fetch(num, '(RFC822)')
        email_msg = data[0][1]
        email_msg = email.message_from_bytes(email_msg, policy=policy.SMTP)
        if email_msg['Subject'].lower().__contains__("staj"):
            sendResponse(email_msg['From'])     
            saveAttachements(email_msg)       
        logMails(email_msg)


if __name__ == "__main__":
    while True:
        readEmails()
