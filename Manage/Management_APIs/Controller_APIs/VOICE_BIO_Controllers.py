from Manage.mongo_connect import mongo_create
from bson.objectid import ObjectId

mydb=mongo_create()
def get_remaining_voice(client_id, service_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_voice = service.get('remaining_voice')
            return remaining_voice
    return False

def decrease_remaining_voice(client_id, service_id):
    if not isinstance(client_id, ObjectId):
        client_id = ObjectId(client_id)
    services = mydb.clients.find_one({'_id': client_id}).get('services')
    if services is None:
        return False
    for service in services:
        if service.get('service_id') == service_id:
            remaining_voice = service.get('remaining_voice')
            if remaining_voice == -1 or remaining_voice == 0:
                return True
            newvalue = remaining_voice - 1
            mydb.clients.update_one({'_id': client_id, 'services.service_id': service_id},
                                    {"$set": {'services.$.remaining_voice': newvalue}})
            return True
    return False

def get_link_function_voicebio(apifunction):
    voicebio = mydb.services.find_one({"sign": "voicebio"})
    for x in voicebio.get("api_routing"):
        if x.get("api_function") == apifunction:
            return x.get('link')


def get_message_error_voicebio(code):
    if code == 1:
        error = "Nói không rõ từ. Vui lòng nói rõ hơn"
    elif code == 2:
        error = "Nói quá nhỏ. Vui lòng nói to hơn"
    elif code == 3:
        error = "Môi trường nhiễu. Vui lòng ghi âm ở môi trường yên tĩnh hơn"
    elif code == 4:
        error = "Độ dài audio không đủ 2s. Vui lòng ghi âm dài hơn"
    elif code == 5:
        error = "Nói không đủ số lượng từ tối thiểu. Vui lòng nói nhiều từ hơn"
    elif code == 6:
        error = "Độ dài audio quá dài (hơn 20p). Vui lòng ghi âm ngắn hơn"
    else:
        error = "Lỗi khác"
    return error