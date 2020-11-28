from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django .shortcuts import redirect
from carsharing_req .models import CarsharUserModel
from .models import ParkingUserModel
from .forms import ParkingForm
import datetime
import json
from django.contrib import messages

# Create your views here.


def index(request):
    params = {
        'msg': '',
    }
    # return render(request, 'parking_req/map1.html', params)
    return render(request, 'parking_req/mapping.html', params)

#登録する緯度、経度をセッションにセット
def test_ajax_response(request):
    input_lat = request.POST.getlist("name_input_lat")
    input_lng = request.POST.getlist("name_input_lng")
    hoge = "lat: "  + input_lat[0] + "lng: " + input_lng[0] + "がセットされました"
    request.session['user_lat'] = input_lat[0]
    request.session['user_lng'] = input_lng[0]

    return HttpResponse(hoge)

#駐車場データ登録機能
class ParkingHostCreate(TemplateView):
    def __init__(self):
        self.params = {
            'title': 'ParkingHostCreate',
            'message': '駐車場情報入力',
            'form': ParkingForm(),
        }
    
    #ログインユーザ、非ログインユーザ判別
    def get(self, request):
        if str(request.user) == "AnonymousUser":
            print('ゲスト')
            messages.error(self.request, 'ログインしてください。')
            return redirect(to='/carsharing_req/index')
        else:
            print(request.user)
            print(request.session['user_lat'])
            print(request.session['user_lng'])

        return render(request, 'parking_req/create.html', self.params)

    #入力データとセッションデータを保存
    def post(self, request):
        dt_now = datetime.datetime.now()
        user_id = request.session['user_id']
        lat = request.session['user_lat']
        lng = request.session['user_lng']
        day = dt_now
        parking_type = request.POST['parking_type']
        width = request.POST['width']
        length = request.POST['length']
        height = request.POST['height']
        record = ParkingUserModel(user_id = user_id, lat = lat, lng=lng, day = day, \
            parking_type = parking_type, width = width, length = length, height = height)
        obj = ParkingUserModel()
        parking = ParkingForm(request.POST, instance=obj)
        self.params['form'] = parking
        #バリデーションチェック
        if (parking.is_valid()):
            record.save()
            #セッションデータ削除
            del request.session['user_lat']
            del request.session['user_lng']
            if 'info_flag' in request.session:
                print(request.session['info_flag'])
                return redirect(to='/owners_req/settinginfo')
            else:
                print('none')
                messages.success(self.request, '駐車場登録が完了しました。')
                return redirect(to='/parking_req/sample')
        return render(request, 'parking_req/create.html', self.params)

def edit(request):
    if (request.method == 'POST'):
        num = request.POST['p_id']
        obj = ParkingUserModel.objects.get(id=num)
        parking = ParkingForm(request.POST, instance=obj)
        params = {
            'title':'ParkingEdit',
            'message': '駐車場情報修正', 
            'form': ParkingForm(),
            'id':num,
        }
        if (parking.is_valid()):
            parking.save()
            messages.success(request, '駐車場情報を修正しました。')
            return redirect(to='/parking_req/sample')
        else:
            params['form'] = ParkingForm(request.POST, instance= obj)        
        
    return render(request, 'parking_req/edit.html', params)

def delete(request, num):
    parking = ParkingUserModel.objects.get(id=num)
    if (request.method == 'POST'):
        parking.delete()
        messages.success(request, '駐車場情報を削除しました。')
        return redirect(to='/parking_req/sample')

    return render(request, 'parking_req/delete.html')

def sample(request):
    s_p = ParkingUserModel.objects.filter(user_id=request.session['user_id'])
    sample_parking = s_p.values("id", "user_id", "lat", "lng")
    if (request.method == 'POST'):
        num1 = request.POST['command']
        #修正機能
        if (num1 == 'edit'):
            num = request.POST['obj.id']
            obj = ParkingUserModel.objects.get(id=num)
            params = {
            'title': 'ParkingEdit',
            'message': '駐車場情報修正',
            'id':num,
            'form': ParkingForm(instance=obj), 
            }
            return render(request, 'parking_req/edit.html', params)
        #削除機能    
        if (num1 == 'delete'):
            num = request.POST['obj.id']
            delete_parking = ParkingUserModel.objects.get(id=num)
            params = {
            'title': 'ParkingDelete',
            'message': '駐車場情報削除',
            'obj': delete_parking,
            'id': num,
            }
            return render(request, 'parking_req/delete.html', params)
        #検索機能
        if (num1 == 'map'):
            data = CarsharUserModel.objects.get(id=request.session['user_id'])
            print(data.pref01+data.addr01+data.addr02)
            add = data.pref01+data.addr01+data.addr02
            markerData = list(sample_parking.all())
            #item_all = ParkingUserModel.objects.all()
            #item = item_all.values("id", "user_id", "lat", "lng")
            #item_list = list(item.all())
            #print(item)
            data = {
                'markerData': markerData,
            }
            params = {
            'name': '自宅',
            'add': add,
            'data_json': json.dumps(data)
            }
            if (request.method == 'POST'):
                params['add'] = request.POST['add']
            return render(request, "parking_req/map3.html", params)        
    else:
        #地図上に登録した駐車場を表示
        data = CarsharUserModel.objects.get(id=request.session['user_id'])
        print(data.pref01+data.addr01+data.addr02)
        add = data.pref01+data.addr01+data.addr02
        markerData = list(sample_parking.all())
        data = {
            'markerData': markerData,
        }
        params = {
            'title': 'ParkingSample',
            'message': '駐車場登録データ',
            'data': sample_parking,
            'name': '自宅',
            'add': add,
            'data_json': json.dumps(data)
        }
        # return render(request, 'parking_req/sample.html', params)
        return render(request, 'parking_req/map3.html', params)