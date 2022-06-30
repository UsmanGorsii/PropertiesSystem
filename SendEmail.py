from email.mime.text import MIMEText
import smtplib
import time
username = "Joelstottjess@gmail.com"  # your gmail account email
password = "yxxrnbsurmrgqdpu"  # your gmail account password
send_to = "Joel@nicaliferealty.com"


def send_emails(subject, body):
    # mailserver = smtplib.SMTP('smtp.office365.com', 587)
    mailserver = smtplib.SMTP('smtp.gmail.com', 587)

    mailserver.ehlo()
    mailserver.starttls()
    mailserver.login(username, password)
    while True:
        try:
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = username
            msg['To'] = send_to
            mailserver.sendmail(username, msg["To"], msg.as_string())
            break
        except Exception as e:
            mailserver.quit()
            del mailserver
            print("Error sending the email, trying again,", e)
            time.sleep(15)
            # mailserver = smtplib.SMTP('smtp.office365.com', 587)
            mailserver = smtplib.SMTP('smtp.gmail.com', 587)

            mailserver.ehlo()
            mailserver.starttls()
            mailserver.login(username, password)
    mailserver.quit()

