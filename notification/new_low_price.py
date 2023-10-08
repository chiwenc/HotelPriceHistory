import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

# Gmail帐户信息
sender_email = 'pricetrackertwsite@gmail.com'
sender_password = 'gyffswilkurceemj'

# 收件人邮箱地址
recipient_email = 'recipient@gmail.com'

# 创建邮件内容
subject = '最新旅館優惠通知'

# 替换参数
user_name = '用户名'
hotel_data = [
    {'hotel_name': '酒店A', 'min_twd_price': 100},
    {'hotel_name': '酒店B', 'min_twd_price': 120},
    {'hotel_name': '酒店C', 'min_twd_price': 80}
]

# 构建邮件正文的 HTML 模板
html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>最新旅館優惠通知</title>
    <!-- 引入Bootstrap CSS -->
    <link href="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css" rel="stylesheet">
</head>
<body>
    <div class="container">
        <div class="jumbotron">
            <h1 class="display-4">親愛的 {user_name} 先生/女士,</h1>
            <p class="lead">我們很高興地通知您，以下是一些提供最新低價的旅館：</p>
            <!-- 使用循環列出多家旅館的資訊 -->
            <ul class="list-group">
                {''.join([f"""
                    <li class="list-group-item">
                        <h3>{hotel['hotel_name']}</h3>
                        <p>價格: {hotel['min_twd_price']} 新台幣</p>
                    </li>
                """ for hotel in hotel_data])}
            </ul>

            <p class="lead">這是一個難得的機會，請不要錯過！</p>
        </div>
    </div>

    <!-- 引入Bootstrap JavaScript和jQuery -->
    <script src="https://code.jquery.com/jquery-3.5.1.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.3/dist/umd/popper.min.js"></script>
    <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js"></script>
</body>
</html>
"""

# 使用SMTP连接到Gmail服务器并发送邮件
try:
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # 将 HTML 模板中的参数替换为实际的值
    html_content = html_template.format(user_name=user_name, hotel_data=hotel_data)

    msg.attach(MIMEText(html_content, 'html'))

    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()
    print('邮件发送成功')
except Exception as e:
    print('邮件发送失败:', str(e))
