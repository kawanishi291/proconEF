from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from .models import CarsharUserModel, UsageModel
from .forms import CarsharUserCreateForm, CarsharUserNameForm
from accounts .models import CustomUser
from parking_req .models import *
from owners_req .models import *
from carsharing_booking .models import BookingModel
from parking_booking .models import ParkingBookingModel
import json, ast, datetime, calendar, hashlib
from django.core.mail import EmailMessage
from .models import Photo
from .forms import PhotoForm

# Create your views here.

# ゲスト/ユーザ 判定
def index(request):
    querySet = CarsharUserModel.objects.filter(email__contains = request.user.email)
    if querySet.first() is None:
        print('no data')
        return redirect(to='carsharing_req:create')
    if str(request.user) == "AnonymousUser":
        print('ゲスト')
    else:
        print(request.user.email)
    return redirect(to='carsharing_req:set_session')

# user_idをSESSIONに格納・オーナー登録済か判定用flagをSESSIONに格納
def set_session(request):
    data = CarsharUserModel.objects.get(email=request.user.email)
    user = CarsharUserModel.objects.get(id=data.id)
    request.session['user_id'] = data.id
    request.session['system_flag'] = user.system_flag
    check_usage_obj = checkUsage(request.session['user_id'])
    check_p_usage_obj = checkParkingUsage(request.session['user_id'])
    if check_p_usage_obj != None:
        ParkingEndMail(request, check_p_usage_obj)
        saveParkingUsage(check_p_usage_obj)
    if check_usage_obj == None:
        return redirect(to='carsharing_req:index')
    else:
        surveyMail(request, check_usage_obj)
        messages.warning(request, '返却確認処理をおこなってください。')
        return redirect(to='survey:questionnaire')


# 説明ページ(HTML)ルーティング
def pages(request, num, page):
    params = {
        'head_title': '',
        'title': '',
        'json_data': '',
        'next': '',
        'prev': ''
    }
    if num == 1:
        path = "./data/page/user_car.json"
        params['head_title'] = 'カーシェアリング利用の流れ'
        with open(path, 'r') as f:
            json_data = f.read()
        json_data = ast.literal_eval(json_data)
        # print(json_data)
        if page == 0:
            return render(request, 'page/user_car.html')
        elif page == 1:
            params['title'] = '会員登録詳細'
            params['json_data'] = json_data['会員登録詳細']
            params['next'] = [2,'検索・予約詳細']
            return render(request, 'page/user_details.html', params)
        elif page == 2:
            params['title'] = '検索・予約詳細'
            params['json_data'] = json_data['検索・予約詳細']
            params['prev'] = [1,'会員登録詳細']
            params['next'] = [3,'解錠詳細']
            return render(request, 'page/user_details.html', params)
        elif page == 3:
            params['title'] = '解錠詳細'
            params['json_data'] = json_data['解錠詳細']
            params['prev'] = [2,'検索・予約詳細']
            params['next'] = [4,'乗車詳細']
            return render(request, 'page/user_details.html', params)
        elif page == 4:
            params['title'] = '乗車詳細'
            params['json_data'] = json_data['乗車詳細']
            params['prev'] = [3,'解錠詳細']
            params['next'] = [5,'給油・洗車']
            return render(request, 'page/user_details.html', params)
        elif page == 5:
            params['title'] = '給油・洗車'
            params['json_data'] = json_data['給油・洗車']
            params['prev'] = [4,'乗車詳細']
            params['next'] = [6,'返却詳細']
            return render(request, 'page/user_details.html', params)
        elif page == 6:
            params['title'] = '返却詳細'
            params['json_data'] = json_data['返却詳細']
            params['prev'] = [5,'給油・洗車']
            params['next'] = [7,'精算詳細']
            return render(request, 'page/user_details.html', params)
        elif page == 7:
            params['title'] = '精算詳細'
            params['json_data'] = json_data['精算詳細']
            params['prev'] = [6,'返却詳細']
            return render(request, 'page/user_details.html', params)
    elif num == 2:
        path = "./data/page/user_parking.json"
        params['head_title'] = '駐車場利用の流れ'
        with open(path, 'r') as f:
            json_data = f.read()
        json_data = ast.literal_eval(json_data)
        if page == 0:
            return render(request, 'page/user_parking.html')
        elif page == 1:
            params['title'] = '会員登録詳細'
            params['json_data'] = json_data['会員登録詳細']
            params['next'] = [2,'検索・予約詳細']
            return render(request, 'page/user_details.html', params)
        elif page == 2:
            params['title'] = '検索・予約詳細'
            params['json_data'] = json_data['検索・予約詳細']
            params['prev'] = [1,'会員登録詳細']
            params['next'] = [3,'駐車詳細']
            return render(request, 'page/user_details.html', params)
        elif page == 3:
            params['title'] = '駐車詳細'
            params['json_data'] = json_data['駐車詳細']
            params['prev'] = [2,'検索・予約詳細']
            params['next'] = [4,'精算詳細']
            return render(request, 'page/user_details.html', params)
        elif page == 4:
            params['title'] = '精算詳細'
            params['json_data'] = json_data['精算詳細']
            params['prev'] = [3,'駐車詳細']
            return render(request, 'page/user_details.html', params)
    elif num == 3:
        return render(request, 'page/owner_car.html')
    elif num == 4:
        return render(request, 'page/owner_parking.html')
    elif num == 5:
        if page == 0:
            return render(request, 'page/car_price_list.html')
        else:
            return render(request, 'page/parking_price_list.html')
    else:
        return redirect(to='carsharing_req:index')


