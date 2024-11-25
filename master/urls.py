from django.urls import path
from . import views

urlpatterns = [
    path('Mater | Dashboard', views.master_dashboard,name='admin_dashboard'),

    # Approval matrix View

    path('Create | Categories', views.category_subcategory_view,name='create_page'),
    path('create_subcategory/', views.create_subcategory, name='create_subcategory'),
    path('create_approval_matrix/', views.create_approval_matrix, name='create_approval_matrix'),
    path('update_category/<int:category_id>/', views.update_category, name='update_category'),
    path('edit_subcategory/', views.edit_subcategory, name='edit_subcategory'),
    path('edit_approval_matrix/<int:approval_id>/', views.edit_approval_matrix, name='edit_approval_matrix'),
    path('delete_catagory/<int:id>/', views.delete_catagory, name='delete_catagory'),
    path('delete_sub/<int:id>/', views.delete_sub, name='delete_sub'),
    path('delete_approval_matrix/<int:approval_id>/', views.delete_approval_matrix, name='delete_approval_matrix'),

    #other pages

    path('All tickets|Admin/',views.admin_all_tickets,name="admin_all_tickets"),
    path('Admin|Create Ticket/',views.admin_create_ticket,name="admin_create_ticket"),

    path('get_subcategory_data/<int:subcategory_id>/', views.get_subcategory_data, name='get_subcategory_data'),
    path('admin_engineer_count/',views.admin_engineers_count,name="admin_engineer_count"),

    #tables/Reports

    path('Admin|Reports/', views.admin_reports, name='admin_reports'),
    path('admin_delete/<int:ticket_id>/', views.admin_delete_ticket, name='admin_delete'),
    path('get-ticket-details/<int:ticket_id>/', views.admin_get_ticket_details, name='get-ticket-details'),
    path('admin_tables_view/export/', views.admin_export_to_pdf, name='admin_export_to_pdf'),
    path('admin_export_to_excel/', views.admin_export_to_excel, name='admin_export_to_excel'),
    
    #User creation

    path('usercreate/', views.user_creation, name='user_creation'),
    path('userlist/', views.user_list, name='user_list'),
    path('addstorecode/', views.add_storecode, name='add_storecode'),
    path('storecodelist/', views.storecode_list, name='storecode_list'),

    #delete -user

    path('user/<int:user_id>/delete/', views.user_delete, name='user_delete'),
 

]