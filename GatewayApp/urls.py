from django.conf.urls import url
from GatewayApp import views


urlpatterns = [
    url(r'^gateway/add_place/$', views.AddPlaceView.as_view()),
    url(r'^gateway/add_rating/$', views.AddRatingView.as_view()),
    url(r'^gateway/add_acceptance/$', views.AddAcceptView.as_view()),
    url(r'^gateway/delete_acceptance/(?P<acceptance_id>\d+)/$', views.DeleteAcceptanceView.as_view()),
    url(r'^gateway/buy_pin/$', views.BuyPinView.as_view()),
]