class CarsharUserInfo(TemplateView):
    def __init__(self):
        self.params = {
            'title': 'Hello World!',
            'message': 'Not found your data.<br>Please send your profile.',
            'form': CarsharUserCreateForm(),
            'link': 'other',
            'gender': '男性',
            'age': '50代',
            'address': '柏市',
        }
    
    def get(self, request):
        if str(request.user) == "AnonymousUser":
            print('ゲスト')
            path = "http://127.0.0.1:8000/parking_booking/push/"
            print(path[:-21])
        else:
            print(request.user)
            user_data = CarsharUserModel.objects.get(id=request.session['user_id'])
            myinfo_list = SetMyInfo(user_data)
            print(myinfo_list)
            self.params['gender'] = myinfo_list[0]
            self.params['age'] = myinfo_list[1]
            self.params['address'] = myinfo_list[2]
            if user_data.charge_flag == False:
                InitializeCharge(user_data)
        return render(request, 'carsharing_req/top.html', self.params)

def SetMyInfo(user_data):
    myinfo_list = []
    if user_data.gender == True:
        myinfo_list.append('男性')
    else:
        myinfo_list.append('女性')
    myinfo_list.append(str(user_data.age)[-2] + '0代')
    address = user_data.addr01
    count = address.count('市')
    if count == 1:
        i = address.find('市')
        myinfo_list.append(address[:i]+'市')
    elif count > 1:
        i = address.rfind('市')
        myinfo_list.append(address[:i]+'市')
    return myinfo_list

def InitializeCharge(user_data):
    if user_data.plan == 'a':
        user_data.charge = 500
    elif user_data.plan == 'b':
        user_data.charge = 1000
    elif user_data.plan == 'c':
        user_data.charge = 2000
    else:
        user_data.charge = 0
    print('チャージ完了')
    user_data.charge_flag = True
    user_data.save()

def carsharuserdata(request):
    data = CarsharUserModel.objects.get(id=request.session['user_id'])
    data2 = CustomUser.objects.get(email=request.user.email)
    params = {
        'title': '個人登録情報確認',
        'message': 'ユーザ情報',
        'data': data,
        'data2': data2,
    }
    return render(request, 'carsharing_req/userdata.html', params)


# class CarsharUserSendMail(generic.FormView):

#     template_name = "carsharing_req/index.html"
#     form_class = CarsharUserCreateForm
#     success_url = reverse_lazy('carsharing_req:index')


#     def form_valid(self, form):
#         form.send_email()
#         messages.success(self.request, 'メッセージを送信しました。')
#         return super().form_valid(form)



