from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from carsharing_req .models import CarsharUserModel, UsageModel, UserFavoriteCarModel
from parking_req .models import ParkingUserModel, ParkingUsageModel
from owners_req .models import ParentCategory, Category, CarInfoParkingModel, CarInfoModel
from carsharing_booking .models import BookingModel
from parking_booking .models import ParkingBookingModel
from .forms import BookingCreateForm, CarCategory
import json
import datetime, locale
import collections
from django.contrib import messages
from django.db.models import Q
from django.core.mail import EmailMessage
# Create your views here.


def select(request):
    return render(request, "carsharing_booking/index.html", {
        "title": 'カーシェアリング予約',
    })

def test_ajax_app(request):
    if str(request.user) == "AnonymousUser":
        print('ゲスト')
    else:
        print(request.user)
    hoge = "Hello Django!!"

    return render(request, "carsharing_booking/ajax.html", {
        "hoge": hoge,
    })


def map(request):
    add = setAdd(request)
    set_list = CarInfoParkingModel.objects.values("parking_id")
    item_all = ParkingUserModel.objects.filter(id__in=set_list)
    item = item_all.values("id", "address", "user_id", "lat", "lng")
    item_list = list(item.all())
    data = {
        'markerData': item_list,
    }
    params = {
        'title': '自宅付近で検索',
        'name': '自宅',
        'add': add,
        'data_json': json.dumps(data),
        'latlng': 'undefined'
    }
    if (request.method == 'POST'):
        params['title'] = '検索地付近で検索'
        params['add'] = request.POST['add']
        params['name'] = '検索'
    return render(request, "carsharing_booking/map.html", params)

def geo(request):
    params = {
        'title': '現在地付近で検索',
        'name': '自宅',
        'add': '',
        'data_json': '',
        'latlng': 'undefined'
    }
    if (request.method == 'POST'):
        if len(request.POST) == 4:
            params['name'] = '現在地'
            params['latlng'] = str(request.POST['latlng'])
            params['lat'] = str(request.POST['lat'])
            params['lng'] = str(request.POST['lng'])
        elif len(request.POST) == 2:
            if request.POST['error'] == '1':
                msg = "位置情報の利用が許可されていません。"
            elif request.POST['error'] == '2':
                msg = "デバイスの位置が判定できませんでした。"
            elif request.POST['error'] == '3':
                msg = "タイムアウトが発生しました。"
            messages.error(request, msg)
            params['add'] = setAdd(request)
            params['name'] = ''
        else:
            messages.error(request, '位置情報が正しく取得出来ませんでした。')
            params['add'] = setAdd(request)
            params['name'] = ''
        set_list = CarInfoParkingModel.objects.values("parking_id")
        item_all = ParkingUserModel.objects.filter(id__in=set_list)
        item = item_all.values("id", "address", "user_id", "lat", "lng")
        item_list = list(item.all())
        data = {
            'markerData': item_list,
        }
        params['data_json'] = json.dumps(data)
    
    return render(request, "carsharing_booking/map.html", params)

def setAdd(request):
    if request.user.id == None:
        add = '〒277-0005 千葉県柏市柏１丁目１−１'
    else:
        data = CarsharUserModel.objects.get(id=request.session['user_id'])
        print(data.pref01+data.addr01+data.addr02)
        add = data.pref01+data.addr01+data.addr02
    return add

def car(request):
    max_num = Category.objects.order_by('id').last()
    max_num = int(max_num.id) + 1
    # print(max_num)
    set_QuerySet_car = CarInfoParkingModel.objects.values("car_id")
    item_all = CarInfoModel.objects.filter(id__in=set_QuerySet_car).order_by('parent_category', 'category')
    # print(set_QuerySet_car)
    # set_QuerySet_parking = CarInfoParkingModel.objects.values("parking_id", "car_id")
    # print(set_QuerySet_parking)
    # addadd = {}
    # for index in set_QuerySet_parking:
    #     address = list(ParkingUserModel.objects.filter(id=index['parking_id']).values("address"))
    #     address = address[0]['address']
    #     index = index['car_id']
    #     addadd.setdefault(index, address)
    # print(addadd)
    # print(item_all.values('category'))
    dict_car = {}
    for key in range(1, max_num):
        print(key)
        value = list(CarInfoModel.objects.select_related('parent_category__parent_category').select_related('category__category').filter(category=key).values('id', 'parent_category__parent_category', 'category__category', 'model_id', 'people', 'used_years'))
        if not value :
            print(key)
            print('空')
        else:
            print('key')
            print(key)
            print('len')
            print(len(value))
            for num in range(1, len(value)+1):
                print('num')
                print(num)
                print(value)
                if num == 1:
                    print(value[0])
                    parking = CarInfoParkingModel.objects.get(car_id_id=int(value[0]['id']))
                    address = ParkingUserModel.objects.get(id=parking.parking_id_id)
                    value[0]['address'] = address.address
                elif num <= len(value):
                    print(value[num-1])
                    parking = CarInfoParkingModel.objects.get(car_id_id=int(value[num-1]['id']))
                    address = ParkingUserModel.objects.get(id=parking.parking_id_id)
                    value[num-1]['address'] = address.address
                # if num == 1:
                #     value[0]['address'] = addadd[value[0]['id']]
                #     print(value[0])
                # else:
                #     value[num-1]['address'] = addadd[value[num-1]['id']]
        dict_car.setdefault(key, value)
        # print(key, value)

    print(dict_car)
    params = {
        'title': '車から検索',
        'car_obj': item_all,
        'form': CarCategory(),
        'parentcategory_list': list(ParentCategory.objects.all()),
        'category_set': list(Category.objects.all().values()),
        'json_car': json.dumps(dict_car, ensure_ascii=False)
    }
    # print(list(Category.objects.all().values()))
    return render(request, "carsharing_booking/car.html", params)

    # print(dict_car)
    params = {
        'car_obj': item_all,
        'form': CarCategory(),
        'parentcategory_list': list(ParentCategory.objects.all()),
        'category_set': list(Category.objects.all().values()),
        'json_car': json.dumps(dict_car, ensure_ascii=False)
    }
    return render(request, "carsharing_booking/car.html", params)

