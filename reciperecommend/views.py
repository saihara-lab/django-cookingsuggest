from django.shortcuts import render, redirect
from .forms import DishHistoryModelForm, DishHistoryInputForm, DishMasterModelForm, RecommendByDriModelForm, LoginForm, SignUpForm
from django.views.generic import DetailView, ListView
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum

import joblib
import numpy as np
from django_pandas.io import read_frame
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import MeCab
from gensim.models.doc2vec import Doc2Vec
from gensim.models.doc2vec import TaggedDocument

from .models import DishHistory, DishMaster, DietaryReferenceIntake


# 履歴登録した料理を分類するモデル
loaded_model_nutrition = joblib.load('model/recipe_classifier_ntr.pkl')
loaded_model_ip = joblib.load(('model/recipe_classifier_ip.pkl'))
# 履歴登録した料理の材料・工程から文書ベクトルを取得するモデル
loaded_model_doc2vec = Doc2Vec.load('model/ip_doc2vec.model')

@login_required
def index(request):
    return render(request, 'reciperecommend/index.html')

@login_required
def dish_history_input_form(request):

  if request.method == 'POST':
    form = DishHistoryInputForm(request.POST)
    if form.is_valid():
      form.save()
      return redirect('dish_classify_result')
  else:
    form = DishHistoryInputForm()
    return render(request, 'reciperecommend/dish_history_input_form.html', {'form':form})