class CreateView(TemplateView):
    def __init__(self):
        self.params = {
        'title': '会員登録',
        'form': CarsharUserCreateForm(),
        'form_name': CarsharUserNameForm()
    }

    def post(self, request):
        # form = CarsharUserCreateForm(request.POST, request.FILES)
        # form_name = CarsharUserNameForm(request.POST, request.FILES)
        form = CarsharUserCreateForm(request.POST)
        form_name = CarsharUserNameForm(request.POST)

        if form.is_valid() and form_name.is_valid():
            first_name = request.POST['first_name']
            last_name = request.POST['last_name']
            first_ja = request.POST['first_ja']
            last_ja = request.POST['last_ja']
            # gender = 'gender' in request.POST
            if request.POST['gender'] == 'True':
                gender = True
            else:
                gender = False
            birthday = birthdayCheck(request.POST['birthday_year'], request.POST['birthday_month'], request.POST['birthday_day'])
            # birthday = birthdaySet(birthday_str)
            age = calcAge(birthday)

            # 二十歳未満の利用を制限
            if age < 20:
                self.params['form'] = form
                self.params['form_name'] = form_name
                messages.error(self.request, '20歳未満の方はご利用いただけません。')
                return render(request, 'carsharing_req/create.html', self.params)
            if age > 80:
                self.params['form'] = form
                self.params['form_name'] = form_name
                messages.error(self.request, '80歳以上の方はご利用いただけません。')
                return render(request, 'carsharing_req/create.html', self.params)

            zip01 = request.POST['zip01']
            pref01 = request.POST['pref01']
            addr01 = request.POST['addr01']
            addr02 = request.POST['addr02']
            tel = request.POST['tel']
            credit_card_company = request.POST['credit_card_company']
            first_en = request.POST['first_en']
            last_en = request.POST['last_en']
            credit_card_num = request.POST['credit_card_num']
            credit_card_num_check = request.POST['credit_card_num'][13:]
            valid_thru = request.POST['valid_thru']

            # クレジットカードの有効期限チェック
            dt_now = datetime.datetime.now()
            if 0 >= int(valid_thru[:2]) or int(valid_thru[:2]) > 12:
                self.params['form'] = form
                self.params['form_name'] = form_name
                messages.error(self.request, 'クレジットカードの期限が不正です。')
                return render(request, 'carsharing_req/create.html', self.params)
            dt_now_y = str(dt_now.year)[:2]
            if int(dt_now_y) > int(valid_thru[3:]):
                self.params['form'] = form
                self.params['form_name'] = form_name
                messages.error(self.request, 'クレジットカードの有効期限が切れています。')
                return render(request, 'carsharing_req/create.html', self.params)
            elif int(dt_now_y) == int(valid_thru[3:]) and int(valid_thru[:2]) < dt_now.month:
                self.params['form'] = form
                self.params['form_name'] = form_name
                messages.error(self.request, 'クレジットカードの有効期限が切れています。')
                return render(request, 'carsharing_req/create.html', self.params)

            security_code = request.POST['security_code']
            plan = request.POST['plan']
            if plan == 'a':
                charge = 500
            elif plan == 'b':
                charge = 1000
            elif plan == 'c':
                charge = 2000
            else:
                charge = 0

            self.params['first_name'] = first_name
            self.params['last_name'] = last_name
            self.params['first_ja'] = first_ja
            self.params['last_ja'] = last_ja
            self.params['gender'] = gender
            self.params['birthday'] = birthday
            self.params['age'] = age
            self.params['zip01'] = zip01
            self.params['pref01'] = pref01
            self.params['addr01'] = addr01
            self.params['addr02'] = addr02
            self.params['tel'] = tel
            self.params['credit_card_company'] = credit_card_company
            self.params['first_en'] = first_en
            self.params['last_en'] = last_en
            self.params['credit_card_num'] = credit_card_num
            self.params['credit_card_num_check'] = credit_card_num_check
            self.params['valid_thru'] = valid_thru
            self.params['security_code'] = security_code
            self.params['plan'] = plan
            self.params['charge'] = charge
            self.params['birthday_year'] = request.POST['birthday_year']
            self.params['birthday_month'] = request.POST['birthday_month']
            self.params['birthday_day'] = request.POST['birthday_day']
            self.params['imageform'] = PhotoForm()
            messages.warning(request, 'まだ登録は完了しておりません。<br>内容を確認後確定ボタンを押してください。')
            return render(request, 'carsharing_req/check.html', self.params)
        else:
            self.params['form'] = form
            self.params['form_name'] = form_name
            return render(request, 'carsharing_req/create.html', self.params)
        return redirect(to='carsharing_req:first')
        
    def get(self, request):
        dt_now = datetime.datetime.now()
        min_year, max_year = LimitationAge(dt_now)
        self.params['min_year'] = min_year
        self.params['max_year'] = max_year
        querySet = CarsharUserModel.objects.filter(email__contains = request.user.email)
        if querySet.first() is None:
            print('no data')
            messages.info(self.request, '会員登録して下さい。')
        else:
            print('data　exist')
            return redirect(to='carsharing_req:index')
        return render(request, 'carsharing_req/create.html', self.params)