def selectcar(request):
    if str(request.user) == "AnonymousUser":
        user_id = 'ゲスト'
    else:
        user_id = request.session['user_id']
    if (request.method == 'POST'):
        mydict = dict(request.POST)
        car_data = selectcardataset(mydict, user_id)
        request.session['select'] = car_data
    else:
        car_data = request.session['select']
        if user_id != 'ゲスト':
            favorite_id_list = list(UserFavoriteCarModel.objects.filter(user_id=user_id).order_by('favorite_car_id_id').values('favorite_car_id_id'))
            print(favorite_id_list)
            for check in car_data:
                check['favorite'] = None
                for favorite_id in favorite_id_list:
                    if favorite_id['favorite_car_id_id'] == check['id']:
                        check['favorite'] = True

    params = {
        'title': '車詳細検索',
        'car_objs': car_data,
        'guest': user_id,
        'flag': len(car_data)
    }
    return render(request, "carsharing_booking/selectcar.html", params)

def selectcardataset(mydict, user_id):
    print(user_id)
    people = (0, 100)
    babysheet = False
    around_view_monitor = False
    car_autonomous = False
    car_nav = False
    etc = False
    non_smoking = False
    if mydict['people'][0] != '':
        people = (int(mydict['people'][0]), int(mydict['people'][0]))
    if mydict['at_mt'][0] == 'AT車':
        at_mt = 'AT'
    elif mydict['at_mt'][0] == 'MT車':
        at_mt = 'MT'
    else:
        at_mt = 'T'
    if mydict.get('option') != None:
        option = True
        option_list = list(mydict['option'])
        car_obj_list = []
        countcheck = 0
        for value in option_list:
            if value == 'babysheet':
                babysheet = True
                tmp = list(CarInfoModel.objects.filter(babysheet=babysheet).values('id'))
                for tmp_id in tmp:
                    car_obj_list.append(tmp_id['id'])
                countcheck += 1
            elif value == 'around_view_monitor':
                around_view_monitor = True
                tmp = list(CarInfoModel.objects.filter(around_view_monitor=around_view_monitor).values('id'))
                for tmp_id in tmp:
                    car_obj_list.append(tmp_id['id'])
                countcheck += 1
            elif value == 'car_autonomous':
                car_autonomous = True
                tmp = list(CarInfoModel.objects.filter(car_autonomous=car_autonomous).values('id'))
                for tmp_id in tmp:
                    car_obj_list.append(tmp_id['id'])
                countcheck += 1
            elif value == 'car_nav':
                car_nav = True
                tmp = list(CarInfoModel.objects.filter(car_nav=car_nav).values('id'))
                for tmp_id in tmp:
                    car_obj_list.append(tmp_id['id'])
                countcheck += 1
            elif value == 'etc':
                etc = True
                tmp = list(CarInfoModel.objects.filter(etc=etc).values('id'))
                for tmp_id in tmp:
                    car_obj_list.append(tmp_id['id'])
                countcheck += 1
            elif value == 'non_smoking':
                non_smoking = True
                tmp = list(CarInfoModel.objects.filter(non_smoking=non_smoking).values('id'))
                for tmp_id in tmp:
                    car_obj_list.append(tmp_id['id'])
                countcheck += 1
        c = collections.Counter(car_obj_list)
        car_obj_list = []
        for tap in c.most_common():
            if tap[1] == countcheck:
                car_obj_list.append(tap[0])
            else:
                break
        print(car_obj_list)
    else:
        option = False
    if mydict.get('category') != None:
        category = int(mydict['category'][0])
        if option == False:
            car_obj = list(CarInfoModel.objects.filter(category_id=category).filter(people__range=people).filter(at_mt__contains=at_mt).values('id'))
        else:
            car_obj = list(CarInfoModel.objects.filter(category_id=category).filter(people__range=people).filter(at_mt__contains=at_mt).filter(id__in=car_obj_list).values('id'))
    else:
        if option == False:
            car_obj = list(CarInfoModel.objects.filter(people__range=people).filter(at_mt__contains=at_mt).values('id'))
        else:
            car_obj = list(CarInfoModel.objects.filter(people__range=people).filter(at_mt__contains=at_mt).filter(id__in=car_obj_list).values('id'))
    car_id_list = []
    for carid in car_obj:
        car_id_list.append(carid.get('id'))
    tmp = list(CarInfoParkingModel.objects.values('car_id'))
    in_list = []
    for carid in tmp:
        in_list.append(carid.get('car_id'))
    exclude_car = list(CarInfoModel.objects.exclude(id__in=in_list).values('id'))
    exclude_car_list = []
    for carid in exclude_car:
        exclude_car_list.append(carid.get('id'))
    for delete in exclude_car_list:
        car_id_list.remove(delete)
    data = list(CarInfoParkingModel.objects.filter(car_id__in=car_id_list).values())
    parking_id_list = []
    for parkingid in data:
        parking_id_list.append(parkingid['parking_id_id'])
    car_data = list(CarInfoModel.objects.select_related('parent_category__parent_category').select_related('category__category').filter(id__in=car_id_list).values('id', 'user_id', 'parent_category__parent_category', 'category__category', 'model_id', 'people', 'tire', 'at_mt', 'babysheet', 'car_nav', 'etc', 'around_view_monitor', 'car_autonomous', 'non_smoking', 'used_mileage', 'used_years', 'img'))
    for num in range(len(car_data)):
        recode = ParkingUserModel.objects.get(id=parking_id_list[num])
        car_data[num]['address'] = recode.address
        car_data[num]['used_mileage'] = "{:,}".format(car_data[num]['used_mileage'])
    if user_id != 'ゲスト':
        favorite_id_list = list(UserFavoriteCarModel.objects.filter(user_id=user_id).order_by('favorite_car_id_id').values('favorite_car_id_id'))
        for check in car_data:
            for favorite_id in favorite_id_list:
                if favorite_id['favorite_car_id_id'] == check['id']:
                    check['favorite'] = True
    print(car_data)
    return car_data


