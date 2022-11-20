from mongo_connect import mongo_create
import setting
from bson import ObjectId
import time
from datetime import datetime, date, timedelta

mydb = mongo_create()


def bot_108(client_id, campaign_id):
    count_call_total = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 108})
    count_call_success = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 108,
         '$or': [{'response.call_status': 100}, {'response.call_status': 101}]})
    count_call_fail = count_call_total - count_call_success
    da_vay = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 108,
         'response.bot_report.da_vay': "Đã vay"})
    co_nhu_cau = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 108,
         'response.bot_report.nhu_cau_vay': "Có nhu cầu"})
    khong_co_nhu_cau = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 108,
         'response.bot_report.nhu_cau_vay': "Không có nhu cầu"})
    statistics = [
        {
            'name': 'Tổng số cuộc gọi',
            'value': count_call_total,
            'bg_color': 'info'
        },
        {
            'name': 'Số cuộc gọi thành công',
            'value': count_call_success,
            'bg_color': 'success'
        },
        {
            'name': 'Số cuộc gọi thất bại',
            'value': count_call_fail,
            'bg_color': 'danger'
        },
        {
            'name': 'Số khách hàng đã vay',
            'value': da_vay,
            'bg_color': 'warning'
        },
        {
            'name': 'Số khách hàng có nhu cầu vay',
            'value': co_nhu_cau,
            'bg_color': 'primary'
        },
        {
            'name': 'Số khách hàng không có nhu cầu vay',
            'value': khong_co_nhu_cau,
            'bg_color': 'secondary'
        }
    ]

    return statistics


def bot_98(client_id, campaign_id):
    count_call_total = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 98})
    count_call_success = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 98,
         '$or': [{'response.call_status': 100}, {'response.call_status': 101}]})
    count_call_fail = count_call_total - count_call_success
    count_users_di_qua_vung_dich = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 98,
         'response.bot_report.di_qua_vung_dich': "Có"})
    count_users_tiep_xuc_f_012 = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 98,
         'response.bot_report.tiep_xuc_f_012': "Có"})
    count_users_trieu_chung = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 98,
         'response.bot_report.trieu_chung': "Có"})
    statistics = [
        {
            'name': 'Tổng số cuộc gọi',
            'value': count_call_total,
            'bg_color': 'info'
        },
        {
            'name': 'Số cuộc gọi thành công',
            'value': count_call_success,
            'bg_color': 'success'
        },
        {
            'name': 'Số cuộc gọi thất bại',
            'value': count_call_fail,
            'bg_color': 'danger'
        },
        {
            'name': 'Số thuê bao đi qua vùng dịch',
            'value': count_users_di_qua_vung_dich,
            'bg_color': 'warning'
        },
        {
            'name': 'Số thuê bao tiếp xúc với F0/F1/F2',
            'value': count_users_tiep_xuc_f_012,
            'bg_color': 'primary'
        },
        {
            'name': 'Số thuê bao có triệu chứng',
            'value': count_users_trieu_chung,
            'bg_color': 'secondary'
        }
    ]

    return statistics


def bot_81(client_id, campaign_id):
    count_call_total = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 81})
    count_call_success = mydb.poc.count_documents(
        {'user_id': client_id, 'origin_request': campaign_id, 'response.botId': 81,
         '$or': [{'response.call_status': 100}, {'response.call_status': 101}]})
    count_call_fail = count_call_total - count_call_success
    statistics = [
        {
            'name': 'Tổng số cuộc gọi',
            'value': count_call_total,
            'bg_color': 'info'
        },
        {
            'name': 'Số cuộc gọi thành công',
            'value': count_call_success,
            'bg_color': 'success'
        },
        {
            'name': 'Số cuộc gọi thất bại',
            'value': count_call_fail,
            'bg_color': 'danger'
        }
    ]

    return statistics