def push(request):
    params = {
        'title': '会員登録',
    }
    if (request.method == 'POST'): 
        email = request.user.email
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        first_ja = request.POST['first_ja']
        last_ja = request.POST['last_ja']
        if request.POST['gender'] == 'True':
            gender = True
        else:
            gender = False
        age = request.POST['age']
        birthday = request.POST['birthday']
        birthday = birthdaySet(birthday)
        zip01 = request.POST['zip01']
        pref01 = request.POST['pref01']
        addr01 = request.POST['addr01']
        addr02 = request.POST['addr02']
        tel = request.POST['tel']
        credit_card_company = request.POST['credit_card_company']
        first_en = request.POST['first_en']
        last_en = request.POST['last_en']
        SECRET_KEY = request.POST['credit_card_num']
        credit_card_num = hashlib.sha256(SECRET_KEY.encode()).hexdigest()
        credit_card_num_check = request.POST['credit_card_num_check']
        valid_thru = request.POST['valid_thru']
        SECRET_KEY = request.POST['security_code']
        security_code = hashlib.sha256(SECRET_KEY.encode()).hexdigest()
        plan = request.POST['plan']
        charge = request.POST['charge']

        imageform = PhotoForm(request.POST, request.FILES)
        print(imageform)

        # heroku使用
        # img = request.FILES['image']
        # params['first_name'] = first_name
        # params['last_name'] = last_name
        # params['first_ja'] = first_ja
        # params['last_ja'] = last_ja
        # params['gender'] = gender
        # params['birthday'] = request.POST['birthday']
        # params['age'] = age
        # params['zip01'] = zip01
        # params['pref01'] = pref01
        # params['addr01'] = addr01
        # params['addr02'] = addr02
        # params['tel'] = tel
        # params['credit_card_company'] = credit_card_company
        # params['first_en'] = first_en
        # params['last_en'] = last_en
        # params['credit_card_num'] = request.POST['credit_card_num']
        # params['credit_card_num_check'] = credit_card_num_check
        # params['valid_thru'] = valid_thru
        # params['security_code'] = request.POST['security_code']
        # params['plan'] = plan
        # params['charge'] = charge
        # params['birthday_year'] = request.POST['birthday_year']
        # params['birthday_month'] = request.POST['birthday_month']
        # params['birthday_day'] = request.POST['birthday_day']
        # params['imageform'] = PhotoForm()
        
        # 現ver
        image = request.FILES['image']
        print(image)
        photo = Photo(image=image)
        predicted, percentage = photo.predict()
        print(predicted)
        print(str(percentage) + '%')
        if predicted == '免許証写真' and int(percentage) >= 80:
            img = request.FILES['image']
        else:
            params['first_name'] = first_name
            params['last_name'] = last_name
            params['first_ja'] = first_ja
            params['last_ja'] = last_ja
            params['gender'] = gender
            params['birthday'] = request.POST['birthday']
            params['age'] = age
            params['zip01'] = zip01
            params['pref01'] = pref01
            params['addr01'] = addr01
            params['addr02'] = addr02
            params['tel'] = tel
            params['credit_card_company'] = credit_card_company
            params['first_en'] = first_en
            params['last_en'] = last_en
            params['credit_card_num'] = request.POST['credit_card_num']
            params['credit_card_num_check'] = credit_card_num_check
            params['valid_thru'] = valid_thru
            params['security_code'] = request.POST['security_code']
            params['plan'] = plan
            params['charge'] = charge
            params['birthday_year'] = request.POST['birthday_year']
            params['birthday_month'] = request.POST['birthday_month']
            params['birthday_day'] = request.POST['birthday_day']
            params['imageform'] = PhotoForm()
            messages.error(request, '免許証と判定されませんでした。<br>横向きの写真をアップロードしてください。')
            return render(request, 'carsharing_req/check.html', params)
        record = CarsharUserModel(email=email, first_name=first_name, last_name=last_name, first_ja=first_ja, last_ja=last_ja, \
            gender=gender, age=age, birthday=birthday, zip01=zip01, pref01=pref01, addr01=addr01, addr02=addr02, tel=tel, \
            credit_card_company=credit_card_company, first_en=first_en, last_en=last_en, \
            credit_card_num=credit_card_num, credit_card_num_check=credit_card_num_check, valid_thru=valid_thru, \
            security_code=security_code, plan=plan, charge=charge, charge_flag=True, img=img)
        record.save()
        messages.success(request, '免許証と判定されました。')
        messages.success(request, '会員登録が完了しました。')
    else:
        messages.error(request, '不正なリクエストです。')
    return redirect(to='/carsharing_req/')


