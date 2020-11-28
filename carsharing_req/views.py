from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.views import generic
from .models import CarsharUserModel
from .forms import CarsharUserCreateForm
from parking_req .models import *
from owners_req .models import HostUserModel

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
    print(data.id)
    request.session['user_id'] = data.id
    print(request.session['user_id'])
    paking_data = ParkingUserModel.objects.filter(user_id=data.id)
    if paking_data.first() is None:
        print('no data')
        request.session['parking_flag'] = False
    else:
        print(paking_data.values('user_id', 'id'))
        request.session['parking_flag'] = True

    owner_data = HostUserModel.objects.filter(user_id=data.id)
    if owner_data.first() is None:
        print('no data')
        request.session['owner_flag'] = False
    else:
        print(owner_data.values('user_id', 'id'))
        request.session['owner_flag'] = True



    return redirect(to='carsharing_req:index')


# 説明ページ(HTML)ルーティング
def pages(request, num):
    if num == 1:
        return render(request, 'user_car.html')
    elif num == 2:
        return render(request, 'user_parking.html')
    elif num == 3:
        return render(request, 'owner_car.html')
    elif num == 4:
        return render(request, 'owner_parking.html')
    elif num == 0:
        pass
    else:
        return redirect(to='carsharing_req:index')


class CarsharUserInfo(TemplateView):
    def __init__(self):
        self.params = {
            'title': 'Hello World!',
            'message': 'Not found your data.<br>Please send your profile.',
            'form': CarsharUserCreateForm(),
            'link': 'other',
        }
    
    def get(self, request):
        if str(request.user) == "AnonymousUser":
            print('ゲスト')
        else:
            print(request.user)
        # return render(request, 'carsharing_req/index.html', self.params)
        return render(request, 'carsharing_req/top.html', self.params)
    
    def post(self, request):
        msg = 'Your name is <b>' + request.POST['name'] + \
            '(' + request.POST['age'] + \
            ')</b><br>Your mail address is <b>' + request.POST['email'] + \
            '</b><br>Thank you send to me!'
        self.params['message'] = msg
        self.params['form'] = CarsharUserCreateForm(request.POST)
        return render(request, 'carsharing_req/index.html', self.params)

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
        'title': 'Member Create',
        'form': CarsharUserCreateForm(),
    }

    def post(self, request):
        
        email = request.user.email
        name = request.POST['name']
        gender = 'gender' in request.POST
        age = request.POST['age']
        birthday = request.POST['birthday']
        zip01 = request.POST['zip01']
        pref01 = request.POST['pref01']
        addr01 = request.POST['addr01']
        addr02 = request.POST['addr02']
        record = CarsharUserModel(email = email,name = name, gender = gender, age = age, birthday = birthday, zip01 = zip01, pref01 = pref01, addr01 = addr01, addr02 = addr02)
        record.save()
        return redirect(to='carsharing_req:first')
        
    def get(self, request):
        querySet = CarsharUserModel.objects.filter(email__contains = request.user.email)
        if querySet.first() is None:
            print('no data')
        else:
            print('data　exist')
            return redirect(to='carsharing_req:index')
        return render(request, 'carsharing_req/create.html', self.params)