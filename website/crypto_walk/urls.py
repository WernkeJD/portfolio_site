from django.urls import path
from . import views

urlpatterns = [
    path('pick_crypto/', views.pick_crypto, name='pick_crypto'),
    path("update_clicks/", views.update_clicks, name="update_clicks"),
    path("update_selections/", views.update_selections, name="update_selections"),
    path("generate_portfolio_value/", views.generate_portfolio_value, name="update_portfolio_value"),
    path("portfolio_comparison/", views.portfolio_comparison, name="portfolio_comparison")
]