def bot_124(client_id, campaign_id):
    count_users = mydb.poc.count_documents(
        {'username': 'Demo Call Callback', 'response.callbot_id': 124, "response.event_type": {'$ne': 'create_callin'}})
    count_users_success = mydb.poc.count_documents(
        {'username': 'Demo Call Callback', 'response.callbot_id': 124, "response.event_type": {'$ne': 'create_callin'},
         'response.report.registration_status': "Thành công"})
    count_users_fail = count_users - count_users_success
    statistics = [
        {
            'name': 'Tổng số cuộc gọi',
            'value': count_users,
            'bg_color': 'info'
        },
        {
            'name': 'Số cuộc gọi đăng ký thành công',
            'value': count_users_success,
            'bg_color': 'success'
        },
        {
            'name': 'Số cuộc gọi đăng ký thất bại',
            'value': count_users_fail,
            'bg_color': 'danger'
        }
    ]
    return statistics


def get_count_contacts(client_id, start, end, status=None):
    if type(start) is str:
        start = time.mktime(datetime.strptime(
            start, "%Y/%m/%d %H:%M:%S").timetuple())
    if type(end) is str:
        end = time.mktime(datetime.strptime(
            end, "%Y/%m/%d %H:%M:%S").timetuple())

    filter = {
        'client_id': ObjectId(client_id),
        'created_at': {'$gte': start, '$lte': end}
    }
    if status:
        filter['status'] = status
    total = mydb.smartbot_contacts.count_documents(filter)
    return total


def get_count_campaigns(client_id, start, end, status=None):
    if type(start) is str:
        start = time.mktime(datetime.strptime(
            start, "%Y/%m/%d %H:%M:%S").timetuple())
    if type(end) is str:
        end = time.mktime(datetime.strptime(
            end, "%Y/%m/%d %H:%M:%S").timetuple())

    filter = {
        'client_id': ObjectId(client_id),
        'created_at': {'$gte': start, '$lte': end}
    }
    if status:
        filter['status'] = status
    total_callin_campaigns = mydb.smartbot_callin_campaigns.count_documents(
        filter)
    total_callout_campaigns = mydb.smartbot_callout_campaigns.count_documents(
        filter)
    return total_callin_campaigns + total_callout_campaigns


def get_count_calls(client_id, start, end, status=None):
    if type(start) is str:
        start = time.mktime(datetime.strptime(
            start, "%Y/%m/%d %H:%M:%S").timetuple())
    if type(end) is str:
        end = time.mktime(datetime.strptime(
            end, "%Y/%m/%d %H:%M:%S").timetuple())

    if len(str(start)) == 13:
        start = start / 1000
    if len(str(end)) == 13:
        end = end / 1000
    filter = {
        'client_id': client_id,
        'event_type': 'end_call',
        'created_at': {'$gte': start, '$lte': end}
    }
    if status:
        filter['status'] = status

    count_calls = mydb.smartbot_webhook.count_documents(filter)
    return count_calls


def get_timeline():
    last_day_of_prev_month = datetime.today().replace(
        day=1, hour=0, minute=0, second=0) - timedelta(days=1)
    start_day_of_prev_month = datetime.today().replace(
        day=1, hour=0, minute=0, second=0) - timedelta(days=last_day_of_prev_month.day)
    start_day_of_this_month = last_day_of_prev_month + timedelta(days=1)

    result = {
        'last_day_of_prev_month': last_day_of_prev_month.timestamp(),
        'start_day_of_prev_month': start_day_of_prev_month.timestamp(),
        'start_day_of_this_month': start_day_of_this_month.timestamp()
    }
    return result


def get_first_day_of_month(month):
    if month <= 0:
        first_day = datetime.now().replace(month=1, day=1, hour=0, minute=0,
                                           second=0, microsecond=0) - timedelta(days=31)
    elif month < 13:
        first_day = datetime.now().replace(month=month, day=1, hour=0,
                                           minute=0, second=0, microsecond=0)
    else:
        first_day = datetime.now().replace(month=12, day=31, hour=0, minute=0,
                                           second=0, microsecond=0) + timedelta(days=1)
    return first_day


