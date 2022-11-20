#!/usr/bin/env python
# encoding: utf-8
from datetime import timedelta, datetime
from celery import Celery
from redisbeat.scheduler import RedisScheduler
from celery.schedules import crontab
import setting
import pandas as pd
from bson.objectid import ObjectId
import api
from numpy import NaN, nan
import os
import shutil
import time
import json

from mongo_connect import mongo_create
mydb = mongo_create()

CELERY_BROKER_URL = setting.CELERY_URL
CELERY_RESULT_BACKEND = setting.CELERY_URL
celery = Celery('tasks', backend=CELERY_RESULT_BACKEND,
                broker=CELERY_BROKER_URL, timezone='Asia/Ho_Chi_Minh')
celery.conf.update(CELERY_REDIS_SCHEDULER_URL=CELERY_BROKER_URL)

celery.conf.beat_schedule = {
    # 'init': {
    #     'task': 'tasks.init',
    #     'schedule': timedelta(seconds=5),
    #     'args': (),
    # },
    # 'check_and_remove_task': {
    #     'task': 'tasks.check_and_remove_task',
    #     'schedule': crontab(),
    #     'args': (),
    # },
}


@celery.task(name='add', serializer='json')
def add(a, b):
    print(a)
    print(b)
    # result = {
    #     'a': a,
    #     'b': b,
    #     'result': a + b,
    # }
    return "add"


@celery.task(name='callout_safe', serializer='json')
def callout_safe(client_id, campaign_id, conversation_id, customer_phone):
    filter = {
        'campaign_id': campaign_id,
        'status': 'da_khoi_tao',
        'conversation_id': {'$ne': ''}
    }
    api_key = mydb.clients.find_one(
        {'_id': ObjectId(client_id)}).get('api_key')
    token = api.get_token_nextiva(api_key)
    response = api.make_call_bot_v3_callout_safe(
        conversation_id, token)
    # response = {'status': 0, 'msg': 'Success'}
    if response.get('status') == 0:
        filter['customer_phone'] = customer_phone
        mydb.smartbot_webhook.update_one(
            filter, {'$set': {'status': 'dang_goi'}})
    return "callout_safe"


@celery.task(name='add_contacts_by_excel', serializer='json')
def add_contacts_by_excel(client_id, tags, data_excel):
    list_tags = []
    for tag in tags:
        tag = ObjectId(tag)
        list_tags.append(tag)
    df = pd.DataFrame.from_dict(data_excel)
    num_of_cols = len(df.columns)
    num_of_rows = len(df)
    infos = []
    for i in range(num_of_rows):
        d = {
            'client_id': ObjectId(client_id),
            'created_at': api.getNOW(),
            'new_tags': list_tags,
        }
        for j in range(num_of_cols):
            key = df.columns.values[j].lower()
            value = df.values[i][j]
            if value is nan:
                value = ""
            d[key] = value
            if key == 'phone' or key == 'called':
                d['phone'] = api.convert_phone_number(str(value))
        infos.append(d)
        filter = {
            'client_id': ObjectId(client_id),
            'phone': d['phone']
        }
        exist_phone = mydb.smartbot_contacts.find_one(filter)
        if exist_phone:
            exist_tags = exist_phone.get('tags')
            exist_tags.extend(d.get('new_tags'))
            d['tags'] = exist_tags
            del d['new_tags']
            mydb.smartbot_contacts.update_one(filter, {"$set": d})
        else:
            d['tags'] = d['new_tags']
            del d['new_tags']
            mydb.smartbot_contacts.insert_one(d)
    if os.path.exists("file"):
        shutil.rmtree('file')
    os.mkdir('file')
    return "add_contacts_by_excel"


