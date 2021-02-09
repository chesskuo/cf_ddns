import requests
import argparse

endpoints = 'https://api.cloudflare.com/client/v4/'
ip_url = {
	'v4': 'http://ip4only.me/api/',
	'v6': 'http://ip6only.me/api/',
}

def getZoneID(dn):
	tmp = dn.split('.')
	top_lv = tmp[-2] + '.' + tmp[-1]
	params = {
		"name": top_lv
	}
	r = requests.get(endpoints + 'zones', headers=headers, params=params)
	return r.json()['result'][0]['id']

def getDomainID(dn, zID, type='A'):
	params = {
		"name": dn,
		"type": type
	}
	r = requests.get(endpoints + 'zones/' + zID + '/dns_records', headers=headers, params=params)
	return r.json()['result'][0]['id']

def get_ip_addr(v):
	try:
		r = requests.get(ip_url[v])
	except:
		exit()
	ip = r.text.split(',')[1]
	return ip

def update_dns(domain, ip_addr_4, ip_addr_6):
	zID = getZoneID(domain)
	domain_id_A = getDomainID(domain, zID)

	print('#--------------------#')
	print(' ', domain)

	data = {
		"type": "A",
		"name": domain,
		"content": ip_addr_4
	}
	r = requests.put(endpoints + 'zones/' + zID + '/dns_records/' + domain_id_A, headers=headers, json=data)
	print('  ipv4 :', r.json()['success'])

	if ip_addr_6 != '':
		domain_id_AAAA = getDomainID(domain, zID, 'AAAA')
		data = {
			"type": "AAAA",
			"name": domain,
			"content": ip_addr_6
		}
		r = requests.put(endpoints + 'zones/' + zID + '/dns_records/' + domain_id_AAAA, headers=headers, json=data)
		print('  ipv6 :', r.json()['success'])

	print('#--------------------#')

if __name__ == '__main__':
	# args parser
	parser = argparse.ArgumentParser(
		prog='cf-ddns',
		usage='cf-ddns [-6] -t <API_TOKEN> -d <DOMAIN>',
	)
	parser.add_argument('-6', action='store_true', help='enable IPv6 mode')
	parser.add_argument('-t', metavar='<API_TOKEN>', required=True, help='your cf api token')
	parser.add_argument('-d', metavar='<DOMAIN>', required=True, help='your cf domain name')
	args = vars(parser.parse_args())

	kwargs = {
		'domain': args['d'],
		'ip_addr_4': get_ip_addr('v4'),
		'ip_addr_6': get_ip_addr('v6') if args['6'] else '',
	}

	api_token = args['t']
	headers = {
		"Authorization": f"Bearer {api_token}",
		"Content-Type": "application/json"
	}

	update_dns(**kwargs)