def get_name_package(client_id):
    service_id = mydb.services.find_one({"sign": 'callbot'}).get('_id')
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == str(service_id):
            name_package = service.get('name_package')
            return name_package
    return False


def get_remaining_call(client_id):
    service_id = mydb.services.find_one({"sign": 'callbot'}).get('_id')
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == str(service_id):
            remaining_call = service.get('remaining_call')
            return remaining_call
    return False


def calc_dashboard_by_month(client_id, month):
    if month == 'all':
        start = 0
        end = datetime.now().timestamp()
    else:
        start = get_first_day_of_month(month).timestamp()
        end = get_first_day_of_month(month+1).timestamp()

    tong_lien_he = get_count_contacts(client_id, start, end)
    da_goi = get_count_contacts(client_id, start, end, "da_goi")
    chua_goi = get_count_contacts(client_id, start, end, "chua_goi")
    tong_chien_dich = get_count_campaigns(client_id, start, end)
    hoan_thanh = get_count_campaigns(client_id, start, end, 'hoan_thanh')
    dang_chay = get_count_campaigns(client_id, start, end, 'dang_chay')
    tong_cuoc_goi = get_count_calls(client_id, start, end)
    thanh_cong = get_count_calls(client_id, start, end, {'$in': [100, 101]})
    that_bai = get_count_calls(client_id, start, end, {'$nin': [100, 101]})

    this_stat = {
        'tong_lien_he': tong_lien_he,
        'da_goi': da_goi,
        'chua_goi': chua_goi,
        'tong_chien_dich': tong_chien_dich,
        'hoan_thanh': hoan_thanh,
        'dang_chay': dang_chay,
        'tong_cuoc_goi': tong_cuoc_goi,
        'thanh_cong': thanh_cong,
        'that_bai': that_bai
    }
    return this_stat


def calc_percentage_change(this_month, prev_month):
    if prev_month == 0 and this_month == 0:
        return 0
    elif prev_month == 0:
        return 100
    elif this_month == 0:
        return -100
    percentage = int((this_month - prev_month)/prev_month * 100)
    return percentage


