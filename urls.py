"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from dejavu.views import *

urlpatterns = [
    path('admin/', admin.site.urls), # работает
    path('auth', AuthApiView.as_view()), #зареганные через терминал проходят, а через админку - НЕТ
    path('logout', LogOutApiView.as_view()), # NO
    path('photographers', PhotographerAPIView.as_view()),  # работает
    path('quotes', QuotesApiView.as_view()),  # работает
    path('phsearch', PhotographerSearchAPIView.as_view()),  # работает
    path('newph', NewPhotographersApiView.as_view()),  # работает
    path('register/', RegisterView.as_view()),  # работает

    path('profpic/', ProfilePicAPIView.as_view()),
    path('reviews', ReviewCreateAPIView.as_view()), #NO, через админку работает
    path('addportfolio', PhotoCreateAPIView.as_view()), #NO, через админку работает

    path('profile/', ProfileView.as_view()),
    path('profile/update/', UpdateProfileView.as_view()),


]


from django.conf.urls.static import static
from django.conf import settings

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
