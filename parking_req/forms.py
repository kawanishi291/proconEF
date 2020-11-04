from django import forms
from.models import ParkingUserModel

# class ParkingForm(forms.Form):

#     #carsharing_id = forms.IntegerField(label='カーシェアリングID')
#     #parking_id = forms.CharField(label='駐車場ID')
#     coordinate = forms.CharField(label='駐車場座標')
#     day = forms.DateField(label='登録日')
#     parking_type = forms.CharField(label='駐車場タイプ')
#     width = forms.IntegerField(label='横幅')
#     length = forms.IntegerField(label='奥行き')
#     height = forms.IntegerField(label='高さ')
#     car_id = forms.IntegerField(label='車両ID')

class ParkingForm(forms.ModelForm):
    class Meta:
        model = ParkingUserModel
        fields = ['coordinate','day','parking_type','width','length','height', 'car_id']
        widget = {
            'coordinate': forms.TextInput(attrs={'class': 'form-control'}),
            'day': forms.DateInput(attrs={'class': 'form-control'}),
            'parking_type': forms.NumberInput(attrs={'class': 'form-control'}),
            'width': forms.NumberInput(attrs={'class': 'form-control'}),
            'length': forms.NumberInput(attrs={'class': 'form-control'}),
            'height': forms.NumberInput(attrs={'class': 'form-control'}),
            'car_id': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'coordinate': '駐車場座標',
            'day': '登録日',
            'parking_type': '駐車場タイプ',
            'width': '横幅',
            'length': '奥行き',
            'height': '高さ',
            'car_id': '車両ID',
        }
