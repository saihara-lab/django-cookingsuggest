from django.contrib import admin
from import_export.resources import ModelResource
from import_export.fields import Field
from import_export.admin import ImportExportMixin
from import_export.formats import base_formats

from .models import DishHistory, DishMaster, DietaryReferenceIntake

class DishMasterResource(ModelResource):

  #id = Field(attribute='id', column_name='料理名')
  name = Field(attribute='name', column_name='料理名')
  energy = Field(attribute='energy', column_name='エネルギー[キロカロリー]')
  carbohydrate = Field(attribute='carbohydrate', column_name='炭水化物[グラム]')
  protein = Field(attribute='protein', column_name='たんぱく質[グラム]')
  fat = Field(attribute='fat', column_name='脂質[グラム]')
  calcium = Field(attribute='calcium', column_name='カルシウム[mg]')
  iron = Field(attribute='iron', column_name='鉄分[mg]')
  vitamin_a = Field(attribute='vitamin_a', column_name='ビタミンA[ug]')
  vitamin_b1 = Field(attribute='vitamin_b1', column_name='ビタミンB1[mg]')
  vitamin_b2 = Field(attribute='vitamin_b2', column_name='ビタミンB2[mg]')
  vitamin_c = Field(attribute='vitamin_c', column_name='ビタミンC[mg]')
  #cover_amt = Field(attribute='cover_amt', column_name='人前')
  ingredient = Field(attribute='ingredient', column_name='材料')
  process = Field(attribute='process', column_name='調理工程')
  cluster_ntr = Field(attribute='cluster_ntr', column_name='n_cluster')
  cluster_ip = Field(attribute='cluster_ip', column_name='ip_cluster')
  sim_dish_ntr = Field(attribute='sim_dish_ntr', column_name='似ている料理_栄養')
  sim_dish_ip = Field(attribute='sim_dish_ip', column_name='似ている料理_材料・工程')
  recommend_dish = Field(attribute='recommend_dish', column_name='おすすめの組み合わせ')

  class Meta:
    model = DishMaster
    #import_order = ('id', 'name', 'energy', 'protein', 'fat', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c', 'cover_amt', 'ingredient', 'process')
    import_order = ('name', 'energy', 'protein', 'fat', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c', 'cover_amt', 'ingredient', 'process', 'cluster_ntr', 'cluster_ip', 'sim_dish_ntr', 'sim_dish_ip')
    #import_id_fields = ['id']

class DishMasterAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('id', 'name')
    resource_class = DishMasterResource
    formats = [base_formats.CSV]

admin.site.register(DishHistory)
admin.site.register(DishMaster, DishMasterAdmin)
admin.site.register(DietaryReferenceIntake)
