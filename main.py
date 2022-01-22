from email.message import EmailMessage
import requests
import smtplib
import os

email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
apikey_alpha = os.getenv("APIKEY_ALPHA")
apikey_news = os.getenv("APIKEY_NEWS")

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

parameters_alpha = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK,
    "interval": "60min",
    "apikey": apikey_alpha,
}

parameters_news = {
    "apiKey": apikey_news,
    "qInTitle": COMPANY_NAME,
}


def send_email():
    response_news = requests.get(url="https://newsapi.org/v2/everything", params=parameters_news)
    response_news.raise_for_status()
    data_news = response_news.json()
    # news_list[:] = cada notícia   /   news_lits[:][0] = título / news_lits[:][1] = descrição / news_lits[:][2] = link
    news_list = [(data_news["articles"][_]["title"],
                  data_news["articles"][_]["description"],
                  data_news["articles"][_]["url"]) for _ in range(3)]
    message = EmailMessage()
    message.set_content(f"{news_list[0][0]}.\n{news_list[0][1]}\n{news_list[0][2]}\n\n"
                        f"{news_list[1][0]}.\n{news_list[1][1]}\n{news_list[1][2]}\n\n"
                        f"{news_list[2][0]}.\n{news_list[2][1]}\n{news_list[2][2]}")
    message['Subject'] = f"{STOCK}: {str_percentage}%"
    message['From'] = email
    message['To'] = email

    with smtplib.SMTP("smtp.gmail.com") as connection:
        connection.starttls()
        connection.login(user=email, password=password)
        connection.send_message(message)
        return


response_alpha = requests.get(url="https://www.alphavantage.co/query", params=parameters_alpha)
response_alpha.raise_for_status()
data_stock = response_alpha.json()

close_yesterday = float(list(data_stock["Time Series (Daily)"].items())[0][1]["4. close"])
close_bf_yesterday = float(list(data_stock["Time Series (Daily)"].items())[1][1]["4. close"])

difference = close_yesterday - close_bf_yesterday
percentage = round((difference / close_bf_yesterday) * 100, 2)

# Se a diferença do valor da bolsa entre o fechamento de antes de ontem com o de ontem for maior que 5%,
# ou menor que -5%,
# então será enviado um email com a diferença e com as três últimas notícias sobre a empresa.
if percentage >= 5:
    str_percentage = "🔺" + str(percentage)
    send_email()
elif percentage <= -5:
    str_percentage = str(percentage).replace("-", "🔻")
    send_email()
