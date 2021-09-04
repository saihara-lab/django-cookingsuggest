from django.db import models
from datetime import date

class DishHistory(models.Model):
  
  # DBのカラム相当部分の定義
  id = models.AutoField(primary_key=True)
  name = models.CharField('料理名', max_length=50)
  energy = models.IntegerField('エネルギー', null=False)
  carbohydrate = models.FloatField('炭水化物', null=False)
  protein = models.FloatField('タンパク質', null=False)
  fat = models.FloatField('脂質', null=False)
  calcium = models.IntegerField('カルシウム', null=False)
  iron = models.FloatField('鉄分', null=False)
  vitamin_a = models.IntegerField('ビタミンA', null=False)
  vitamin_b1 = models.FloatField('ビタミンB1', null=False)
  vitamin_b2 = models.FloatField('ビタミンB2', null=False)
  vitamin_c = models.IntegerField('ビタミンC', null=False)
  #cover_amt = models.IntegerField('材料〜人前', null=False)
  ingredient = models.TextField('材料', null=False)
  process = models.TextField('調理工程', null=False)
  nutrition_result = models.IntegerField(blank=True, null=True)
  nutrition_proba = models.FloatField(default=0.0)
  i_p_result = models.IntegerField(blank=True, null=True)
  i_p_proba = models.FloatField(default=0.0)
  sim_dish_ntr = models.TextField('似ている料理:栄養', blank=True, null=True)
  sim_dish_ip = models.TextField('似ている料理:材料・工程', blank=True, null=True)
  recommend_dish = models.TextField('おすすめの組み合わせ', blank=True, null=True)
  registered_date = models.DateField(default=date.today())

  # 管理画面の表示方法を定義
  def __str__(self):
    if self.nutrition_proba == 0.0 and self.i_p_proba == 0.0:
        return '%d, %s, %s' % (self.id, self.name, self.registered_date)
    else:
        return '%d, %s, %s, %s, %s' % (self.id, self.name, self.registered_date, self.nutrition_result, self.i_p_result)


class DishMaster(models.Model):
  
  # DBのカラム相当部分の定義
  id = models.AutoField(primary_key=True)
  name = models.CharField('料理名', max_length=50)
  energy = models.IntegerField('エネルギー', null=True)
  carbohydrate = models.FloatField('炭水化物', null=True)
  protein = models.FloatField('タンパク質', null=True)
  fat = models.FloatField('脂質', null=True)
  calcium = models.FloatField('カルシウム', null=True)
  iron = models.FloatField('鉄分', null=True)
  vitamin_a = models.FloatField('ビタミンA', null=True)
  vitamin_b1 = models.FloatField('ビタミンB1', null=True)
  vitamin_b2 = models.FloatField('ビタミンB2', null=True)
  vitamin_c = models.FloatField('ビタミンC', null=True)
  #cover_amt = models.IntegerField('材料〜人前', null=False)
  ingredient = models.TextField('材料', null=True)
  process = models.TextField('調理工程', null=True)
  cluster_ntr = models.FloatField('分類:栄養', null=True)
  cluster_ip = models.FloatField('分類:材料・工程', null=True)
  sim_dish_ntr = models.TextField('似ている料理:栄養', null=True)
  sim_dish_ip = models.TextField('似ている料理:材料・工程', null=True)
  recommend_dish = models.TextField('おすすめの組み合わせ', null=True)
  registered_date = models.DateField(default=date.today())

  # 管理画面の表示方法を定義
  def __str__(self):
    return '%d, %s, %s' % (self.id, self.name, self.registered_date)

class DietaryReferenceIntake(models.Model):

  age_range_options = (
    (1, '18～29歳'),
    (2, '30歳～49歳'),
    (3, '50歳～64歳'),
  )

  gender_options = (
    (1, '男性'),
    (2, '女性'),
  )

  # DBのカラム相当部分の定義
  id = models.AutoField(primary_key=True)
  age_range = models.IntegerField('年齢区分', choices=age_range_options, default=0)
  gender = models.IntegerField('性別', choices=gender_options, default=0)
  energy = models.IntegerField('エネルギー', null=False)
  protein = models.FloatField('タンパク質', null=False)
  fat = models.FloatField('脂質', null=False)
  calcium = models.IntegerField('カルシウム', null=False)
  iron = models.FloatField('鉄分', null=False)
  vitamin_a = models.IntegerField('ビタミンA', null=False)
  vitamin_b1 = models.FloatField('ビタミンB1', null=False)
  vitamin_b2 = models.FloatField('ビタミンB2', null=False)
  vitamin_c = models.IntegerField('ビタミンC', null=False)
  registered_date = models.DateField(default=date.today())

  # 管理画面の表示方法を定義
  def __str__(self):
    return '%d, %d, %d, %s' % (self.id, self.age_range, self.gender, self.registered_date)