def get_statistic_campaigns(campaign_id):
    filter = {
        'campaign_id': campaign_id,
        '$or': [
            {'event_type': 'converted_audio', 'status': {'$in': [100, 101]}},
            {'status': {
                '$nin': [100, 101, 'chua_goi', 'da_goi', 'da_khoi_tao']}},
        ]
    }

    filter_cuoc_goi_thanh_cong = {
        'campaign_id': campaign_id,
        '$or': [
            {'event_type': 'converted_audio', 'status': {'$in': [100, 101]}},
        ]
    }
    danh_sach_cuoc_goi_thanh_cong = mydb.smartbot_webhook.find(
        filter_cuoc_goi_thanh_cong)
    so_cuoc_goi_thanh_cong = mydb.smartbot_webhook.count_documents(
        filter_cuoc_goi_thanh_cong)

    thoi_gian_goi_it_hon_5s = 0
    thoi_gian_goi_tu_5_den_10s = 0
    thoi_gian_goi_nhieu_hon_10s = 0

    thoi_gian_cho_it_hon_5s = 0
    thoi_gian_cho_tu_5_den_10s = 0
    thoi_gian_cho_nhieu_hon_10s = 0

    tong_thoi_gian_cho = 0
    tong_thoi_gian_goi = 0
    for rec in danh_sach_cuoc_goi_thanh_cong:
        call_at = rec.get('call_at')
        pickup_at = rec.get('pickup_at')
        hangup_at = rec.get('hangup_at')
        thoi_gian_cho = (pickup_at - call_at)/1000
        thoi_gian_goi = (hangup_at - pickup_at)/1000

        if thoi_gian_goi < 5:
            thoi_gian_goi_it_hon_5s += 1
        elif thoi_gian_goi <= 10:
            thoi_gian_goi_tu_5_den_10s += 1
        else:
            thoi_gian_goi_nhieu_hon_10s += 1

        if thoi_gian_cho < 5:
            thoi_gian_cho_it_hon_5s += 1
        elif thoi_gian_cho <= 10:
            thoi_gian_cho_tu_5_den_10s += 1
        else:
            thoi_gian_cho_nhieu_hon_10s += 1

        tong_thoi_gian_cho += thoi_gian_cho
        tong_thoi_gian_goi += thoi_gian_goi

    so_cuoc_goi = mydb.smartbot_webhook.count_documents(filter)
    thoi_gian_goi_trung_binh = int(
        tong_thoi_gian_goi / so_cuoc_goi_thanh_cong) if so_cuoc_goi_thanh_cong > 0 else 0
    thoi_gian_cho_trung_binh = int(
        tong_thoi_gian_cho / so_cuoc_goi_thanh_cong) if so_cuoc_goi_thanh_cong > 0 else 0

    chua_goi = mydb.smartbot_webhook.count_documents(
        {'campaign_id': campaign_id, 'status': {'$in': ['chua_goi', 'da_khoi_tao']}})
    thanh_cong = mydb.smartbot_webhook.count_documents(
        {'campaign_id': campaign_id, 'event_type': 'end_call', 'status': {'$in': [100, 'da_goi']}})
    khach_hang_cup_may_giua_chung = mydb.smartbot_webhook.count_documents(
        {'campaign_id': campaign_id, 'event_type': 'end_call', 'status': 101})
    cuoc_goi_duoc_chuyen_tiep = mydb.smartbot_webhook.count_documents(
        {'campaign_id': campaign_id, 'event_type': 'end_call', 'status': 102})
    khong_nghe_may = mydb.smartbot_webhook.count_documents(
        {'campaign_id': campaign_id, 'event_type': 'end_call', 'status': 103})
    khong_lien_lac_duoc = mydb.smartbot_webhook.count_documents(
        {'campaign_id': campaign_id, 'event_type': 'end_call', 'status': 104})
    he_thong_loi = mydb.smartbot_webhook.count_documents(
        {'campaign_id': campaign_id, 'event_type': 'end_call', 'status': 105})
    chua_khoi_tao = mydb.smartbot_webhook.count_documents(
        {'campaign_id': campaign_id, 'status': 'chua_goi'})
    da_khoi_tao = mydb.smartbot_webhook.count_documents(
        {'campaign_id': campaign_id, 'status': 'da_khoi_tao'})

    stat = {
        'so_cuoc_goi': so_cuoc_goi,
        'thoi_gian_goi_trung_binh': thoi_gian_goi_trung_binh,
        'thoi_gian_cho_trung_binh': thoi_gian_cho_trung_binh,
        'chua_goi': chua_goi,
        'thanh_cong': thanh_cong,
        'khach_hang_cup_may_giua_chung': khach_hang_cup_may_giua_chung,
        'cuoc_goi_duoc_chuyen_tiep': cuoc_goi_duoc_chuyen_tiep,
        'khong_nghe_may': khong_nghe_may,
        'khong_lien_lac_duoc': khong_lien_lac_duoc,
        'he_thong_loi': he_thong_loi,
        'thoi_gian_goi_it_hon_5s': thoi_gian_goi_it_hon_5s,
        'thoi_gian_goi_tu_5_den_10s': thoi_gian_goi_tu_5_den_10s,
        'thoi_gian_goi_nhieu_hon_10s': thoi_gian_goi_nhieu_hon_10s,
        'thoi_gian_cho_it_hon_5s': thoi_gian_cho_it_hon_5s,
        'thoi_gian_cho_tu_5_den_10s': thoi_gian_cho_tu_5_den_10s,
        'thoi_gian_cho_nhieu_hon_10s': thoi_gian_cho_nhieu_hon_10s,
        'chua_khoi_tao': chua_khoi_tao,
        'da_khoi_tao': da_khoi_tao,
    }
    return stat