def history(request):
    if str(request.user) == "AnonymousUser":
        messages.error(request, 'ログインしてください。')
        return redirect(to='carsharing_req:index')
    else:
        user_id = request.session['user_id']
    booking = UsageModel.objects.filter(user_id=user_id).exclude(charge=-1).order_by('-end_day', '-end_time').values()
    for item in list(booking):
        num = CarInfoModel.objects.filter(id=item['car_id']).values("category")
        category = Category.objects.get(id=num[0]['category'])
        item['category'] = category.category
        item['parent_category'] = category.parent_category
        parking_id = CarInfoParkingModel.objects.filter(car_id=item['car_id']).values("parking_id")
        p_obj = ParkingUserModel.objects.get(id=parking_id[0]['parking_id'])
        item['parking_id'] = parking_id[0]['parking_id']
        item['address'] = p_obj.address
        item['lat'] = p_obj.lat
        item['lng'] = p_obj.lng
        if item['start_day'] == item['end_day']:
            flag = True
        else:
            flag = False
        item['start_day'] = dateStr(item['start_day'])
        item['start_time'] = timeStr(item['start_time'])
        item['end_day'] = dateStr(item['end_day'])
        item['end_time'] = timeStr(item['end_time'])
        if flag == True:
            item['end_day'] = ''
        item['charge'] = "{:,}".format(item['charge'])
        car_obj = CarInfoModel.objects.get(id=item['car_id'])
        item['img'] = car_obj.img
        print(item)
    count = len(booking)
    params = {
        'title': '履歴から予約',
        'data': booking,
        'count': count
    }
    return render(request, "carsharing_booking/history.html", params)


def favoritelist(request):
    if str(request.user) == "AnonymousUser":
        messages.error(request, 'ログインしてください。')
        return redirect(to='carsharing_req:index')
    else:
        user_id = request.session['user_id']
    favorite_car_dict = list(UserFavoriteCarModel.objects.filter(user_id=user_id).values('favorite_car_id'))
    favorite_car_list = []
    for favorite_car_id in favorite_car_dict:
        favorite_car_list.append(favorite_car_id['favorite_car_id'])
    print(favorite_car_list)
    car_objs = list(CarInfoModel.objects.select_related('parent_category__parent_category').select_related('category__category').filter(id__in=favorite_car_list).values('id', 'user_id', 'parent_category__parent_category', 'category__category', 'model_id', 'people', 'tire', 'at_mt', 'babysheet', 'car_nav', 'etc', 'around_view_monitor', 'car_autonomous', 'non_smoking', 'used_mileage', 'used_years', 'img'))
    count = 1
    for car_obj in car_objs:
        car_obj['count'] = count
        car_obj['car_id'] = car_obj['id']
        setid = CarInfoParkingModel.objects.get(car_id=int(car_obj['id']))
        car_obj['id'] = setid.id
        parikng = ParkingUserModel.objects.get(id=setid.parking_id_id)
        car_obj['parking_id'] = parikng.id
        car_obj['lat'] = parikng.lat
        car_obj['lng'] = parikng.lng
        car_obj['address'] = parikng.address
        count += 1
    print(car_objs)
    params = {
        'title': 'お気に入り',
        'car_objs': car_objs,
        'count': len(car_objs)
    }
    return render(request, "carsharing_booking/favoritelist.html", params)