# -------------------------------------------------------------------------------------------------------
# 年齢制限
def LimitationAge(dt_now):
    min_year = dt_now.year - 20
    max_year = dt_now.year - 80
    return min_year, max_year

# 生年月日
def birthdayCheck(y, m, d):
    if len(m) == 1:
        m = '0' + m
    if len(d) == 1:
        d = '0' + d
    birthday = y + m + d
    return birthday

# 生年月日設定(型変換)
def birthdaySet(ymd):
    y = ymd[0:4]
    m = ymd[4:6]
    d = ymd[6:8]
    tstr = y + '-' + m + '-' + d
    tdatetime = datetime.datetime.strptime(tstr, '%Y-%m-%d')
    return tdatetime

# 年齢計算関数
def calcAge(birthdayStr):
  if not (birthdayStr.isdigit() and len(birthdayStr)==8):
    return -1
  dStr = datetime.datetime.now().strftime("%Y%m%d")
  return (int(dStr)-int(birthdayStr))//10000
# -------------------------------------------------------------------------------------------------------



class CalendarView(TemplateView):
    def __init__(self):
        self.params = {
        'title': 'FullCalendar',
        'events': ''
    }

    def get(self, request):
        # カーシェアリング予約
        events = []
        booking = BookingModel.objects.filter(user_id=request.session['user_id']).exclude(charge=-1).order_by('end_day', 'end_time')
        booking = booking.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in booking:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', 'カーシェアリング予約'+str(title)], ['start', start], ['end', end], ['color', '#9BF9CC']))
            events.append(event)
        
        # 駐車場予約
        booking2 = ParkingBookingModel.objects.filter(user_id=request.session['user_id']).exclude(charge=-1).order_by('end_day', 'end_time')
        booking2 = booking2.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in booking2:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', '駐車場予約'+str(title)], ['start', start], ['end', end], ['color', '#A7F1FF']))
            events.append(event)
        
        # 車両貸し出し制限
        loaning1 = BookingModel.objects.filter(user_id=request.session['user_id'], charge=-1).order_by('end_day', 'end_time')
        loaning1 = loaning1.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in loaning1:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', '車両貸し出し'+str(title)], ['start', start], ['end', end], ['color', '#00CC33']))
            events.append(event)


        # 駐車場貸し出し制限
        loaning2 = ParkingBookingModel.objects.filter(user_id=request.session['user_id'], charge=-1).order_by('end_day', 'end_time')
        loaning2 = loaning2.values("id", "start_day", "start_time", "end_day", "end_time")
        for obj in loaning2:
            title = obj.get("id")
            start = obj.get("start_day") + 'T' + obj.get("start_time")
            end = obj.get("end_day") + 'T' + obj.get("end_time")
            event = dict((['title', '駐車場貸し出し'+str(title)], ['start', start], ['end', end], ['color', '#6495ED']))
            events.append(event)
        self.params['events'] = json.dumps(events)
        
        return render(request, 'carsharing_req/calendar.html', self.params)