def get_statistic_bot_report(campaign_id):
    REPORT_DICT = setting.REPORT_DICT
    filter = {
        'campaign_id': campaign_id,
        'event_type': 'converted_audio',
    }
    recs = mydb.smartbot_webhook.find(filter)
    stat = {}
    for rec in recs:
        report = rec.get('report')
        for key, value in report.items():
            key = str(key)
            value = str(value)
            new_dict = stat.get(key) if stat.get(key) else {}
            if value in new_dict:
                count = new_dict.get(value)
                count += 1
                new_dict[value] = count
            else:
                new_dict[value] = 1
            stat[key] = new_dict
    converted_key = {}
    for key in stat:
        if key in REPORT_DICT:
            converted_key[REPORT_DICT.get(key)] = stat.get(key)

    return converted_key


def get_statistic_bot_124(campaign_id):
    filter_thanh_cong = {
        'response.callbot_id': 124,
        "response.event_type": {'$ne': 'create_callin'}
    }
    danh_sach_cuoc_goi_thanh_cong = mydb.poc.find(filter_thanh_cong)
    tong_thoi_gian_cho = 0
    tong_thoi_gian_goi = 0
    for rec in danh_sach_cuoc_goi_thanh_cong:
        rec = rec.get('response')
        call_at = rec.get('call_at')
        pickup_at = rec.get('pickup_at')
        hangup_at = rec.get('hangup_at')
        thoi_gian_cho = (pickup_at - call_at)/1000
        thoi_gian_goi = (hangup_at - pickup_at)/1000
        tong_thoi_gian_cho += thoi_gian_cho
        tong_thoi_gian_goi += thoi_gian_goi

    so_cuoc_goi_thanh_cong = mydb.poc.count_documents(filter_thanh_cong)
    thoi_gian_goi_trung_binh = int(
        tong_thoi_gian_goi / so_cuoc_goi_thanh_cong) if so_cuoc_goi_thanh_cong > 0 else 0
    thoi_gian_cho_trung_binh = int(
        tong_thoi_gian_cho / so_cuoc_goi_thanh_cong) if so_cuoc_goi_thanh_cong > 0 else 0
    dang_ky_thanh_cong = mydb.poc.count_documents({'response.callbot_id': 124, "response.event_type": {
                                                  '$ne': 'create_callin'}, 'response.report.registration_status': 'Thành công'})
    dang_ky_that_bai = mydb.poc.count_documents({'response.callbot_id': 124, "response.event_type": {
                                                '$ne': 'create_callin'}, 'response.report.registration_status': {'$ne': 'Thành công'}})
    da_co_tai_khoan = mydb.poc.count_documents({'response.callbot_id': 124, "response.event_type": {
                                               '$ne': 'create_callin'}, 'response.report.have_account': 'Có'})
    chua_co_tai_khoan = mydb.poc.count_documents({'response.callbot_id': 124, "response.event_type": {
                                                 '$ne': 'create_callin'}, 'response.report.have_account': {'$ne': 'Có'}})

    stat = {
        'so_cuoc_goi': so_cuoc_goi_thanh_cong,
        'thoi_gian_goi_trung_binh': thoi_gian_goi_trung_binh,
        'thoi_gian_cho_trung_binh': thoi_gian_cho_trung_binh,
        'dang_ky_thanh_cong': dang_ky_thanh_cong,
        'dang_ky_that_bai': dang_ky_that_bai,
        'da_co_tai_khoan': da_co_tai_khoan,
        'chua_co_tai_khoan': chua_co_tai_khoan,
    }
    return stat