@celery.task(name='init_campaign')
def init_campaign(client_id, campaign_id, list_gio_goi_ra, infos, number_have_call, call_type, nhac_lich_theo, khoang_ngay_goi, week, month):
    # Thêm khách hàng vào smartbot_webhook
    index_phone = number_have_call
    if call_type == "call_repeat":
        if nhac_lich_theo == 'week':
            cal_list_date_call = api.cal_list_date_call(
                nhac_lich_theo, khoang_ngay_goi, week)
            for index, info in enumerate(infos):
                if index_phone > 0:
                    index_phone -= 1
                    lst_ngay = []
                    time_ngay = str(list_gio_goi_ra[index]).split("T")[1]
                    for i in cal_list_date_call:
                        time_call = i+" "+time_ngay
                        convert_time_call = pd.to_datetime(time_call)
                        lst_ngay.append(convert_time_call)
                    try:
                        data_call_params = {
                            'campaign_id': campaign_id,
                            'client_id': client_id,
                            'customer_phone': info.get('called'),
                            'input_slots': info.get('call_params'),
                            'status': 'chua_goi',
                            'gio_goi_ra': lst_ngay,
                            'created_at': api.getNOW(),
                        }
                        mydb.smartbot_webhook.insert_one(data_call_params)
                    except:
                        break
                else:
                    break
        else:
            cal_list_date_call = api.cal_list_date_call(
                nhac_lich_theo, khoang_ngay_goi, month)
            for index, info in enumerate(infos):
                if index_phone > 0:
                    index_phone -= 1
                    lst_ngay = []
                    time_ngay = str(list_gio_goi_ra[index]).split("T")[1]
                    for i in cal_list_date_call:
                        time_call = i+" "+time_ngay
                        convert_time_call = pd.to_datetime(time_call)
                        lst_ngay.append(convert_time_call)
                    try:
                        data_call_params = {
                            'campaign_id': campaign_id,
                            'client_id': client_id,
                            'customer_phone': info.get('called'),
                            'input_slots': info.get('call_params'),
                            'status': 'chua_goi',
                            'gio_goi_ra': lst_ngay,
                            'created_at': api.getNOW(),
                        }
                        mydb.smartbot_webhook.insert_one(data_call_params)
                    except:
                        break
                else:
                    break
        number_of_calls = number_have_call * len(lst_ngay)
    else:
        for index, info in enumerate(infos):
            if index_phone > 0:
                index_phone -= 1
                try:
                    data_call_params = {
                        'campaign_id': campaign_id,
                        'client_id': client_id,
                        'customer_phone': info.get('called'),
                        'input_slots': info.get('call_params'),
                        'status': 'chua_goi',
                        'gio_goi_ra': [pd.to_datetime(list_gio_goi_ra[index])],
                        'created_at': api.getNOW(),
                    }
                    mydb.smartbot_webhook.insert_one(data_call_params)
                except:
                    break
            else:
                break
        number_of_calls = number_have_call
    mydb.smartbot_callout_campaigns.update_one({'_id': ObjectId(campaign_id)}, {'$set': {
                                               'number_of_calls': number_of_calls}})

    # Init cuộc gọi
    url_webhook = f'{setting.BASE_URL}/smartbot_webhook/{client_id}/{campaign_id}'
    campaign = mydb.smartbot_callout_campaigns.find_one(
        {'_id': ObjectId(campaign_id)})

    hotlines = campaign.get('hotline')
    lst_viettel = []
    lst_vina = []
    lst_mobi = []
    for hotline in hotlines:
        provider_hotline = api.detect_phone_number(hotline)
        if provider_hotline == 'Viettel':
            lst_viettel.append(hotline)
        if provider_hotline == 'Mobifone':
            lst_mobi.append(hotline)
        if provider_hotline == 'Vinaphone':
            lst_vina.append(hotline)

    bot_region = campaign.get('region')
    bot_id = mydb.bots.find_one(
        {'_id': ObjectId(campaign.get('bot_id'))}).get('bot_id')
    api_key = mydb.clients.find_one(
        {'_id': ObjectId(client_id)}).get('api_key')

    list_call_params = mydb.smartbot_webhook.find(
        {'campaign_id': campaign_id, 'status': 'chua_goi'})
    for index, call_params in enumerate(list_call_params):
        customer_phone = call_params.get('customer_phone')
        hotline = api.choose_hotline(
            customer_phone, lst_viettel, lst_mobi, lst_vina, hotlines)
        input_slots = call_params.get('input_slots')
        token = api.get_token_nextiva(api_key)
        response = api.make_call_bot_v3_create(input_slots, hotline,
                                               customer_phone, bot_id, bot_region, url_webhook, token)
        if response.get('status') == 0:
            mydb.smartbot_webhook.update_one({'campaign_id': campaign_id, 'customer_phone': customer_phone},
                                             {'$set': {'status': 'da_khoi_tao', 'conversation_id': response.get('conversation_id')}})
        # mydb.smartbot_webhook.update_one({'campaign_id': campaign_id, 'customer_phone': customer_phone},
        #                                  {'$set': {'status': 'da_khoi_tao', 'conversation_id': 'conver'}})
        # print(input_slots, hotline, customer_phone,
        #       bot_id, bot_region, url_webhook)
        time.sleep(3)

    # Gọi ra với eta
    filter = {
        'campaign_id': campaign_id,
        'status': 'da_khoi_tao',
        'conversation_id': {'$ne': ''}
    }
    customers = mydb.smartbot_webhook.find(filter)
    for customer in customers:
        list_gio_goi_ra = customer.get('gio_goi_ra')
        customer_phone = customer.get('customer_phone')
        conversation_id = customer.get('conversation_id')
        for gio in list_gio_goi_ra:
            celery.send_task(name='callout_safe', args=(
                client_id, campaign_id, conversation_id, customer_phone), eta=gio - timedelta(hours=7))
    return "init_campaign"


