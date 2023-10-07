# sender_email = 'elertsms@gmail.com'
# sender_password = 'frtvmacnyfvtovnn'

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
def send_mail(mailsList, body, subject ):
    # Sender's email credentials
    sender_email = 'elertsms@gmail.com'
    sender_password = 'rwcrkxcjnlkirvhx'

    # List of recipient email addresses
    recipient_emails = mailsList

    # Create a MIMEText object to represent the email content
    message = MIMEMultipart()
    message['From'] = sender_email
    message['To'] = ', '.join(recipient_emails)  # Join the email addresses with a comma and space
    message['Subject'] = subject
    message.attach(MIMEText(body, 'plain'))

    # Establish a connection to the SMTP server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    # Log in to the email account
    server.login(sender_email, sender_password)

    # Send the email
    server.sendmail(sender_email, recipient_emails, message.as_string())

    # Close the connection
    server.quit()

    print("Email sent successfully to multiple recipients!")






