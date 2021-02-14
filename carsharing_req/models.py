from django.db import models
from carsharing_booking .models import BookingModel
from owners_req .models import CarInfoModel
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.core.validators import FileExtensionValidator

import numpy as np
import tensorflow.compat.v1 as tf
from tensorflow import keras
from tensorflow.keras.models import load_model
from PIL import Image
import io, base64



# Create your models here.

class CarsharUserModel(models.Model):
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    first_ja = models.CharField(max_length=100)
    last_ja = models.CharField(max_length=100)
    email = models.EmailField(max_length=200)
    gender = models.BooleanField()
    age = models.IntegerField(default=0)
    birthday = models.DateField()
    tel = models.CharField(max_length=15, \
        validators=[RegexValidator(r'^\d{10}$|^\d{11}$', 'ハイフン無しの数字で入力して下さい。')] )
    zip01 = models.IntegerField(validators=[RegexValidator(r'^\d{7}$', 'ハイフン無しの数字で入力して下さい。'), MaxValueValidator(9999999)] )
    pref01 = models.CharField(max_length=100)
    addr01 = models.CharField(max_length=100)
    addr02 = models.CharField(max_length=100)
    system_flag = models.IntegerField(default=0)
    # img = models.FileField(
    img = models.ImageField(
        upload_to='users/license/%Y/%m/%d/',
        #拡張子バリデーター。アップロードファイルの拡張子が違う時にエラー
        validators=[FileExtensionValidator(['jpg','png','gif', ])],
        blank=True, 
        null=True
    )
    # カード情報
    credit_card_company = models.CharField(max_length=50)
    first_en = models.CharField(max_length=100, \
        validators=[RegexValidator(r'^[A-Z]*$', '半角英大文字で入力して下さい。')] )
    last_en = models.CharField(max_length=100, \
        validators=[RegexValidator(r'^[A-Z]*$', '半角英大文字で入力して下さい。')] )
    credit_card_num = models.CharField(max_length=300, \
        validators=[RegexValidator(r'^\d{16}$')] )
        # 本番用バリデーション
        # '^(4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12}|^(?:2131|1800|35\d{3})\d{11}$)$'
    credit_card_num_check = models.IntegerField(validators=[MinValueValidator(100), MaxValueValidator(999)])
    valid_thru = models.CharField(max_length=5, \
        validators=[RegexValidator(r'^([0-9]{2})[/]([0-9]{2})$', '月/年\nの型式で入力して下さい。\t\t例:2025年3月の場合\n03/25')] )
    credit_card_num_check = models.IntegerField(validators=[MinValueValidator(000), MaxValueValidator(999)]) 
    security_code = models.CharField(max_length=300, \
        validators=[RegexValidator(r'^\d{3}$')] )
    # security_code = models.IntegerField(validators=[MinValueValidator(100), MaxValueValidator(999)])
    plan = models.CharField(max_length=30)
    charge = models.IntegerField(default=0)
    charge_flag = models.BooleanField(default=False)

    
    def __str__(self):
        return '<Friend:id=' + str(self.id) + ',' + self.first_name + ' ' + self.last_name + '(' + str(self.age) + ')>'


class UsageModel(models.Model):
    
    user_id = models.IntegerField()
    car_id = models.IntegerField()
    booking_id = models.ForeignKey(BookingModel, verbose_name='予約番号', default=0, on_delete=models.PROTECT)
    start_day = models.CharField(verbose_name='開始日', max_length=10)
    start_time = models.CharField(verbose_name='開始時刻', max_length=5)
    end_day = models.CharField(verbose_name='終了日', max_length=10)
    end_time = models.CharField(verbose_name='終了時刻', max_length=5)
    charge = models.IntegerField(default=1000, verbose_name='利用料金')
    regist_date = models.DateTimeField(default=timezone.now, verbose_name='登録日時')

    def __str__(self):
        return '<carshar_usage_id=' + str(self.id) + '>'

graph = tf.get_default_graph()

class Photo(models.Model):
    image = models.ImageField(upload_to='photos')

    IMAGE_SIZE = 224 # 画像サイズ
    MODEL_FILE_PATH = './vgg16_transfer.h5' # モデルファイル
    classes = ["免許証写真", "保険証写真"]
    num_classes = len(classes)

    # 引数から画像ファイルを参照して読み込む
    def predict(self):
        model = None
        global graph
        with graph.as_default():
            model = load_model(self.MODEL_FILE_PATH)

            img_data = self.image.read()
            img_bin = io.BytesIO(img_data)
            img_bin.seek(0)

            image = Image.open(img_bin)
            image = image.convert("RGB")
            image = image.resize((self.IMAGE_SIZE, self.IMAGE_SIZE))
            data = np.asarray(image) / 255.0
            X = []
            X.append(data)
            X = np.array(X)

            result = model.predict([X])[0]
            predicted = result.argmax()
            percentage = int(result[predicted] * 100)

            print(image)
            print(self.classes[predicted], percentage)
            return self.classes[predicted], percentage

    def image_src(self):
        with self.image.open() as img:
            base64_img = base64.b64encode(img.read()).decode()

            return 'data:' + img.file.content_type + ';base64,' + base64_img


class UserFavoriteCarModel(models.Model):
    user_id = models.IntegerField(default=0, verbose_name='ユーザID')
    favorite_car_id = models.ForeignKey(CarInfoModel, on_delete=models.CASCADE, verbose_name='お気に入り車両ID')
    def __str__(self):
        return '<user_id=' +str(self.user_id) + str(self.favorite_car_id) + '>'