def booking_car(request, num):
    request.session['select'] = "car"
    if str(request.user) == "AnonymousUser":
        user_id = 'ゲスト'
        guest = True
    else:
        user_id = request.session['user_id']
        guest = False

    if guest == False:
        user_data = CarsharUserModel.objects.get(id=request.session['user_id'])
        my_plan = user_data.plan
    else:
        my_plan = 'guest'
    
    params = {
        'title': '予約',
        'guest': user_id,
        'events': '',
        'car_id': num,
        'form': BookingCreateForm(),
        'car_data': CarInfoModel.objects.get(id=num),
        'status': my_plan
    }
    events = []
    # カーシェアリング予約
    booking = BookingModel.objects.filter(car_id=num).exclude(charge=-1).order_by('end_day', 'end_time')
    booking = booking.values("id", "start_day", "start_time", "end_day", "end_time")
    for obj in booking:
        title = obj.get("id")
        start = obj.get("start_day") + 'T' + obj.get("start_time")
        end = obj.get("end_day") + 'T' + obj.get("end_time")
        event = dict((['title', 'カーシェアリング予約'+str(title)], ['start', start], ['end', end], ['color', '#A9A9A9']))
        events.append(event)
    # 車両貸し出し制限
    loaning = BookingModel.objects.filter(car_id=num, charge=-1).order_by('end_day', 'end_time')
    loaning = loaning.values("id", "start_day", "start_time", "end_day", "end_time")
    for obj in loaning:
        title = obj.get("id")
        start = obj.get("start_day") + 'T' + obj.get("start_time")
        end = obj.get("end_day") + 'T' + obj.get("end_time")
        event = dict((['title', '車両貸し出し'+str(title)], ['start', start], ['end', end], ['color', '#DC143C']))
        events.append(event)

    request.session['events'] = json.dumps(events)
    params['events'] = request.session['events']
    car_obj = CarInfoModel.objects.filter(id=num)
    params['favorite'] = False
    if guest == False:
    # if user_id != 'ゲスト':
        favorite_id_list = list(UserFavoriteCarModel.objects.filter(user_id=user_id, favorite_car_id_id=num).values('favorite_car_id_id'))
        if len(favorite_id_list) != 0:
            request.session['favorite'] = True
        else:
            request.session['favorite'] = False
    else:
        request.session['favorite'] = False
    request.session['car_objs'] = car_obj
    # parking_id = CarInfoParkingModel.objects.filter(car_id=num).values('parking_id')
    # request.session['parking_id'] = parking_id[0]['parking_id']
    request.session['obj_id'] = num
    parking_id = CarInfoParkingModel.objects.filter(id=num).values("parking_id")
    request.session['address'] = ParkingUserModel.objects.get(id=parking_id[0]["parking_id"]).address
    params['address'] = request.session['address']
    params['favorite'] = request.session['favorite']
    return render(request, "carsharing_booking/car_next.html", params)


def booking(request, num):
    request.session['select'] = "map"
    request.session['obj_id'] = num
    if str(request.user) == "AnonymousUser":
        print('ゲスト')
        guest = True
    else:
        print(request.user)
        guest = False
    
    if guest == False:
        user_data = CarsharUserModel.objects.get(id=request.session['user_id'])
        my_plan = user_data.plan
    else:
        my_plan = 'guest'
    
    params = {
        'form': BookingCreateForm(),
        'message': '予約入力',
        'car_objs': '',
        'car_id': '',
        'num': request.session['obj_id'],
        'status': my_plan
    }
    num = request.session['obj_id']
    address = ParkingUserModel.objects.filter(id=request.session['obj_id']).values('address')
    params['address'] = address[0]['address']
    items = CarInfoParkingModel.objects.filter(parking_id=num).values('car_id')
    print(items)
    car_list = []
    for item in items:
        index = item['car_id']
    # params['car_id'] = index
        car_list.append(index)
        car_obj = CarInfoModel.objects.filter(id__in=car_list)
    params['car_objs'] = car_obj
    request.session['car_objs'] = car_obj

    event_dict = {}
    # カーシェアリング予約
    for carnum in car_list:
        events = []
        booking = BookingModel.objects.filter(car_id=carnum).exclude(charge=-1).order_by('end_day', 'end_time')
        booking = booking.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in booking:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', 'カーシェアリング予約'+str(title)], ['start', start], ['end', end], ['color', '#A9A9A9']))
            events.append(event)
        # 車両貸し出し制限
        loaning = BookingModel.objects.filter(car_id=carnum, charge=-1).order_by('end_day', 'end_time')
        loaning = loaning.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in loaning:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', '車両貸し出し'+str(title)], ['start', start], ['end', end], ['color', '#DC143C']))
            events.append(event)
        event_dict[carnum] = events
    request.session['events'] = json.dumps(event_dict)
    params['events'] = request.session['events']
    print(event_dict)

    
    return render(request, 'carsharing_booking/booking.html', params)


def booking_history(request, num):
    pass


