import json

import requests

# url and headers for the event post API. Token requires the events.ingest permission.
url_post_event = "https://[url]/api/v2/events/ingest"
headers_post_event = {
    'accept': 'application/json; charset=utf-8',
    'Authorization': 'Api-Token [token]',
    'Content-Type': 'application/json; charset=utf-8'
}
# url, headers, and parameters for the get slo API. Token requires the slo.read permission.
slo_url = "https://[url]/api/v2/slo"
headers_get_slo = {
    'accept': 'application/json; charset=utf-8',
    'Authorization': 'Api-Token [token]'
}
params_slo = [
    ['pageSize', '1'],
    ['sort', 'name'],
    ['timeFrame', 'CURRENT'],
    ['pageIdx', '1'],
    ['demo', 'false'],
    ['evaluate', 'true'],
    ['enabledSlos', 'true']
]

# break in the printout
print("----")
while True:
    response = json.loads(requests.get(slo_url, headers=headers_get_slo, params=params_slo).content)
    slo_count = response['totalCount']
    page_size = response['pageSize']
    slo_list = response['slo']
    while len(slo_list) < slo_count:
        params_slo[3][1] = str(len(slo_list) + 1)
        response = json.loads(requests.get(slo_url, headers=headers_get_slo, params=params_slo).content)
        slo_list.append(response['slo'][0])
    for slo in slo_list:
        if slo['evaluatedPercentage'] < slo['target']:
            slo_filter = '","entitySelector":"' + slo['filter'].replace('"', '') if slo['filter'].replace('"',
                                                                                                          '') != '' else ''
            print("Missed target on:", slo['name'], end=" -Posting: ")
            data_fail = '{"eventType":"CUSTOM_ALERT",' \
                        '"title":"Failure on SLO: ' + slo['name'] + \
                        slo_filter + \
                        '","properties":{"SLO":"' + slo['name'] + \
                        '","Description":"' + slo['description'] + \
                        '","Evaluated percentage":"' + str(slo['evaluatedPercentage']) + \
                        '","Error budget":"' + str(slo['errorBudget']) + \
                        '","SLO status":"' + slo['status'] + \
                        '","SLO target percent":"' + str(slo['target']) + \
                        '","SLO warning percent":"' + str(slo['warning']) + \
                        '","SLO timeframe":"' + slo['timeframe'] + \
                        '"}}'
            resp = requests.post(url_post_event, headers=headers_post_event, data=data_fail)
            print(resp)
        elif slo['evaluatedPercentage'] < slo['warning']:
            slo_filter = '","entitySelector":"' + slo['filter'].replace('"', '') if slo['filter'].replace('"',
                                                                                                          '') != '' else ''
            print("Warning on:", slo['name'], end=" -Posting: ")
            data_warn = '{"eventType":"CUSTOM_ALERT",' \
                        '"title":"Warning on SLO: ' + slo['name'] + \
                        slo_filter + \
                        '","properties":{"SLO":"' + slo['name'] + \
                        '","Description":"' + slo['description'] + \
                        '","Evaluated percentage":"' + str(slo['evaluatedPercentage']) + \
                        '","Error budget":"' + str(slo['errorBudget']) + \
                        '","SLO status":"' + slo['status'] + \
                        '","SLO target percent":"' + str(slo['target']) + \
                        '","SLO warning percent":"' + str(slo['warning']) + \
                        '","SLO timeframe":"' + slo['timeframe'] + \
                        '"}}'
            resp = requests.post(url_post_event, headers=headers_post_event, data=data_warn)
            print(resp)
        else:
            print("no issue on:", slo['name'])
    print("----")
