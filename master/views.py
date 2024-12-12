from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.models import User,Group
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import cache_control
from user_module.decorators import allowed_users
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist  
from django.http import  HttpResponseRedirect, HttpResponse
from django.contrib import messages
from django.urls import reverse
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.db import IntegrityError
import pandas as pd
from django.http import HttpResponseNotFound

from .forms import *
from tickets.models import *
from tickets.forms import *


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def master_dashboard(request):
    # Count auto tickets
    auto_tickets_count = Item.objects.filter(approval__approval='auto').count()

    # Count manual tickets
    manual_tickets = Item.objects.filter(approval__approval='manual')
    manual_tickets_count = Item.objects.filter(approval__approval='manual').count()

    # Count overall tickets
    overall_tickets_count = Item.objects.count()

    # Count engineers
    engineers_count = User.objects.filter(groups__name='Engineer').count()

    # Create a context dictionary with the counts
    context = {
        'auto_tickets_count': auto_tickets_count,
        'manual_tickets_count': manual_tickets_count,
        'overall_tickets_count': overall_tickets_count,
        'engineers_count': engineers_count,
        'manual_tickets':manual_tickets,
    }

    return render(request, 'Admin/admin_dashboard.html', context)

 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def category_subcategory_view(request):
    # Order categories by id in descending order to show the newest first
    categories = Category.objects.all().order_by('-id')
    subcategories = Subcategory.objects.all().order_by('-id')
    approvalmatrix = ApprovalMatrix.objects.all()

    paginator = Paginator(categories, 8)  # Display 8 categories per page
    page = request.GET.get('page')  # Get the current page number from the request
    categories = paginator.get_page(page)

    if request.method == 'POST':
        category_form = CategoryForm(request.POST)
        if category_form.is_valid():
            category_form.save()
            return redirect('create_page')

    else:
        category_form = CategoryForm()

    

    return render(request, 'Admin/createpage.html', {
        'categories': categories,
        'category_form': category_form,  # Use different variable names for each form
        'subcategories': subcategories,
        'approvalmatrix':approvalmatrix,
        
    })




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def create_subcategory(request):

    if request.method == 'POST':
        subcategory_form = SubcategoryForm(request.POST)
        if subcategory_form.is_valid():
            subcategory_form.save()
            # Redirect to a success page or perform other actions
            return redirect('create_page')  # Replace 'create_page' with the appropriate URL name
    else:
        subcategory_form = SubcategoryForm()

    # Render the template with the form in both cases
    return render(request, 'Admin/createpage.html', {'subcategory_form': subcategory_form,})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def create_approval_matrix(request):
    if request.method == 'POST':
        form = ApprovalMatrixForm(request.POST)
        if form.is_valid():
            try:
                form.save()  # Save the form data to the database
                # You can add a success message or redirect to another page here
                return redirect('create_page')  # Replace 'create_page' with the name of your success view
            except IntegrityError:
                form.add_error(None, 'The combination of functionality, technicality, and approval already exists.')
        else:
            # Print form errors to the console if form is not valid
            print("Form errors:", form.errors.as_json())
    else:
        form = ApprovalMatrixForm()

    return render(request, 'Admin/createpage.html', {'form': form})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def admin_all_tickets(request):
    engineers = User.objects.filter(groups__name='Engineer')
    all_items = Item.objects.all()
    total_item_count = Item.objects.all().count()
    all_tickets = Item.objects.all()

    assigned_tickets = Item.objects.filter(Q(status='open') | Q(status='assigned') | Q(status='pending') | Q(status='inprogress') | Q(status='Resolved')| Q(status='closed')|Q(status='seek-clarification'))
    search_query = request.GET.get('search_query', '')

    # Initialize the error_message variable to None
    error_message = None 

    # If a search query is provided, filter the tickets by ticket number or status
    if search_query:
        all_tickets = all_tickets.filter(
           Q(id__icontains=search_query) |  # Search by ticket number
            Q(status__iexact=search_query) |  # Search by status (case-insensitive)
            Q(category__name__icontains=search_query) |  # Search by category name (case-insensitive)
            Q(subcategory__name__icontains=search_query)
            
        ) 

        # Check if the search result is empty
        if not all_tickets:
            error_message = "No matching tickets found."
    # Define a custom sorting function to order the statuses
    def custom_sort(ticket):
        status_order = {
            'open': 0,
            'assigned': 1,
            'inprogress': 2,
            'pending': 3,
            'Resolved': 4,
            'closed': 5,
        }
        return status_order.get(ticket.status, 5)  # Default to a high number for other statuses

    # Sort the tickets based on the custom sorting function
    assigned_tickets = sorted(assigned_tickets, key=custom_sort)


    success_param = request.GET.get('success', False)
    success_message = success_param == 'True'
    latest_ticket = None  # Initialize latest_ticket to None
    topic = "Ticket Created Successfully"  # Set the topic here

    if success_message:
        latest_ticket = Item.objects.latest('id')  # Fetch the latest created ticket
        text = f'TicketAWO1200000{latest_ticket.id}' if latest_ticket else ""
    else:
        text = ""

  
    # Fetch attachments for each ticket
    ticket_attachments = {}
    for ticket in all_tickets:
        attachments = FileUpload.objects.filter(item=ticket.id)
        ticket_attachments[ticket.id] = attachments
    # Debugging: Print ticket IDs and the number of attachments
    for ticket_id, attachments in ticket_attachments.items():
        print(f"Ticket ID: {ticket_id}, Number of Attachments: {attachments.count()}")

    context = {
        'all_items': all_items,  # Update the variable name
        'total_item_count': total_item_count,  # Update the variable name
        'engineers': engineers,
        'assigned_tickets': assigned_tickets,
        'all_tickets': all_tickets,
        'success_message': {
            'topic': topic,
            'text': text,
        },
        'latest_ticket': latest_ticket,
        'ticket_attachments': ticket_attachments,  # Pass ticket attachments to the template
        'error_message':error_message

    }
    return render(request, 'Admin/admin_alltickets.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def admin_create_ticket(request):
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    approval_matrix = ApprovalMatrix.objects.all()  # Fetch all approval matrix entries
    
    context = {
        'categories': categories,
        'subcategories': subcategories,
    }

    if request.method == 'POST':
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        description = request.POST.get('description')
        files = request.FILES.getlist('fileUpload[]')  # Get a list of uploaded files

        # Check if the user selected 'Please select' for category or subcategory
        if category_id == 'Please select':
            messages.error(request, 'Please select a valid category.')
        elif subcategory_id == 'Please select':
            messages.error(request, 'Please select a valid subcategory.')
        elif not description:
            messages.error(request, 'Description is required.')
        else:
            try:
                category = Category.objects.get(pk=int(category_id))
                subcategory = Subcategory.objects.get(pk=int(subcategory_id))
                
                # Fetch the functionality and technically values from the selected subcategory
                functionality = subcategory.functionality
                technically = subcategory.technically

            except (ValueError, Category.DoesNotExist, Subcategory.DoesNotExist):
                messages.error(request, 'Invalid category or subcategory selected.')
            else:
                total_file_size = sum(file.size for file in files)
                # Check if the total file size exceeds 30KB (30 * 1024 bytes)
                if total_file_size > 30 * 1024:
                    messages.error(request, 'Total file size exceeds 30KB. Please reduce the file sizes.')
                else:
                    # Find the matching ApprovalMatrix entry based on functionality and technically
                    try:
                        approval_entry = approval_matrix.get(functionally=functionality, technically=technically)
                    except ApprovalMatrix.DoesNotExist:
                        messages.error(request, 'No matching approval matrix entry found.')
                    else:
                        item = Item(category=category, subcategory=subcategory, description=description)
                        item.functionality = functionality  # Set the functionality value
                        item.technically = technically  # Set the technically value
                        item.approval = approval_entry  # Set the approval value from the ApprovalMatrix
                        item.created_by = request.user

                        if request.user.stores.exists():
                            item.store_code = request.user.stores.first().store_code
                        else:
                            item.store_code = None

                        item.save()

                        for file in files:
                            file_size = file.size
                            file_upload = FileUpload(
                                item=item,
                                file=file,
                                file_size=file_size,
                                # ... (other fields if needed)
                            )
                            file_upload.save()

                        return redirect(reverse('admin_all_tickets')+ '?success=True')

    return render(request, 'Admin/admin_create_ticket.html', context)





@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
def delete_catagory(request, id):
  categories = Category.objects.get(id=id)
  categories.delete()
  return HttpResponseRedirect(reverse('create_page')) 

def delete_sub(request, id):
    subcategory = get_object_or_404(Subcategory, id=id)
    subcategory.delete()
    messages.success(request, "Subcategory deleted successfully.")
    return redirect('create_page')  # Ensure 'create_page' is defined in your URLs

from django.http import JsonResponse

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
def update_category(request, category_id):
    if request.method == "POST":
        value = request.POST.get("value")
        field = request.POST.get("field")
        category = Category.objects.get(pk=category_id)

        if field == "name":
            category.name = value
        elif field == "technically":
            category.technically = value
        elif field == "functionality":
            category.functionality = value

        category.save()

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})