@celery.task(name='test_init_campaign')
def test_init_campaign(number_of_calls, list_customer_phone):
    # khoi tao chien dich
    campaign_data = {
        'name': f'Chiến dịch {number_of_calls} cuộc gọi',
        'number_of_calls': number_of_calls,
        'status': 'da_khoi_tao',
        'created_at': api.getNOW()
    }
    x = mydb.test_campaign.insert_one(campaign_data)
    campaign_id = str(x.inserted_id)
    for customer_phone in list_customer_phone:
        phone_data = {
            'campaign_id': campaign_id,
            'customer_phone': customer_phone,
            'status': 'chua_goi',
            'created_at': api.getNOW()
        }
        mydb.test_smartbot_webhook.insert_one(phone_data)

    # KHOI TAO CUOC GOI
    mydb.test_campaign.update_one({'_id': ObjectId(campaign_id)}, {
                                  '$set': {'status': 'dang_chay'}})
    list_call_params = mydb.test_smartbot_webhook.find(
        {'campaign_id': campaign_id, 'status': 'chua_goi'})
    for call_params in list_call_params:
        customer_phone = call_params.get('customer_phone')
        response = {'status': 0, 'message': 'success',
                    'conversation_id': f'{campaign_id}_{customer_phone}'}
        if response.get('status') == 0:
            mydb.test_smartbot_webhook.update_one({'campaign_id': campaign_id, 'customer_phone': customer_phone},
                                                  {'$set': {'status': 'da_khoi_tao', 'conversation_id': response.get('conversation_id'), 'khoi_tao_luc': api.getNOW()}})
        time.sleep(0.5)
    mydb.test_campaign.update_one({'_id': ObjectId(campaign_id)}, {
                                  '$set': {'status': 'hoan_thanh'}})
    filter = {
        'campaign_id': campaign_id,
        'status': 'da_khoi_tao',
        'conversation_id': {'$ne': ''}
    }
    start = datetime.now()
    list_gio_goi_ra = pd.date_range(start, periods=number_of_calls, freq="1s")

    customers = mydb.test_smartbot_webhook.find(filter)
    for index, customer in enumerate(customers):
        customer_phone = customer.get('customer_phone')
        conversation_id = customer.get('conversation_id')
        gio_goi_ra = list_gio_goi_ra[index]
        eta = gio_goi_ra
        # Uncomment when develop
        # eta= gio_goi_ra - timedelta(hours=7)
        filter['customer_phone'] = customer_phone
        mydb.test_smartbot_webhook.update_one(
            filter, {'$set': {'gio_goi_ra': eta.timestamp()}})
        celery.send_task(name='test_callout_safe', args=(
            campaign_id, conversation_id, customer_phone), eta=eta)

    return "init_campaign"


@celery.task(name='test_callout_safe')
def test_callout_safe(campaign_id, conversation_id, customer_phone):
    filter = {
        'campaign_id': campaign_id,
        'status': 'da_khoi_tao',
        'conversation_id': {'$ne': ''}
    }
    response = {'status': 0, 'msg': 'Success'}
    if response.get('status') == 0:
        filter['customer_phone'] = customer_phone
        mydb.test_smartbot_webhook.update_one(
            filter, {'$set': {'status': 'dang_goi', 'call_at': api.getNOW()}})
    return "callout_safe"


@celery.task(name='test_call')
def test_call(number_of_calls, delay):
    x = mydb.test_call.insert_one({
        'name': f'Chiến dịch {number_of_calls} cuộc gọi',
        'number_of_calls': number_of_calls,
        'delay': delay,
        'created_at': api.getNOW(),
    })
    campaign_id = str(x.inserted_id)
    start = datetime.now()
    eta = start + timedelta(seconds=delay)
    # eta = eta - timedelta(hours=7)
    for i in range(number_of_calls):
        random_phone = api.convert_phone_number(
            str(100000000+i))
        insert_data = {
            'campaign_id': campaign_id,
            'customer_phone': random_phone,
            'created_at': api.getNOW(),
            'khoi_tao_luc': api.getNOW(),
            'status': 'da_khoi_tao',
            'gio_goi_ra': eta.timestamp(),
        }
        mydb.test_smartbot_webhook.insert_one(insert_data)
        conversation_id = 'conver'
        customer_phone = random_phone
        celery.send_task(name='test_callout_safe', args=(
            campaign_id, conversation_id, customer_phone), eta=eta)
    return 'test_call'

@celery.task(name='call_again')
def call_again(conversation_id, client_id):
    api_key = mydb.clients.find_one(
        {'_id': ObjectId(client_id)}).get('api_key')
    token = api.get_token_nextiva(api_key)
    response = api.make_call_bot_v3_callout_safe(conversation_id, token)
    return response
    # return 'call_again'