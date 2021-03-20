import psycopg2

DATABASE_URL = 'postgres://xtnkefldcyslwo:9892716013df510c9b4ffc3489790a8223e74037232d504a12319b86ace6ffcf@ec2-54-73-147-133.eu-west-1.compute.amazonaws.com:5432/d306gfjbu4tvu8'

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

cursor = conn.cursor()

#cursor.execute("DELETE FROM Subscriptions")

cursor.execute("SELECT * FROM Subscriptions")
result = cursor.fetchall()

for i in result:
    print(i)


    """start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )"""