#利用確認・一覧・詳細
class DetailsList(TemplateView):
    def __init__(self):
        self.params = {
            'title': '利用履歴一覧',
            'data': '',
            'data2': '',
        }

    def post(self, request, year=0, month=0):
        self.params['title'] = "利用履歴詳細"
        booking = UsageModel.objects.get(user_id=request.session['user_id'], id=request.POST['booking'])
        booking.start_day = dateStr(booking.start_day)
        booking.start_time = timeStr(booking.start_time)
        booking.end_day = dateStr(booking.end_day)
        booking.end_time = timeStr(booking.end_time)
        booking.charge = "{:,}".format(booking.charge)
        self.params['booking'] = booking

        if request.POST['flag'] == 'car':
            car_obj = CarInfoModel.objects.get(id=request.POST['car'])
            self.params['flag'] = "car"
            self.params['data'] = car_obj
            parking_obj = ParkingUserModel.objects.get(id=request.POST['parking'])
            self.params['data2'] = parking_obj
        else:
            parking_obj = ParkingUserModel.objects.get(id=request.POST['parking'])
            self.params['flag'] = "parking"
            self.params['data2'] = parking_obj
            

        return render(request, 'carsharing_booking/list_next.html', self.params)

    def get(self, request, year=datetime.datetime.now().strftime('%Y'), month=datetime.datetime.now().strftime('%m')):
        last_day = calendar.monthrange(int(year), int(month))[1]
        farst_day = year + '-' + month + '-01'
        last_day = year + '-' + month + '-' + str(last_day) 
        print(farst_day)
        print(last_day)
        # dt_now = datetime.datetime.now()
        # d_now = dt_now.strftime('%Y-%m-%d')
        # print(d_now)
        prev_url, next_url = SetUrl(year, month)
        self.params['prev_url'] = prev_url
        self.params['next_url'] = next_url
        print(month[:1])
        if month[:1] == '0':
            print(month[1:2])
            month = month[1:2]
        self.params['now'] = year + '年' + month + '月'
        booking = UsageModel.objects.filter(user_id=request.session['user_id'], start_day__range=(farst_day, last_day)).exclude(charge=-1).order_by('-end_day', '-end_time').values()
        booking2 = ParkingUsageModel.objects.filter(user_id=request.session['user_id'], start_day__range=(farst_day, last_day)).exclude(charge=-1).order_by('-end_day', '-end_time').values()
        

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
            item['address'] = address[0]['address']
            item['start_day'] = dateStr(item['start_day'])
            item['start_time'] = timeStr(item['start_time'])
            item['end_day'] = dateStr(item['end_day'])
            item['end_time'] = timeStr(item['end_time'])
            if flag == True:
                item['end_day'] = ''
            item['charge'] = "{:,}".format(item['charge'])
            car_obj = CarInfoModel.objects.get(id=item['car_id'])
            item['img'] = car_obj.img
            # print(item)
        for item in list(booking2):
            address = ParkingUserModel.objects.filter(id=item['parking_id']).values("address")
            item['address'] = address[0]['address']
            # print(item)
        self.params['data'] = booking
        self.params['data2'] = booking2
        return render(request, 'carsharing_booking/list.html', self.params)

def dateStr(day):
    day_date = datetime.datetime.strptime(day, "%Y-%m-%d")
    day_week = day_date.weekday()
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
    return day + day_week

def timeStr(time):
    time = time.replace(':', '時')
    time += '分'
    h = (int(time[0:2]))
    m = (time[2:])
    time = str(h) + m
    return time

def SetUrl(year, month):
    prev_year = year
    prev_month = str(int(month) - 1)
    next_year = year
    next_month = str(int(month) + 1)
    if month == '01':
        prev_year = str(int(year) - 1)
        prev_month = '12'
    elif month == '12':
        next_year = str(int(year) + 1)
        next_month = '01'
    if len(prev_month) == 1:
        prev_month = '0' + prev_month
    if len(next_month) == 1:
        next_month = '0' + next_month
    prev_url = "/carsharing_req/details/" + prev_year + "/" + prev_month
    next_url = "/carsharing_req/details/" + next_year + "/" + next_month
    # print(prev_url)
    # print(next_url)
    return prev_url, next_url