def checkBooking(request):
    params = {
        'parking_obj': '',
        'title': 'カーシェアリング予約確認',
        'message': '予約情報確認',
        'data': '',
        'kingaku': '',
        'times': '',
        'car_obj': '',
        'car_objs': request.session['car_objs'],
        'address': '',

    }
    # error時の入力保存しredirect
    if str(request.user) == "AnonymousUser":
        print('ゲスト')
        user_id = 'ゲスト'
    else:
        print(request.user)
        user_id = request.session['user_id']

    if request.session['select'] == 'map':
        address = ParkingUserModel.objects.filter(id=request.session['obj_id']).values('address')
        params['address'] = address[0]['address']
    elif request.session['select'] == 'car':
        params['car_id'] = request.session['obj_id']
        params['address'] = request.session['address']
        params['car_data'] = CarInfoModel.objects.get(id=request.session['obj_id'])
        params['favorite'] = request.session['favorite']
        params['guest'] = user_id
    params['events'] = request.session['events']
    obj = BookingModel()
    c_b = BookingCreateForm(request.POST, instance=obj)
    params['form'] = c_b
        
    

    # POSTデータを変数へ格納
    start_day = request.POST['start_day']
    end_day = request.POST['end_day']
    start_time = request.POST['start_time']
    end_time = request.POST['end_time']

    # POSTデータをdatetime型へ変換
    start = start_day + ' ' + start_time
    start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M')
    print(start)
    print(type(start))
    end = end_day + ' ' + end_time
    end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M')
    print(end)
    print(type(end))

    booking_list = BookingModel.objects.filter(car_id=request.POST['car_id'])
    booking_list = booking_list.filter(Q(start_day=start_day) | Q(start_day=end_day) | Q(end_day=start_day) | Q(end_day=end_day))
    # print(booking_list)
    booking_list = booking_list.values('id', 'start_day', 'start_time', 'end_day', 'end_time')
    for item in booking_list:
        booking_id = item['id']
        booking_sd = item['start_day']
        booking_st = item['start_time']
        booking_ed = item['end_day']
        booking_et = item['end_time']
        print('item')
        print(item)
        booking_start = booking_sd + ' ' + booking_st
        booking_start = datetime.datetime.strptime(booking_start, '%Y-%m-%d %H:%M')
        booking_end = booking_ed + ' ' + booking_et
        booking_end = datetime.datetime.strptime(booking_end, '%Y-%m-%d %H:%M')
        if start <= booking_end and end >= booking_start:
            print("被り！！")
            messages.error(request, '申し訳ございません。その時間帯は既に予約済みです。別の車両にするか時間帯を変更してください。<br>' + datetime.datetime.strftime(booking_start, "%Y年%m月%d日 %H:%M") + ' 〜 ' + datetime.datetime.strftime(booking_end, "%Y年%m月%d日 %H:%M"))
            if request.session['select'] == 'map':
                return render(request, 'carsharing_booking/booking.html', params)
            elif request.session['select'] == 'car':
                return render(request, "carsharing_booking/car_next.html", params)
        else:
            print("大丈夫！")

    print(booking_list)

    # charge = request.POST['charge']
    if str(request.user) == "AnonymousUser":
        print('ゲスト')
        guest = True
    else:
        print(request.user)
        guest = False
    
    if guest == False:
        user_data = CarsharUserModel.objects.get(id=request.session['user_id'])
        my_plan = user_data.plan
    else:
        my_plan = 'guest'
    print(my_plan)

    time = end - start
    d = int(time.days)
    m = int(time.seconds / 60)
    print(d)
    print(int(m))
    charge = 0
    times = ''

    if d <= 0:
        print('1day')
    else:
        print('days')
        daycount = d
        while daycount >= 0:
            if daycount == 1:
                daycount -= 1
                if my_plan == 'a':
                    charge += 8880
                elif my_plan == 'b':
                    charge += 8280
                elif my_plan == 'c':
                    charge += 7180
                elif my_plan == 'guest':
                    charge += 8880
                break
            elif daycount == 2:
                daycount -= 2
                if my_plan == 'a':
                    charge += 14280
                elif my_plan == 'b':
                    charge += 13380
                elif my_plan == 'c':
                    charge += 11480
                elif my_plan == 'guest':
                    charge += 14280
                break
            elif daycount == 3:
                daycount -= 3
                if my_plan == 'a':
                    charge += 20380
                elif my_plan == 'b':
                    charge += 19080
                elif my_plan == 'c':
                    charge += 16380
                elif my_plan == 'guest':
                    charge += 20380
                break
            else:
                daycount -= 3
                if my_plan == 'a':
                    charge += 20380
                elif my_plan == 'b':
                    charge += 19080
                elif my_plan == 'c':
                    charge += 16380
                elif my_plan == 'guest':
                    charge += 20380

        times = str(d) + '日 '

    if start_time < end_time:
        print('tule')
        # charge += int(m / 15 * 225)
        h = int(m / 60)
        hourcount = h
        while hourcount >= 6:
            if hourcount == 6:
                hourcount -= 6
                if my_plan == 'a':
                    charge += 4580
                elif my_plan == 'b':
                    charge += 4280
                elif my_plan == 'c':
                    charge += 3680
                elif my_plan == 'guest':
                    charge += 4580
            elif hourcount == 12:
                hourcount -= 12
                if my_plan == 'a':
                    charge += 6780
                elif my_plan == 'b':
                    charge += 6380
                elif my_plan == 'c':
                    charge += 5480
                elif my_plan == 'guest':
                    charge += 6780
            elif hourcount >= 12:
                hourcount -= 12
                if my_plan == 'a':
                    charge += 6780
                elif my_plan == 'b':
                    charge += 6380
                elif my_plan == 'c':
                    charge += 5480
                elif my_plan == 'guest':
                    charge += 6780
            else:
                hourcount -= 6
                if my_plan == 'a':
                    charge += 4580
                elif my_plan == 'b':
                    charge += 4280
                elif my_plan == 'c':
                    charge += 3680
                elif my_plan == 'guest':
                    charge += 4580
        minutecount = hourcount*60
        m = int(m % 60)
        minutecount += m
        if my_plan == 'a':
            charge += int(minutecount / 15 * 225)
        elif my_plan == 'b':
            charge += int(minutecount / 15 * 210)
        elif my_plan == 'c':
            charge += int(minutecount / 15 * 180)
        elif my_plan == 'guest':
            charge += int(minutecount / 15 * 225)
        x = str(h) + '時間 ' + str(m) + '分'
        if d <= 0:
            if my_plan == 'a':
                if h <= 12 and charge > 6780:
                    charge = 6780
                elif h <= 6 and charge > 4580:
                    charge = 4580
            elif my_plan == 'b':
                if h <= 12 and charge > 6380:
                    charge = 6380
                elif h <= 6 and charge > 4280:
                    charge = 4280
            elif my_plan == 'c':
                if h <= 12 and charge > 5480:
                    charge = 5480
                elif h <= 6 and charge > 3680:
                    charge = 3680
            elif my_plan == 'guest':
                print('g')
                if h <= 12 and charge > 6780:
                    charge = 6780
                elif h <= 6 and charge > 4580:
                    charge = 4580
        times += x
    elif start_time >= end_time and d < 0:
        print('false')
        messages.error(request, '終了時刻が開始時刻よりも前です。')
        if request.session['select'] == 'map':
            return render(request, 'carsharing_booking/booking.html', params)
        elif request.session['select'] == 'car':
            return render(request, "carsharing_booking/car_next.html", params)
    else:
        h = int(m / 60)
        hourcount = h
        while hourcount > 6:
            if hourcount == 6:
                hourcount -= 6
                if my_plan == 'a':
                    charge += 4580
                elif my_plan == 'b':
                    charge += 4280
                elif my_plan == 'c':
                    charge += 3680
                elif my_plan == 'guest':
                    charge += 4580
                break
            elif hourcount == 12:
                hourcount -= 12
                if my_plan == 'a':
                    charge += 6780
                elif my_plan == 'b':
                    charge += 6380
                elif my_plan == 'c':
                    charge += 5480
                elif my_plan == 'guest':
                    charge += 6780
                break
            elif hourcount >= 12:
                hourcount -= 12
                if my_plan == 'a':
                    charge += 6780
                elif my_plan == 'b':
                    charge += 6380
                elif my_plan == 'c':
                    charge += 5480
                elif my_plan == 'guest':
                    charge += 6780
                break
            else:
                hourcount -= 6
                if my_plan == 'a':
                    charge += 4580
                elif my_plan == 'b':
                    charge += 4280
                elif my_plan == 'c':
                    charge += 3680
                elif my_plan == 'guest':
                    charge += 4580
        minutecount = hourcount*60
        m = int(m % 60)
        minutecount += m
        if my_plan == 'a':
            charge += int(minutecount / 15 * 225)
        elif my_plan == 'b':
            charge += int(minutecount / 15 * 210)
        elif my_plan == 'c':
            charge += int(minutecount / 15 * 180)
        elif my_plan == 'guest':
            charge += int(minutecount / 15 * 225)
        x = str(h) + '時間 ' + str(m) + '分'
        if d <= 0:
            if my_plan == 'a':
                if h <= 12 and charge > 6780:
                    charge = 6780
                elif h <= 6 and charge > 4580:
                    charge = 4580
            elif my_plan == 'b':
                if h <= 12 and charge > 6380:
                    charge = 6380
                elif h <= 6 and charge > 4280:
                    charge = 4280
            elif my_plan == 'c':
                if h <= 12 and charge > 5480:
                    charge = 5480
                elif h <= 6 and charge > 3680:
                    charge = 3680
            elif my_plan == 'guest':
                if h <= 12 and charge > 6780:
                    charge = 6780
                elif h <= 6 and charge > 4580:
                    charge = 4580
        times += x
    if d == 0 and m < 15 and h == 0:
        messages.error(request, '15分未満は利用できません。')
        if request.session['select'] == 'map':
            return render(request, 'carsharing_booking/booking.html', params)
        elif request.session['select'] == 'car':
            return render(request, "carsharing_booking/car_next.html", params)
        
    data = {
        'car_id': request.POST['car_id'],
        'start_day': start_day,
        'start_time': start_time,
        'end_day': end_day,
        'end_time': end_time,
        'charge': charge,
    }
    if request.session['select'] == 'map':
        address = ParkingUserModel.objects.filter(id=request.session['obj_id']).values('address')
    elif request.session['select'] == 'car':
        parking_id = CarInfoParkingModel.objects.filter(car_id=request.session['obj_id']).values('parking_id')
        print(parking_id)
        address = ParkingUserModel.objects.filter(id=parking_id[0]['parking_id']).values('address')
        print(address)
    params['address'] = address[0]['address']
    params['kingaku'] = "{:,}".format(charge)
    params['data'] = data
    params['times'] = times
    params['car_obj'] = CarInfoModel.objects.get(id=request.POST['car_id'])
    messages.warning(request, 'まだ予約完了しておりません。<br>こちらの内容で宜しければ確定ボタンをクリックして下さい。')
    return render(request, "carsharing_booking/check.html", params)

