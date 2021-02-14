from django.urls import path
from . import views
from .views import ParkingAdminCreate, CreateCarAdminView, SettingAdminInfo, DownloadData, UploadData

app_name = 'administrator'
urlpatterns = [
    path('', views.admin_main, name='admin_main'),
    path('ajax/', views.test_ajax_response),
    path('createparking/', views.index, name='createparking'),
    path('create/', ParkingAdminCreate.as_view(), name='create'),
    path('checkparking/', views.checkparking, name='checkparking'),
    path('edit/', views.edit, name='edit'),
    path('delete/<int:num>', views.delete, name='delete'),
    path('createCar/', CreateCarAdminView.as_view(), name='createCar'),
    path('checkcar/', views.checkcar, name='checkcar'),
    path('settinginfo/', SettingAdminInfo.as_view(), name='settinginfo'),
    path('createsetting/<int:num>', views.CreateSetting, name='createsetting'),
    path('deletesetting/<int:num>', views.DeleteSetting, name='deletesetting'),
    path('stationarea/', views.StationArea, name='stationarea'),
    path('superuser/', views.superuser, name='superuser'),
    path('download_data/', DownloadData.as_view(), name='download_data'),
    path('upload_data/', UploadData.as_view(), name='upload_data'),
    path('mobile/', views.mobile, name='mobile'),
    path('survey/', views.survey, name='survey')
]