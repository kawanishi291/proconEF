from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django .shortcuts import redirect
from carsharing_req .models import CarsharUserModel
from owners_req .models import CarInfoParkingModel
from parking_req .models import *
import json, datetime
from .models import ParkingBookingModel
from .forms import ParkingBookingForm
from django.contrib import messages
from django.db.models import Q

# Create your views here.

def index(request):
    return HttpResponse('parking_booking')

def test(request):
    input_parking_id = request.POST.getlist("name_parking_id")
    request.session['user_parking_id'] = input_parking_id[0]
    return redirect(to='/parking_booking/create')

# def test_ajax_app(request):
#     if str(request.user) == "AnonymousUser":
#         print('ゲスト')
#     else:
#         print(request.user)
#     hoge = "Hello Django!!"

#     return render(request, "carsharing_booking/index.html", {
#         "hoge": hoge,
#     })

# def test_ajax_response(request):
#     input_text = request.POST.getlist("name_input_text")
#     hoge = "Ajax Response: " + input_text[0]

#     return HttpResponse(hoge)

def map(request):
    if request.user.id == None:
        add = '千葉県柏市末広町10-1'
    else:
        data = CarsharUserModel.objects.get(id=request.session['user_id'])
        print(data.pref01+data.addr01+data.addr02)
        add = data.pref01+data.addr01+data.addr02
    set_list = CarInfoParkingModel.objects.values("parking_id")
    item_all = ParkingUserModel.objects.exclude(id__in=set_list)
    item = item_all.values("id", "user_id", "lat", "lng", "address")
    item_list = list(item.all())
    print(item)
    data = {
        'markerData': item_list,
    }
    params = {
        'name': '自宅',
        'add': add,
        'data_json': json.dumps(data)
    }
    if (request.method == 'POST'):
        params['add'] = request.POST['add']
        params['name'] = '検索'
    return render(request, "parking_booking/map.html", params)

#駐車場予約
class ParkingBookingCreate(TemplateView):
    def __init__(self):
        self.params = {
            'title': '駐車場予約',
            'message': '予約情報入力',
            'form': ParkingBookingForm(),
        }
    
    #ログインユーザ、非ログインユーザ判別
    def get(self, request):
        if str(request.user) == "AnonymousUser":
            print('ゲスト')
            messages.error(self.request, 'ログインしてください。')
            return redirect(to='/carsharing_req/index')
        else:
            print(request.user)
            #print(request.session['user_lat'])
            #print(request.session['user_lng'])

        return render(request, 'parking_booking/booking.html', self.params)

    #入力データ保存
    def post(self, request):
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

        booking_list = ParkingBookingModel.objects.filter(parking_id=request.session['user_parking_id'])
        booking_list = booking_list.filter(Q(start_day=start_day) | Q(start_day=end_day) | Q(end_day=start_day) | Q(end_day=end_day))
        print(booking_list)
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
                messages.error(request, '申し訳ございません。その時間帯は既に予約済みです。別の駐車場にするか時間帯を変更してください。<br>' + datetime.datetime.strftime(booking_start, "%Y年%m月%d日 %H:%M") + ' 〜 ' + datetime.datetime.strftime(booking_end, "%Y年%m月%d日 %H:%M"))
                return render(request, 'parking_booking/booking.html', self.params)
            else:
                print("大丈夫！")

        print(booking_list)


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
            charge = int(d * 660)
            times = str(d) + '日 '

        if start_time < end_time:
            print('tule')
            charge += int(m / 60 * 220)
            h = int(m / 60)
            m = int(m % 60)
            x = str(h) + '時間 ' + str(m) + '分'
            times += x
        elif start_time >= end_time and d < 0:
            print('false')
            obj = ParkingBookingModel()
            p_b = ParkingBookingForm(request.POST, instance=obj)
            self.params['form'] = p_b
            messages.error(request, '終了時刻が開始時刻よりも前です。')
            return render(request, 'parking_booking/booking.html', self.params)
        elif d <= 0 and m < 15:
            messages.error(request, '15分以下は利用できません。')
            return render(request, 'parking_booking/booking.html', self.params)
        else:
            charge += int(m / 60 * 220)
            h = int(m / 60)
            m = int(m % 60)
            x = str(h) + '時間 ' + str(m) + '分'
            times += x
        
        data = {
            'start_day': start_day,
            'start_time': start_time,
            'end_day': end_day,
            'end_time': end_time,
            'charge': charge,
        }
        self.params['kingaku'] = "{:,}".format(charge)
        self.params['data'] = data
        self.params['times'] = times
        self.params['message'] = '予約情報確認'
        messages.warning(self.request, 'まだ予約完了しておりません。<br>こちらの内容で宜しければ確定ボタンをクリックして下さい。')
        return render(request, "parking_booking/check.html", self.params)
        

def push(request):
    if (request.method == 'POST'):
        user_id = int(request.session['user_id'])
        parking_id = int(request.session['user_parking_id'])
        start_day = request.POST['start_day']
        end_day = request.POST['end_day']
        start_time = request.POST['start_time']
        end_time = request.POST['end_time']
        charge = int(request.POST['charge'])
        record = ParkingBookingModel(user_id = user_id, parking_id = parking_id, start_day = start_day, \
            end_day = end_day, start_time = start_time, end_time = end_time, charge = charge)
        record.save()
        messages.success(request, '予約が完了しました。<br>ご登録されているメールアドレスに予約完了メールを送信致しました。ご確認下さい。')
        del request.session['user_parking_id']
        #mail送信メソッドの呼び出し
        success_booking_mail(request, charge, start_day, start_time, end_day, end_time)
    else:
        messages.error(request, '不正なリクエストです')
    return redirect(to='parking_booking:map')

def success_booking_mail(request, charge, start_day, start_time, end_day, end_time):

    subject = "駐車場予約完了確認メール"
    path = request.build_absolute_uri()
    url = path[:-21] + 'carsharing_booking/list/'
    message = str(request.user) + "様\n \
        駐車場のご予約ありがとうございます。\n \
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