def push(request):
    if str(request.user) == "AnonymousUser":
        messages.error(request, 'ログインしてください。')
        return redirect(to='carsharing_req:index')
    if (request.method == 'POST'):
        user_id = int(request.session['user_id'])
        car_id = int(request.POST['car_id'])
        start_day = request.POST['start_day']
        end_day = request.POST['end_day']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        charge = int(request.POST['charge'])
        record = BookingModel(user_id=user_id, car_id=car_id, start_day=start_day, start_time=start_time, end_day=end_day, end_time=end_time, charge=charge)
        record.save()
        del request.session['events']
        del request.session['car_objs']
        del request.session['obj_id']
        del request.session['select']
        request.session['favorite'] = "none"
        del request.session['favorite']
        messages.success(request, '予約が完了しました。<br>ご登録されているメールアドレスに予約完了メールを送信致しました。ご確認下さい。')
        #mail送信メソッドの呼び出し
        success_booking_mail(request, charge, start_day, start_time, end_day, end_time)
    else:
        messages.error(request, '不正なリクエストです')
    return redirect(to='/carsharing_booking/reservation')


def success_booking_mail(request, charge, start_day, start_time, end_day, end_time):

    subject = "予約完了確認メール"
    path = request.build_absolute_uri()
    url = path[:-5] + 'list/'
    message = str(request.user) + "様\n \
        ご予約ありがとうございます。\n \
        お手続きが完了いたしました。\n\n \
        開始日:" + start_day + "\n \
        開始時刻:" + start_time + "\n \
        終了日:" + end_day + "\n \
        終了時刻:" + end_time + "\n \
        料金:" + str(charge) + "円\n\n \
        予約詳細はコチラから！！\n \
        URL: " + url + "\n"
    user = request.user  # ログインユーザーを取得する
    from_email = 's.kawanishi291@gmail.com'  # 送信者
    user.email_user(subject, message, from_email)  # メールの送信
    pass

