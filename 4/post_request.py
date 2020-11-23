import requests, base64
# URL = 'https://datasend.webpython.graders.eldf.ru/submissions/1/'
# usrlog = "alladin"
# usrpass = "opensesame"
# r=requests.post(URL, 
#                 auth = (usrlog, usrpass))
# print(r.text)
# requests.post('https://datasend.webpython.graders.eldf.ru/submissions/1/', auth=('alladin', 'opensesame'))

usrlog = "galchonok"
usrpass = "ktotama"
URL_new = 'https://datasend.webpython.graders.eldf.ru/'
path = 'submissions/super/duper/secret/'
r = requests.put('{}{}'.format(URL_new, path), 
                auth = (usrlog, usrpass))
print(r.text)