@login_required
def dish_classify_result(request):
  ## 最新の料理履歴データを取得
  # ■１．栄養
  data_n = DishHistory.objects.order_by('id').reverse().values_list('protein', 'fat', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c')
  # 材料・工程
  data_ip = DishHistory.objects.order_by('id').reverse().values_list('ingredient', 'process')

  ## 推論の実行
  # 栄養
  x_n = np.array([data_n[0]])
  y_n = loaded_model_nutrition.predict(x_n)
  y_n_proba = loaded_model_nutrition.predict_proba(x_n)
  y_n_proba = y_n_proba * 100  # 予測確率を*100
  y_n, y_n_proba = y_n[0], y_n_proba[0]  # それぞれ0番目を取り出す

  # 推論結果を保存
  dish = DishHistory.objects.order_by('id').reverse()[0]
  dish.nutrition_proba = y_n_proba[y_n] # 栄養
  dish.nutrition_result = y_n

  ## 推論結果のクラスタに該当するデータを抽出
  same_cluster_data = DishMaster.objects.filter(cluster_ntr=y_n).order_by('id').values_list('protein', 'fat', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c')
  same_cluster_idx = DishMaster.objects.filter(cluster_ntr=y_n).order_by('id').values_list('id')
  same_cluster_idx = [int(idx[0]) for idx in same_cluster_idx]

  # 栄養のコサイン類似度が高い上位3件の料理のIDを取得
  tgt = x_n.flatten()
  tgt = [float(t) for t in tgt]
  tgt = np.array(tgt)
  cos_sims = {}
  for idx, data in zip(same_cluster_idx, same_cluster_data):
    vec = np.array(data)

    cs = round(float(cosine_similarity(tgt.reshape(1, -1), vec.reshape(1, -1))),3)
    cos_sims[idx] = cs

  cos_sims_top3 = sorted(cos_sims.items(), key=lambda x:x[1], reverse=True)[:3]
  top3_idx = [k[0] for k in cos_sims_top3]

  sim_dish_ntr_list = DishMaster.objects.filter(id__in = top3_idx).values_list('name')
  sim_dish_ntr_list = [n[0] for n in sim_dish_ntr_list]
  dish.sim_dish_ntr = ' '.join(sim_dish_ntr_list)

  # ■２．材料・工程
  # 前処理と形態素解析
  data_ip_tgt = data_ip[0]
  data_ip_tgt = data_ip_tgt[0] + data_ip_tgt[0]
  data_ip_tgt = data_ip_tgt.replace('\n', '') # 改行コードを削除
  data_ip_mst = list(DishMaster.objects.order_by('id').values_list('id','ingredient', 'process'))
  data_ip_mst_id = []
  data_ip_preprocessed = []
  for d in data_ip_mst:
    x_ip_text = d[1] + d[2]
    x_ip_text = x_ip_text.replace('\n', '') # 改行コードを削除
    data_ip_mst_id.append(d[0])
    data_ip_preprocessed.append(x_ip_text)

  def keitaiso(text):
    tagger = MeCab.Tagger("-Ochasen")
    tagger.parse("")
    node = tagger.parseToNode(text)
    word = ""
    pre_feature = ""
    while node:
          # 名詞、形容詞、動詞、形容動詞であるかを判定する。
      HANTEI = "名詞" in node.feature
      HANTEI = "形容詞" in node.feature or HANTEI
      HANTEI = "動詞" in node.feature or HANTEI
      HANTEI = "形容動詞" in node.feature or HANTEI
          # 以下に該当する場合は除外する。（ストップワード）
      HANTEI = (not "代名詞" in node.feature) and HANTEI
      HANTEI = (not "助動詞" in node.feature) and HANTEI
      HANTEI = (not "非自立" in node.feature) and HANTEI
      HANTEI = (not "数" in node.feature) and HANTEI
      HANTEI = (not "人名" in node.feature) and HANTEI
      if HANTEI:
        if ("名詞接続" in pre_feature and "名詞" in node.feature) or ("接尾" in node.feature):
          word += "{0}".format(node.surface)
        else:
          word += " {0}".format(node.surface)
        #print("{0}{1}".format(node.surface, node.feature))
      pre_feature = node.feature
      node = node.next
    return word[1:]
  
  tgt_word_list = keitaiso(data_ip_tgt).split(' ')
  mst_word_lists = [keitaiso(d).split(' ') for d in data_ip_preprocessed]

  ## 文書ベクトル類似度トップ３取得
  doc_sim = {}
  for id, data in zip(data_ip_mst_id, mst_word_lists):
    sim = loaded_model_doc2vec.docvecs.similarity_unseen_docs(loaded_model_doc2vec, tgt_word_list, data, alpha=1, min_alpha=0.0001, steps=5)
    doc_sim[id] = sim

  doc_sim_top3_ip = sorted(doc_sim.items(), key=lambda x:x[1], reverse=True)[:3]
  top3_idx_ip = [k[0] for k in doc_sim_top3_ip]

  sim_dish_ip_list = DishMaster.objects.filter(id__in = top3_idx_ip).values_list('name')
  sim_dish_ip_list = [n[0] for n in sim_dish_ip_list]
  dish.sim_dish_ip = ' '.join(sim_dish_ip_list)

  dish.save() # データを保存

  # 推論結果をHTMLに渡す
  return render(request, 'reciperecommend/dish_classify_result.html', {'nutrition_y':y_n, 'nutrition_y_proba':round(y_n_proba[y_n], 2), 'dish_sim_ntr': dish.sim_dish_ntr, 'dish_sim_ip': dish.sim_dish_ip})

# 料理履歴
@login_required
def dish_history(request):
  # 削除ボタンが押された場合の処理
  if request.method == 'POST':
    d_id = request.POST
    d_dish = DishHistory.objects.filter(id=d_id['d_id'])
    d_dish.delete()
    dishes = DishHistory.objects.all()
    return render(request, 'reciperecommend/dish_history.html', {'dishes':dishes})
  else:
    dishes = DishHistory.objects.all()
    return render(request, 'reciperecommend/dish_history.html', {'dishes':dishes})

# 料理履歴詳細
@login_required
def dish_history_detail(request, id):
  obj = DishHistory.objects.get(pk=id)
  form = DishHistoryModelForm(instance=obj)
  return render(request, 'reciperecommend/dish_history_detail.html', {
    'id': id,
    'form': form,
    'data': obj
  })

# 料理履歴編集
@login_required
def dish_history_edit(request, id):
  obj = DishHistory.objects.get(pk=id)
  form = DishHistoryModelForm(instance=obj)
  return render(request, 'reciperecommend/dish_history_edit.html',{
    'id': id,
    'form': form
  })

# 料理履歴更新
@require_POST
def dish_history_update(request, id):
  # ポストデータと既存のモデルのデータを東郷
  obj = DishHistory.objects.get(pk=id)
  form = DishHistoryModelForm(request.POST, instance=obj)
  if form.is_valid():
    # 検証に通過したものを反映
    form.save()
    messages.success(request, '料理を更新しました。')
    return redirect(reverse('dish_history_edit', kwargs={'id': id}))
  else:
    return render(request, 'reciperecommend/dish_history_edit.html',{
    'id': id,
    'form': form
  })

# 料理履歴削除
@require_POST
def dish_history_delete(request, id):
  obj = DishHistory.objects.get(pk=id)
  obj.delete()
  messages.success(request, '料理を削除しました。')
  return redirect(reverse('dish_history'))

# 料理マスタ一覧
#@method_decorator(require_POST, name='dispatch')
class DishMasterList(ListView):
  model = DishMaster

  def get_queryset(self):
    q_word = self.request.GET.get('query')

    if q_word:
        object_list = DishMaster.objects.filter(
            Q(name__icontains=q_word) | Q(ingredient__icontains=q_word))
    else:
        object_list = DishMaster.objects.all()
    return object_list

# 料理マスタ詳細
@login_required
def dish_master_detail(request, id):
  obj = DishMaster.objects.get(pk=id)
  return render(request, 'reciperecommend/dish_master_detail.html', {
    'id': id,
    'data': obj
  })

# RCIから料理をレコメンド：年齢・性別入力
@login_required
def recommend_by_dri(request):
  if request.method == 'POST':
    age_range = request.POST.get('age_range')
    gender = request.POST.get('gender')

    tgt_dri = DietaryReferenceIntake.objects.filter(age_range=age_range, gender=gender).order_by('id').reverse().values_list('protein', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c')

    tgt_protein_sum = DishHistory.objects.order_by('id').reverse()[:21].aggregate(Sum('protein'))
    tgt_calcium_sum = DishHistory.objects.order_by('id').reverse()[:21].aggregate(Sum('calcium'))
    tgt_iron_sum = DishHistory.objects.order_by('id').reverse()[:21].aggregate(Sum('iron'))
    tgt_vitamin_a_sum = DishHistory.objects.order_by('id').reverse()[:21].aggregate(Sum('vitamin_a'))
    tgt_vitamin_b1_sum = DishHistory.objects.order_by('id').reverse()[:21].aggregate(Sum('vitamin_b1'))
    tgt_vitamin_b2_sum = DishHistory.objects.order_by('id').reverse()[:21].aggregate(Sum('vitamin_b2'))
    tgt_vitamin_c_sum = DishHistory.objects.order_by('id').reverse()[:21].aggregate(Sum('vitamin_c'))

    tgt_dri_weeksum = [float(tgt_dri[0][i]) * 7 for i in range(7)]

    messages = []
    #if tgt_ntr_sum.sum_protein < tgt_dri_weeksum[0]:
    if tgt_protein_sum['protein__sum'] < tgt_dri_weeksum[0]:
      messages.append('タンパク質')
    #if tgt_ntr.sum_calcium < tgt_dri_weeksum[1]:
    if tgt_calcium_sum['calcium__sum'] < tgt_dri_weeksum[1]:
      messages.append('カルシウム')
    #if tgt_ntr.sum_iron < tgt_dri_weeksum[2]:
    if tgt_iron_sum['iron__sum'] < tgt_dri_weeksum[2]:
      messages.append('鉄分')
    #if tgt_ntr.vitamin_a < tgt_dri_weeksum[3]:
    if tgt_vitamin_a_sum['vitamin_a__sum'] < tgt_dri_weeksum[3]:
      messages.append('ビタミンA')
    #if tgt_ntr.vitamin_b1 < tgt_dri_weeksum[4]:
    if tgt_vitamin_b1_sum['vitamin_b1__sum'] < tgt_dri_weeksum[4]:
      messages.append('ビタミンB1')
    #if tgt_ntr.vitamin_b2 < tgt_dri_weeksum[5]:
    if tgt_vitamin_b2_sum['vitamin_b2__sum'] < tgt_dri_weeksum[5]:
      messages.append('ビタミンB2')
    #if tgt_ntr.vitamin_c < tgt_dri_weeksum[6]:
    if tgt_vitamin_c_sum['vitamin_c__sum'] < tgt_dri_weeksum[6]:
      messages.append('ビタミンC')


    necessary_ntr = []

    ## タンパク質
    # 栄養が目標に届かない場合
    if tgt_dri_weeksum[0] - tgt_protein_sum['protein__sum'] > 0:
      necessary_ntr.append((tgt_dri[0][0] / 3) + ((tgt_dri_weeksum[0] - tgt_protein_sum['protein__sum']) / 3))
    # 栄養が目標に届いた場合
    else:
      necessary_ntr.append(tgt_dri[0][0] / 3)

    ## カルシウム
    # 栄養が目標に届かない場合
    if tgt_dri_weeksum[1] - tgt_calcium_sum['calcium__sum'] > 0:
      necessary_ntr.append((tgt_dri[0][1] / 3) + ((tgt_dri_weeksum[1] - tgt_calcium_sum['calcium__sum']) / 3))
    # 栄養が目標に届いた場合
    else:
      necessary_ntr.append(tgt_dri[0][1] / 3)

    ## 鉄分
    # 栄養が目標に届かない場合
    if tgt_dri_weeksum[2] - tgt_iron_sum['iron__sum'] > 0:
      necessary_ntr.append((tgt_dri[0][2] / 3) + ((tgt_dri_weeksum[2] - tgt_iron_sum['iron__sum']) / 3))
    # 栄養が目標に届いた場合
    else:
      necessary_ntr.append(tgt_dri[0][2] / 3)

    ## ビタミンA
    # 栄養が目標に届かない場合
    if tgt_dri_weeksum[3] - tgt_vitamin_a_sum['vitamin_a__sum'] > 0:
      necessary_ntr.append((tgt_dri[0][3] / 3) + ((tgt_dri_weeksum[3] - tgt_vitamin_a_sum['vitamin_a__sum']) / 3))
    # 栄養が目標に届いた場合
    else:
      necessary_ntr.append(tgt_dri[0][3] / 3)

    ## ビタミンB1
    # 栄養が目標に届かない場合
    if tgt_dri_weeksum[4] - tgt_vitamin_b1_sum['vitamin_b1__sum'] > 0:
      necessary_ntr.append((tgt_dri[0][4] / 3) + ((tgt_dri_weeksum[4] - tgt_vitamin_b1_sum['vitamin_b1__sum']) / 3))
    # 栄養が目標に届いた場合
    else:
      necessary_ntr.append(tgt_dri[0][4] / 3)

    ## ビタミンB2
    # 栄養が目標に届かない場合
    if tgt_dri_weeksum[5] - tgt_vitamin_b2_sum['vitamin_b2__sum'] > 0:
      necessary_ntr.append((tgt_dri[0][5] / 3) + ((tgt_dri_weeksum[5] - tgt_vitamin_b2_sum['vitamin_b2__sum']) / 3))
    # 栄養が目標に届いた場合
    else:
      necessary_ntr.append(tgt_dri[0][5] / 3)

    ## ビタミンC
    # 栄養が目標に届かない場合
    if tgt_dri_weeksum[6] - tgt_vitamin_c_sum['vitamin_c__sum'] > 0:
      necessary_ntr.append((tgt_dri[0][6] / 3) + ((tgt_dri_weeksum[6] - tgt_vitamin_c_sum['vitamin_c__sum']) / 3))
    # 栄養が目標に届いた場合
    else:
      necessary_ntr.append(tgt_dri[0][6] / 3)

    necessary_ntr = np.array(necessary_ntr)

    # コサイン類似度上位3つの料理を取得
    dish_data_all = DishMaster.objects.all().values_list('protein', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c')
    dish_data_idx = DishMaster.objects.all().values_list('id')
    dish_data_idx = [int(idx[0]) for idx in dish_data_idx]

    cos_sims = {}
    for idx, data in zip(dish_data_idx, dish_data_all):
      vec = np.array(data)

      cs = round(float(cosine_similarity(necessary_ntr.reshape(1, -1), vec.reshape(1, -1))),3)
      cos_sims[idx] = cs

    cos_sims_top3 = sorted(cos_sims.items(), key=lambda x:x[1], reverse=True)[:3]
    top3_idx = [k[0] for k in cos_sims_top3]

    recommend_dish_list = DishMaster.objects.filter(id__in = top3_idx).values_list('name')
    recommend_dish_list = [n[0] for n in recommend_dish_list]

    return render(request, 'reciperecommend/recommend_by_dri.html', {
      'message_label': '不足している栄養',
      'messages': messages,
      'recomend_dish_label': 'おすすめの料理',
      'recommend_dish_list': recommend_dish_list
    })

  else:

    messages = '年齢と性別を入力して、ボタンを押してください'
    form = RecommendByDriModelForm()

    return render(request, 'reciperecommend/recommend_by_dri.html', {
      'form': form
  })

# ログインページ
class Login(LoginView):
  form_class = LoginForm
  template_name = 'reciperecommend/login.html'

# ログアウトページ
class Logout(LogoutView):
  template_name = 'reciperecommend/base.html'

# サインアップ
def signup(request):
  if request.method == 'POST':
    form = SignUpForm(request.POST)
    if form.is_valid():
      form.save()
      #フォームから'username'を読み取る
      username = form.cleaned_data.get('username')
      #フォームから'password1'を読み取る
      password = form.cleaned_data.get('password1')
      # 読み取った情報をログインに使用する情報として new_user に格納
      new_user = authenticate(username=username, password=password)
      if new_user is not None:
        # new_user の情報からログイン処理を行う
        login(request, new_user)
        # ログイン後のリダイレクト処理
        return redirect('index')
  # POST で送信がなかった場合の処理
  else:
    form = SignUpForm()
    return render(request, 'reciperecommend/signup.html', {'form':form})

def lp(request):
    return render(request, 'reciperecommend/lp.html')

"""
## 新規登録時の材料・工程の推論と類似度の取得：TF-IDF
@login_required
def dish_classify_result(request):
  ## 最新の料理履歴データを取得
  # 栄養
  data_n = DishHistory.objects.order_by('id').reverse().values_list('protein', 'fat', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c')
  # 材料・工程
  data_ip = DishHistory.objects.order_by('id').reverse().values_list('ingredient', 'process')

  ## 推論の実行
  # 栄養
  x_n = np.array([data_n[0]])
  y_n = loaded_model_nutrition.predict(x_n)
  y_n_proba = loaded_model_nutrition.predict_proba(x_n)
  y_n_proba = y_n_proba * 100  # 予測確率を*100
  y_n, y_n_proba = y_n[0], y_n_proba[0]  # それぞれ0番目を取り出す

  # 材料・工程
  # 前処理と形態素解析
  data_ip_tgt = data_ip[0]

  data_ip_mst = list(DishMaster.objects.values_list('ingredient', 'process'))
  data_ip_mst.append(data_ip_tgt)

  x_ip_preprocessed = []
  for d in data_ip_mst:
    x_ip_text = d[0] + d[1]
    x_ip_text = x_ip_text.replace('\n', '') # 改行コードを削除
    x_ip_preprocessed.append(x_ip_text)

  mecab = MeCab.Tagger('-Ochasen')

  nva_parse_all = []
  for x in x_ip_preprocessed:
    res = mecab.parse(x)
    words = res.split('\n')[:-2]

    nva_list = []
    for word in words:
      part = word.split('\t')
      if ('名詞-一般' in part[3] or '動詞-自立' in part[3] or '形容詞-自立' in part[3]) and part[0] != '゙':
        nva_list.append(part[2])
    nva_parse = ' '.join(nva_list)
    nva_parse_all.append(nva_parse)

  # TF-IDFを取得
  vectorizer = TfidfVectorizer()
  tfidf_all = vectorizer.fit_transform(nva_parse_all)
  tfidf_tgt = tfidf_all[-1]

  # 推論結果を保存
  dish = DishHistory.objects.order_by('id').reverse()[0]
  dish.nutrition_proba = y_n_proba[y_n] # 栄養
  dish.nutrition_result = y_n

  ## 推論結果のクラスタに該当するデータを抽出
  #df_target = read_frame(dish, fieldnames=['protein', 'fat', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c'])
  #target_data = df_target.values

  #same_cluster_obj = DishMaster.objects.filter(cluster=y_n).order_by('id').values_list('id', 'protein', 'fat', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c')
  #df_m_ntr = read_frame(same_cluster_obj, fieldnames=['id', 'protein', 'fat', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c'])
  #same_cluster_data = df_m_ntr.drop('id', axis=1).values
  #same_cluster_idx = df_m_ntr['id'].values

  same_cluster_data = DishMaster.objects.filter(cluster_ntr=y_n).order_by('id').values_list('protein', 'fat', 'calcium', 'iron', 'vitamin_a', 'vitamin_b1', 'vitamin_b2', 'vitamin_c')
  same_cluster_idx = DishMaster.objects.filter(cluster_ntr=y_n).order_by('id').values_list('id')
  same_cluster_idx = [int(idx[0]) for idx in same_cluster_idx]

  # 栄養のコサイン類似度が高い上位3件の料理のIDを取得
  tgt = x_n.flatten()
  tgt = [float(t) for t in tgt]
  tgt = np.array(tgt)
  cos_sims = {}
  for idx, data in zip(same_cluster_idx, same_cluster_data):
    vec = np.array(data)

    cs = round(float(cosine_similarity(tgt.reshape(1, -1), vec.reshape(1, -1))),3)
    cos_sims[idx] = cs

  cos_sims_top3 = sorted(cos_sims.items(), key=lambda x:x[1], reverse=True)[:3]
  top3_idx = [k[0] for k in cos_sims_top3]

  sim_dish_ntr_list = DishMaster.objects.filter(id__in = top3_idx).values_list('name')
  sim_dish_ntr_list = [n[0] for n in sim_dish_ntr_list]
  dish.sim_dish_ntr = ' '.join(sim_dish_ntr_list)

  # 材料・工程のコサイン類似度が高い上位3件の料理のIDを取得
  other_ip_idx = DishMaster.objects.order_by('id').values_list('id')
  other_ip_idx = [int(idx[0]) for idx in other_ip_idx]
  cos_sims_ip = {}
  for idx, data in zip(other_ip_idx, tfidf_all):
    cs_ip = round(float(cosine_similarity(tfidf_tgt.reshape(1, -1), data.reshape(1, -1))),3)
    cos_sims_ip[idx] = cs_ip

  cos_sims_top3_ip = sorted(cos_sims_ip.items(), key=lambda x:x[1], reverse=True)[:3]
  top3_idx_ip = [k[0] for k in cos_sims_top3_ip]

  sim_dish_ip_list = DishMaster.objects.filter(id__in = top3_idx_ip).values_list('name')
  sim_dish_ip_list = [n[0] for n in sim_dish_ip_list]
  dish.sim_dish_ip = ' '.join(sim_dish_ip_list)

  dish.save() # データを保存

  # 推論結果をHTMLに渡す
  return render(request, 'reciperecommend/dish_classify_result.html', {'nutrition_y':y_n, 'nutrition_y_proba':round(y_n_proba[y_n], 2), 'dish_sim_ntr': dish.sim_dish_ntr, 'dish_sim_ip': dish.sim_dish_ip})

"""