def favorite(request, flag, num):
    first = len(list(UserFavoriteCarModel.objects.filter(user_id=request.session['user_id'], favorite_car_id_id=num)))
    if first == 0:
        record = UserFavoriteCarModel(user_id=request.session['user_id'], favorite_car_id_id=num)
        print('record_save')
        record.save()
        messages.success(request, 'お気に入りに追加しました。')
    else:
        record = UserFavoriteCarModel.objects.filter(user_id=request.session['user_id'], favorite_car_id_id=num)
        print('recode_delete')
        record.delete()
        messages.success(request, 'お気に入りから削除しました。')
    if flag == 'serect':
        return redirect(to='carsharing_booking:selectcar')
    elif flag == 'bookingcar':
        return redirect(to='carsharing_booking:booking_car', num=num)
    elif flag == 'favorites':
        return redirect(to='carsharing_booking:favoritelist')

def reservation(request):
    booking = BookingModel.objects.filter(user_id=request.session['user_id']).values('id', 'car_id', 'start_day', 'start_time', 'end_day', 'end_time', 'charge').last()
    data = {
        'car_id': booking['car_id'],
        'start_day': booking['start_day'],
        'start_time': booking['start_time'],
        'end_day': booking['end_day'],
        'end_time': booking['end_time'],
        'charge': booking['charge'],
    }
    car_obj = CarInfoModel.objects.get(id=booking['car_id'])
    parking_id = CarInfoParkingModel.objects.filter(car_id=booking['car_id']).values('parking_id')
    address = ParkingUserModel.objects.filter(id=parking_id[0]['parking_id']).values('address')
    add = address[0]['address']

    # str型をdatetime型へ変換
    start = booking['start_day'] + ' ' + booking['start_time']
    start = datetime.datetime.strptime(start, '%Y-%m-%d %H:%M')
    end = booking['end_day'] + ' ' + booking['end_time']
    end = datetime.datetime.strptime(end, '%Y-%m-%d %H:%M')

    # 日にち　分数計算
    time = end - start
    d = int(time.days)
    m = int(time.seconds / 60)
    times = ''

    # 利用合計日時計算
    if d <= 0:
        print('1day')
    else:
        times = str(d) + '日 '

    if booking['start_time'] < booking['end_time']:
        h = int(m / 60)
        m = int(m % 60)
        x = str(h) + '時間 ' + str(m) + '分'
        times += x
    else:
        h = int(m / 60)
        m = int(m % 60)
        x = str(h) + '時間 ' + str(m) + '分'
        times += x

    params = {
        'title': '予約完了',
        'message': '予約情報',
        'address': add,
        'car_obj': car_obj,
        'data': data,
        'times': times,
        'kingaku': '',
    }
    params['kingaku'] = "{:,}".format(booking['charge'])
    return render(request, "carsharing_booking/check.html", params)


#予約確認・一覧・詳細
class ReservationList(TemplateView):
    def __init__(self):
        self.params = {
            'title': '予約一覧',
            'data': '',
            'data2': '',
        }

    def post(self, request):
        self.params['title'] = "予約詳細"
        if request.POST['flag'] == 'car':
            car_obj = CarInfoModel.objects.get(id=request.POST['car'])
            self.params['flag'] = "car"
            self.params['data'] = car_obj
            parking_obj = ParkingUserModel.objects.get(id=request.POST['parking'])
            self.params['data2'] = parking_obj
            booking = BookingModel.objects.get(user_id=request.session['user_id'], id=request.POST['booking'])
        else:
            parking_obj = ParkingUserModel.objects.get(id=request.POST['parking'])
            self.params['flag'] = "parking"
            self.params['data2'] = parking_obj
            booking = ParkingBookingModel.objects.get(user_id=request.session['user_id'], id=request.POST['booking'])
        booking.start_day = dateStr(booking.start_day)
        booking.start_time = timeStr(booking.start_time)
        booking.end_day = dateStr(booking.end_day)
        booking.end_time = timeStr(booking.end_time)
        booking.charge = "{:,}".format(booking.charge)
        self.params['booking'] = booking
        return render(request, 'carsharing_booking/list_next.html', self.params)

    def get(self, request):
        if str(request.user) == "AnonymousUser":
            return redirect(to='carsharing_req:index')
        dt_now = datetime.datetime.now()
        d_now = dt_now.strftime('%Y-%m-%d')
        # print(d_now)
        usage = []
        usage_list = list(UsageModel.objects.values('id'))
        for item in usage_list:
            usage.append(item['id'])
        usage2 = []
        usage_list2 = list(ParkingUsageModel.objects.values('id'))
        for item in usage_list2:
            usage2.append(item['id'])
        booking = BookingModel.objects.filter(user_id=request.session['user_id']).exclude(charge=-1).exclude(id__in=usage).order_by('end_day', 'end_time').values('id', 'user_id', 'car_id', 'start_day', 'start_time', 'end_day', 'end_time', 'charge')
        booking2 = ParkingBookingModel.objects.filter(user_id=request.session['user_id']).exclude(charge=-1).exclude(id__in=usage2).order_by('end_day', 'end_time').values('id', 'user_id', 'parking_id', 'start_day', 'start_time', 'end_day', 'end_time', 'charge')
        for item in list(booking):
            print(item['car_id'])
            num = CarInfoModel.objects.filter(id=item['car_id']).values("category")
            category = Category.objects.filter(id=num[0]['category']).values("category")
            item['category'] = category[0]['category']
            parking_id = CarInfoParkingModel.objects.filter(car_id=item['car_id']).values("parking_id")
            address = ParkingUserModel.objects.filter(id=parking_id[0]['parking_id']).values("address")
            item['parking_id'] = parking_id[0]['parking_id']
            item['address'] = address[0]['address']
            if item['start_day'] == item['end_day']:
                flag = True
            else:
                flag = False
            item['start_day'] = dateStr(item['start_day'])
            item['start_time'] = timeStr(item['start_time'])
            item['end_day'] = dateStr(item['end_day'])
            item['end_time'] = timeStr(item['end_time'])
            if flag == True:
                item['end_day'] = ''
            item['charge'] = "{:,}".format(item['charge'])
            car_obj = CarInfoModel.objects.get(id=item['car_id'])
            item['img'] = car_obj.img
            print(item)
        for item in list(booking2):
            address = ParkingUserModel.objects.filter(id=item['parking_id']).values("address")
            if item['start_day'] == item['end_day']:
                flag = True
            else:
                flag = False
            item['address'] = address[0]['address']
            item['start_day'] = dateStr(item['start_day'])
            item['start_time'] = timeStr(item['start_time'])
            item['end_day'] = dateStr(item['end_day'])
            item['end_time'] = timeStr(item['end_time'])
            if flag == True:
                item['end_day'] = ''
            item['charge'] = "{:,}".format(item['charge'])
            print(item)
        self.params['data'] = booking
        self.params['data2'] = booking2
        return render(request, 'carsharing_booking/list.html', self.params)


