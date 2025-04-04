# Import libraries
from email.mime.text import MIMEText 
from email.mime.image import MIMEImage 
from email.mime.multipart import MIMEMultipart

###################################################################################################
def html2email(subject, html, sender = 'jwatkin@sandia.gov', recipients = ['jwatkin@sandia.gov']):
    '''
    Send email with html string
    '''
    # Details
    msgRoot = MIMEMultipart('related')
    msgRoot['Subject'] = subject
    msgRoot['From'] = sender
    msgRoot['To'] = ", ".join(recipients)
    msgAlternative = MIMEMultipart('alternative')
    msgRoot.attach(msgAlternative)

    # Alternative text
    msgText = MIMEText('Alternative plain text.')
    msgAlternative.attach(msgText)

    # Main message
    msgText = MIMEText(html,'html')
    msgAlternative.attach(msgText)

    # Send the email (this example assumes SMTP authentication is required)
    import smtplib
    smtp = smtplib.SMTP()
    smtp.connect('smtp.sandia.gov')
    smtp.sendmail(sender, recipients, msgRoot.as_string())
    smtp.quit()

