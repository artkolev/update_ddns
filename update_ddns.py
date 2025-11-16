#!/usr/bin/env python

import datetime
import requests
import logging

import xml.etree.ElementTree as ET

FORMAT=u'%(levelname)s: %(message)s'
logging.basicConfig(filename='update_ddns.log', filemode='a',
                    format=FORMAT, level=logging.ERROR)
logging.getLogger('').setLevel(logging.ERROR)
logging.getLogger('app').setLevel(logging.INFO)
logging.getLogger('handlers').setLevel(logging.ERROR)

log = logging.getLogger('app')


def get_request(ulr_str):
    try:
        return_text = requests.get(ulr_str, timeout=10);
    except requests.exceptions.ConnectionError as e:
        log.error('Request connection error to {}'.format(ulr_str))
        return None

    if return_text.status_code == 200:
        return return_text.text
    else:
        log.error('Server error {}'.format(return_text.status_code))
        return None

def update_ddns(domain, subdomain, token, api_url, timeout, get_ip_url):
    log.info ("{}: Start updating ddns".format(datetime.datetime.strftime(
                                     datetime.datetime.now(),'%d-%m-%Y %H:%M')))

    #get current ip
    current_ip = get_request(get_ip_url);

    if not current_ip:
        log.error('Current IP is not detected')
        return

    log.debug('Current IP: {}'.format(current_ip))
    #get id subdomain record
    get_records_url = '{}get_domain_records?token={}&domain={}'.\
        format(api_url, token, domain)
    records = get_request(get_records_url)

    if not records:
        log.error('Error get records')
        return

    root_get_id = ET.fromstring(records)
    status_get_id = root_get_id.findall("./domains/error")[0].text
    if status_get_id != 'ok':
        log.error('Error get subdomain ID: {}').format(status_get_id)
        return

    try:
        record_id = (root_get_id.findall("./domains/domain/response/record[@subdomain='{}']"
                                        .format(subdomain))[0].text)
    except IndexError:
        log.error('Subdomain "{}" is not foud'.format(subdomain))
        return
    if record_id == current_ip:
        log.info('IP is not updated')
        return

    try:
        id_record = root_get_id.findall(("./domains/domain/response/record[@subdomain='{}']"
                               .format(subdomain)))[0].get('id')
    except IndexError:
        log.error('Subdomain "{}" is not foud'.format(subdomain))
        return
    log.debug('ID subdomain record: {}'.format(id_record))

    #set subdomain IP
    set_ip_url = ('{}/edit_a_record?token={}&domain={}&subdomain={}\
                  &record_id={}&ttl={}&content={}'
                  .format(api_url,
                          token,
                          domain,
                          subdomain,
                          id_record,
                          timeout,
                          current_ip))
    set_ip = get_request(set_ip_url)

    if not set_ip:
        og.error('Error set subdomain IP')
        return

    root_set_ip = ET.fromstring(records)
    status_set_ip = root_set_ip.findall("./domains/error")[0].text
    if status_get_id == 'ok':
        log.info('IP successfuly updated to {}'\
                .format(current_ip))

if __name__ == "__main__":
    update_ddns('example.com',
                'subdomain',
                'secret_coken',
                'https://pddimp.yandex.ru/nsapi/',
                600,
                'https://api.ipify.org/')