def get_subcategory_data(request, subcategory_id):
    try:
        subcategory = Subcategory.objects.get(pk=subcategory_id)
        subcategories = Subcategory.objects.filter(category=subcategory.category).values("id", "name","functionality","technically")

        data = list(subcategories)
        return JsonResponse({"success": True, "data": data})
    except Subcategory.DoesNotExist:
        return JsonResponse({"success": False})


from django.shortcuts import get_object_or_404

def edit_subcategory(request):
    if request.method == 'POST':
        subcategory_id = request.POST['subcategory_id']
        try:
            subcategory = Subcategory.objects.get(pk=subcategory_id)
            
            # Fetch the Category instance based on the selected category's ID
            category_id = request.POST['category']
            category = get_object_or_404(Category, pk=category_id)
            
            subcategory.category = category
            subcategory.name = request.POST['name']
            subcategory.functionality = request.POST['functionality']
            subcategory.technically = request.POST['technically']
            subcategory.save()
            return redirect('create_page')  # Replace 'category_list' with your actual URL pattern name
        except Subcategory.DoesNotExist:
            # Handle the case where the Subcategory doesn't exist
            pass
    # Handle other cases here or return an error response


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def admin_engineers_count(request):
    engineers = User.objects.filter(groups__name='Engineer')

    # Calculate the assigned tickets count for each engineer
    engineer_data = []
    for engineer in engineers:
        assigned_tickets_count = Item.objects.filter(assignee=engineer).count()
        engineer_data.append({'engineer': engineer, 'assigned_tickets_count': assigned_tickets_count})

    context = {
        'engineers_data': engineer_data,  # Pass the list of engineer data to the template
    }

    return render(request, 'Admin/engineers_ticket.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def admin_reports(request):
    # Order the queryset by the 'created' field in descending order
    all_tickets = Item.objects.all().order_by('id')

    # Configure the number of items per page
    items_per_page = 10
    paginator = Paginator(all_tickets, items_per_page)
    
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    
    # Calculate the range of items being displayed
    start_index = (page.number - 1) * items_per_page + 1
    end_index = min(start_index + items_per_page - 1, paginator.count)
    context = {
        'all_tickets': page,  # Use the paginated queryset
        'page': page,
        'start_index': start_index,
        'end_index': end_index,
        'total_items': paginator.count,
    }
    
    return render(request, 'Admin/admin_tables.html', context)

def admin_export_to_pdf(request):

    # Get the 'export' parameter from the request

    export_type = request.GET.get('export')

 

    if export_type == 'pdf':

        # Export to PDF

        template_path = 'CFAPerson/pdf_template.html'

        all_tickets = Item.objects.all().order_by('-created')

        context = {'all_tickets': all_tickets}

        response = HttpResponse(content_type='application/pdf')

        response['Content-Disposition'] = 'filename="ticket_data.pdf"'

        template = get_template(template_path)

        html = template.render(context)

        pisa_status = pisa.CreatePDF(html, dest=response)

 

        if pisa_status.err:

            return HttpResponse('We had some errors <pre>' + html + '</pre>')

 

        return response

 

    else:

        # Handle other cases or errors

        return HttpResponse('Invalid export type')

 
def admin_export_to_excel(request):
    # Retrieve the data you want to export to Excel
    all_tickets = Item.objects.all().order_by('-created')

    # Prepare the data in a DataFrame
    data = {
        'Ticket Number': [f"{ticket.store_code}-{ticket.id}" for ticket in all_tickets],
        'Category': [ticket.category for ticket in all_tickets],
        'Subcategory': [ticket.subcategory for ticket in all_tickets],
        'Date': [ticket.created.strftime('%Y-%m-%d %H:%M:%S') for ticket in all_tickets],
        'Status': [ticket.status for ticket in all_tickets],
    }
    df = pd.DataFrame(data)

    # Create an Excel response
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="ticket_data.xlsx"'

    # Write the DataFrame to the response
    df.to_excel(response, index=False)

    return response 
    
def admin_delete_ticket(request, ticket_id):
    try:
        ticket = Item.objects.get(pk=ticket_id)
        ticket.delete()
    except Item.DoesNotExist:
        pass  # Handle the case where the ticket does not exist

    return redirect('admin_reports')

def admin_get_ticket_details(request, ticket_id):
    try:
        ticket = Item.objects.get(id=ticket_id)
        ticket_details = {

            'category': ticket.category,

            'assignee': ticket.assignee,

            'subcategory': ticket.subcategory,

            'created': ticket.created.strftime('%Y-%m-%d %H:%M:%S'),

            'status': ticket.status,

            'raised_code':ticket.raised_code,

            'id': ticket.id,  # Include the ticket ID in the response'
            # Add more details as needed

        }

        return JsonResponse(ticket_details)

    except Item.DoesNotExist:

        return JsonResponse({'error': 'Ticket not found'}, status=404)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def Non_Ad_user_creation(request, user_id=None):
    if request.method == 'POST':
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return HttpResponseNotFound("User not found.") 
            form = CustomUserChangeForm(request.POST, instance=user)
        else:
            form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            return redirect('user_list')
        else:
            return render(request, 'Admin/user_create.html', {'form': form, 'user_id': user_id})  # Remove 'user' from the context 
    else:
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return HttpResponseNotFound("User not found.") 
            form = CustomUserChangeForm(instance=user)
        else:
            form = CustomUserCreationForm()
        return render(request, 'Admin/user_create.html', {'form': form, 'user_id': user_id})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def Ad_user_creation(request, user_id=None):
    if request.method == 'POST':
        if user_id: 
            user = User.objects.get(id=user_id)
            form = AdUserCreationForm(request.POST, instance=user)
        else:
            form = AdUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() 
            return redirect('user_list') 
        else:
            user = None 
    else:
        if user_id:
            user = User.objects.get(id=user_id)
            form = AdUserCreationForm(instance=user)
        else:
            form = AdUserCreationForm()
            user = None 

    return render(request, 'Admin/ad_user_create.html', {'form': form, 'user_id': user_id, 'user': user})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def user_list(request):
    users = User.objects.all().select_related('usertype') 
    storecode=Store.objects.all()
    context = {
        'users': users,  # Pass the user data to the template
        'storecode':storecode,
    }
    return render(request, 'Admin/user_list.html',context)




@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def add_storecode(request):
    if request.method == 'POST':
        form = AddStoreCodeForm(request.POST)

        if form.is_valid():
            selected_username = form.cleaned_data['username']
            store_code = form.cleaned_data['store_code']

            # Find the user by the selected username
            selected_user = User.objects.get(username=selected_username)

            # Check if the user is in the "CFAPerson" group
            store_person_group = Group.objects.get(name='CFAPerson')

            if selected_user.groups.filter(pk=store_person_group.pk).exists():
                # CFAPerson can have only one store
                existing_store = Store.objects.filter(user=selected_user).first()
                if existing_store:
                    form.add_error(None, "CFAPersons can have only one store.")
                else:
                    # Create a new Store object and save it
                    store = Store(store_code=store_code, user=selected_user)
                    store.save()

                    return redirect('storecode_list')  # Redirect to a success page
            else:
                form.add_error(None, "The selected user is not in the 'CFAPerson' group.")
        else:
            print(form.errors)  # Print the validation errors to the console
    else:
        form = AddStoreCodeForm()

    # Fetch a list of usernames
    usernames = User.objects.filter(groups__name='CFAPerson').values_list('username', flat=True)

    return render(request, 'Admin/add_storecode.html', {'form': form, 'usernames': usernames})

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Admin'])
def storecode_list(request):
    stores=Store.objects.all()
    context={
        'stores':stores,
    }
    return render(request,'Admin/storecode_list.html',context)



def user_delete(request, user_id):
    try:
        # Retrieve the user using the provided user_id
        user = get_object_or_404(User, id=user_id)
        
        # Deactivate the user by setting is_active to False
        user.is_active = False
        user.save()  # Save the change to the database
        
    except User.DoesNotExist:
        pass  # Handle the case where the user does not exist
    
    # Redirect to the user list page or any other page as required
    return redirect('user_list')


@login_required
@allowed_users(allowed_roles=['Admin'])
def edit_approval_matrix(request, approval_id):
    if request.method == 'POST':
        # Get the ApprovalMatrix instance to edit
        approval_matrix = ApprovalMatrix.objects.get(pk=approval_id)
        
        form = ApprovalMatrixForm(request.POST, instance=approval_matrix)
        if form.is_valid():
            # Print the values of the three fields for debugging
            print("Functionally:", form.cleaned_data['functionally'])
            print("Technically:", form.cleaned_data['technically'])
            print("Approval:", form.cleaned_data['approval'])
            
            # Update the instance with the edited data
            approval_matrix.functionally = form.cleaned_data['functionally']
            approval_matrix.technically = form.cleaned_data['technically']
            approval_matrix.approval = form.cleaned_data['approval']
            
            # Save the edited instance
            approval_matrix.save()

            # You can add a success message or redirect to another page here
            return redirect('create_page')  # Replace 'success_view_name' with the name of your success view
    else:
        form = ApprovalMatrixForm()

    return render(request, 'Admin/createpage.html', {'form': form})



def delete_approval_matrix(request, approval_id):
    approval = get_object_or_404(ApprovalMatrix, id=approval_id)
    approval.delete()
    return redirect('create_page')