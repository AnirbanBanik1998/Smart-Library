import requests, socket
import barcode
from barcode.writer import ImageWriter

c128 = barcode.get_barcode_class('CODE128')

host_name = socket.gethostname()
host_ip = socket.gethostbyname(host_name)
url = 'http://{}:5000'.format(host_ip)
res = requests.get('{}/get_all_books'.format(url))

if res.status_code == 200:
	books = res.json()['books']
	for book in books:
		code = c128(book['barcode_id'], writer=ImageWriter())
		fullname = code.save('../../Books/{}'.format(book['name']))



