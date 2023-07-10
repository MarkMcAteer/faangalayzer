from django.urls import path
from . import views

app_name = 'converter'

urlpatterns = [
    path('', views.converter, name='converter'),
    path('investor-details/', views.investor_details, name='investor-details'),
    path('deposit-value/', views.deposit_value, name='deposit-value'),
    path('withdraw-value/', views.withdraw_value, name='withdraw-value'),
    path('buy-stock-view/', views.buy_stock_view, name='buy-stock-view'),
    path('sell-stock-view/', views.sell_stock_view, name='sell-stock-view'),
]
