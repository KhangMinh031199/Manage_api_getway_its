from Manage.mongo_connect import mydb

id='241142961'
name_service='siv2'
request = "{\"ID\":\"" + id + "\"}"
def check_identification_in_db(user_id, name_service, request):
    service_is_exist = mydb.user_identification.find_one(
        {"user_id": user_id, "services.name_service": name_service, "services.request": request})
    if service_is_exist:
        print("a")
    else:
        print("b")

check_identification_in_db(id, name_service, request)