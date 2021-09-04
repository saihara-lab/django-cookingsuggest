from django import forms # Djangoが準備しているforms
from .models import DishHistory, DishMaster, DietaryReferenceIntake # モデルの部分で定義したDBのテーブル
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User # 追加

class DishHistoryInputForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DishHistoryInputForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
    # DBの内容のメタ情報を記載しています
    class Meta:
        model = DishHistory
        exclude = ['id', 'nutrition_result', 'nutrition_proba', 'i_p_result', 'i_p_proba', 'sim_dish_ntr', 'sim_dish_ip', 'recommend_dish','registered_date']

class DishHistoryModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DishHistoryModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
    # DBの内容のメタ情報を記載しています
    class Meta:
        model = DishHistory
        exclude = ['id', 'nutrition_result', 'nutrition_proba', 'i_p_result', 'i_p_proba', 'registered_date']

class DishMasterModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(DishMasterModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
    # DBの内容のメタ情報を記載しています
    class Meta:
        model = DishMaster
        exclude = ['id', 'cluster_ntr', 'cluster_ip' 'registered_date']

class RecommendByDriModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(RecommendByDriModelForm, self).__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
    # DBの内容のメタ情報を記載しています
    class Meta:
        model = DietaryReferenceIntake
        fields = ['age_range', 'gender']

# ログインフォーム
class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

# サインアップフォーム
class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        #htmlの表示を変更可能にします
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', )