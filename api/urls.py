from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Catch-all route to serve index.html for any unmatched path
    re_path(r'^.*$', views.index, name='catch_all'),
    path('find-drugs/', views.find_drugs, name='find_drugs'),
    path('get-symptoms-analysis/', views.get_symptoms_analysis, name='get_symptoms_analysis'),
    path('find-pharmacies/', views.find_pharmacies, name='find_pharmacies'),
    path('get-disease/', views.get_disease, name='get_disease'),
    path('get-familiar-drug/', views.get_familiar_drug, name='get_familiar_drug'),
    path('translate/', views.translate, name='translate'),
]
