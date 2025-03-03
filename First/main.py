import csv

from pythonping import ping


hosts = ['www.google.com', 'stackoverflow.com', 'github.com', '8.8.8.8', 
         'vk.com', 'youtube.com', 'yandex.ru', 'ru.wikipedia.org',
         'thedoors.com', 'www.reddit.com']

with open('res.csv', 'w') as result_file:
    result_writter = csv.writer(result_file)
    for host in hosts:
        #print("Domain is: ", host)
        ping_result = ping(target=host, count=10, timeout=2)
        result_writter.writerow([host, ping_result.rtt_avg_ms])
        #print(ping_result)
        #print('---')