def checkUsage(user_id):
    dt_now = datetime.datetime.now()
    d_now = dt_now.strftime('%Y-%m-%d')
    t_now = dt_now.strftime('%H:%M')
    usage = UsageModel.objects.filter(user_id=user_id).values('booking_id')
    # print(usage)
    if len(usage) == 0:
        # print('first')
        booking = BookingModel.objects.filter(user_id=user_id, end_day__lte=d_now).exclude(charge=-1).values().order_by('end_day', 'end_time').last()
    else:
        usage_list = []
        for booking_id in usage:
            usage_list.append(booking_id['booking_id'])
            booking = BookingModel.objects.filter(user_id=user_id, end_day__lte=d_now).exclude(id__in=usage_list).exclude(charge=-1).exclude(end_day=d_now, end_time__gte=t_now).values().order_by('end_day', 'end_time').last()
    # print(booking)
    return booking

def checkParkingUsage(user_id):
    dt_now = datetime.datetime.now()
    d_now = dt_now.strftime('%Y-%m-%d')
    t_now = dt_now.strftime('%H:%M')
    usage = ParkingUsageModel.objects.filter(user_id=user_id).values('booking_id')
    # print(usage)
    if len(usage) == 0:
        # print('first')
        booking = ParkingBookingModel.objects.filter(user_id=user_id, end_day__lte=d_now).exclude(charge=-1).values().order_by('end_day', 'end_time').last()
    else:
        usage_list = []
        for booking_id in usage:
            usage_list.append(booking_id['booking_id'])
            booking = ParkingBookingModel.objects.filter(user_id=user_id, end_day__lte=d_now).exclude(id__in=usage_list).exclude(charge=-1).exclude(end_day=d_now, end_time__gte=t_now).values().order_by('end_day', 'end_time').last()
    # print(booking)
    return booking


def surveyMail(request, booking):
    subject = "返却確認のお願い"
    path = request.build_absolute_uri()
    url = path[:-27] + 'survey/questionnaire'
    message = str(request.user) + "様\n \
        運転お疲れ様でした。返却のお時間です。\n \
        またのご利用をお待ちしております。\n\n \
        開始日: " + booking['start_day'] + "\n \
        開始時刻: " + booking['start_time'] + "\n \
        終了日: " + booking['end_day'] + "\n \
        終了時刻: " + booking['end_time'] + "\n \
        料金: " + str(booking['charge']) + "円\n\n \
        コチラから返却確認をして下さい。\n \
        URL: " + url + "\n"
    user = request.user  # ログインユーザーを取得する
    from_email = 's.kawanishi291@gmail.com'  # 送信者
    user.email_user(subject, message, from_email)  # メールの送信
    pass

def ParkingEndMail(request, booking):
    subject = "駐車場利用時間終了のお知らせ"
    message = str(request.user) + "様\n \
        ご利用ありがとうございました。\n \
        お気を付けて、いってらっしゃいませ。\n\n \
        開始日: " + booking['start_day'] + "\n \
        開始時刻: " + booking['start_time'] + "\n \
        終了日: " + booking['end_day'] + "\n \
        終了時刻: " + booking['end_time'] + "\n \
        料金: " + str(booking['charge']) + "円\n\n \
        またのご利用お待ちしております。"
    user = request.user  # ログインユーザーを取得する
    from_email = 's.kawanishi291@gmail.com'  # 送信者
    user.email_user(subject, message, from_email)  # メールの送信
    pass

def saveParkingUsage(booking):
    booking_id = ParkingBookingModel.objects.get(id=booking['id'])
    record = ParkingUsageModel(user_id=booking['user_id'], parking_id=booking['parking_id'], \
        booking_id=booking_id, start_day=booking['start_day'], start_time=booking['start_time'], \
        end_day=booking['end_day'], end_time=booking['end_time'], charge=booking['charge'])
    record.save()
    pass