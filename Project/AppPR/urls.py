from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index, name='index'),
    re_path(r'^requests/',views.requests, name='requests'),
    re_path(r'^members/',views.members, name='members'),
    re_path(r'^inventory/',views.inventory, name='inventory'),
    re_path(r'^newReq/',views.newReq, name='newReq'),
    re_path(r'^recItem/',views.recItem, name='recItem'),
    re_path(r'^pendApr/',views.pendApr, name='pendApr'),
    re_path(r'^pendDel/',views.pendDel, name='pendDel'),
    re_path(r'^aprReq/',views.aprReq, name='aprReq'),
    re_path(r'^addMember/',views.addMember, name='addMember'),
    re_path(r'^delReq/',views.delReq, name='delReq'),
    re_path(r'^login/',views.login, name='login'),
    re_path(r'^staffportal/',views.login, name='stafflogin'),
    re_path(r'^studentportal/',views.login, name='studentlogin'),
    re_path(r'^closeportal/',views.closeportal, name='closeportal'),
    re_path(r'^expChart/$',views.expChart, name='expChart'),
]