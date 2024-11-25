from django.urls import path
from . import views

urlpatterns = [
  path('Engineer|Dashboard', views.engineer_dashboard, name='engineer_dashboard'),
  path('All Tickets|Engineer',views.all_tickets,name="engineer_alltickets"),
  path('update_status/<int:item_id>/', views.update_status, name='update_status'),

#table
   path('Engineer|Tables_view/', views.table_view, name='engineer_tables'),

    path('get-ticket-details/<int:ticket_id>/', views.get_ticket_details, name='get-ticket-details'),
    path('engineer_tables_view/export/', views.engineer_export_to_pdf, name='engineer_export_to_pdf'),
    path('engineer_export_to_excel/', views.engineer_export_to_excel, name='engineer_export_to_excel'),

]