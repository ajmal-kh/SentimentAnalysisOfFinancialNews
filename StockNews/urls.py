from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [

    # path('',views.greetings,name='home')
	url(r'',views.greetings),
    url(r'^home/search$',views.search),
]