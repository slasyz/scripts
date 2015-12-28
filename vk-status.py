#!/usr/bin/python3

import api.services.vk
from time import sleep

vk_req = api.services.vk.VK('12522425', '2994650', 'TKG0ZAtlwoOEwK0qPLU7')
vk_req.auth('status,offline')

while True:
    print(vk_req.request('account.setOnline'))
    sleep(60)
