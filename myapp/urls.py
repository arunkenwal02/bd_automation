from django.urls import path
from .views import *


urlpatterns = [
    path('createproject/', CreateProject.as_view()),
    path('insertparam/', ExcelImport.as_view()),
    path('logs/', Logs.as_view()),
    path('retrieve/', RetrieveApi.as_view()),
    path('del/<int:pk>/', DelApi.as_view()),
    path('delete/', EmptyProjectTable.as_view())
]