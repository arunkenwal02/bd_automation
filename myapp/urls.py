from django.urls import path
from .views import *


urlpatterns = [
    path('insertparam/', ExcelImport.as_view()),
    path('del/', DelApi.as_view())
]