class DeleteBooking(TemplateView):
    def __init__(self):
        self.params = {
            'title': '予約キャンセル',
        }

    def post(self, request):
        if request.POST['flag'] == 'car':
            booking = BookingModel.objects.get(id=request.POST['id'])
            booking.delete()
            messages.error(request, '予約をキャンセルしました。')
        else:
            booking = ParkingBookingModel.objects.get(id=request.POST['id'])
            booking.delete()
            messages.error(request, '予約をキャンセルしました。')
        return redirect(to='carsharing_req:first')

    def get(self, request, flag='error', num=0):
        if flag == 'car':
            self.params['flag'] = 'car'
            booking = BookingModel.objects.get(id=num)
            if booking.user_id == request.session['user_id']:
                booking.start_day = dateStr(booking.start_day)
                booking.start_time = timeStr(booking.start_time)
                booking.end_day = dateStr(booking.end_day)
                booking.end_time = timeStr(booking.end_time)
                booking.charge = "{:,}".format(booking.charge)
                self.params['booking'] = booking
                car_id = booking.car_id
                parking_id = CarInfoParkingModel.objects.get(car_id=car_id).parking_id_id
                self.params['car_obj'] = CarInfoModel.objects.get(id=car_id)
                self.params['parking_obj'] = ParkingUserModel.objects.get(id=parking_id)
                messages.warning(request, 'まだ予約のキャンセル処理を完了しておりません。<br>本当にキャンセルして宜しければ、キャンセル確定ボタンをクリックして下さい。')
                return render(request, 'carsharing_booking/delete.html', self.params)
            else:
                messages.error(request, '不正なリクエストです')
                return redirect(to='carsharing_req:index')
        elif flag == 'parking':
            booking = ParkingBookingModel.objects.get(id=num)
            if booking.user_id == request.session['user_id']:
                # booking.delete()
                booking.start_day = dateStr(booking.start_day)
                booking.start_time = timeStr(booking.start_time)
                booking.end_day = dateStr(booking.end_day)
                booking.end_time = timeStr(booking.end_time)
                booking.charge = "{:,}".format(booking.charge)
                self.params['booking'] = booking
                parking_id = booking.parking_id
                self.params['parking_obj'] = ParkingUserModel.objects.get(id=parking_id)
                messages.warning(request, 'まだ予約のキャンセル処理を完了しておりません。<br>本当にキャンセルして宜しければ、キャンセル確定ボタンをクリックして下さい。')
                return render(request, 'carsharing_booking/delete.html', self.params)
            else:
                messages.error(request, '不正なリクエストです')
                return redirect(to='carsharing_req:index')
        else:
            messages.error(request, '不正なリクエストです')
            return redirect(to='carsharing_req:index')
        

# 日付を日本語(str型)に変換するメソッド
def dateStr(day):
    day_date = datetime.datetime.strptime(day, "%Y-%m-%d")
    day_week = day_date.weekday()
    print(type(day_date))
    if day_week == 0:
        day_week = '(月)'
    elif day_week == 1:
        day_week = '(火)'
    elif day_week == 2:
        day_week = '(水)'
    elif day_week == 3:
        day_week = '(木)'
    elif day_week == 4:
        day_week = '(金)'
    elif day_week == 5:
        day_week = '(土)'
    else:
        day_week = '(日)'
    y_date = day_date.year
    m_date = day_date.month
    d_date = day_date.day
    day = str(y_date) + "年" + str(m_date) + "月" + str(d_date) + "日"
    print(day)
    print(day_week)
    return day + day_week

# 時間を日本語(str型)に変換するメソッド
def timeStr(time):
    time = time.replace(':', '時')
    time += '分'
    h = (int(time[0:2]))
    m = (time[2:])
    time = str(h) + m
    return time