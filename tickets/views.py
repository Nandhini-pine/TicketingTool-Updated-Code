from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from . models import *
from django.contrib import messages
from django.urls import reverse
from user_module.decorators import allowed_users
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.models import User  # Import the User model
from django.forms.models import model_to_dict
from django.db.models.functions import Coalesce
from django.db.models import Sum
from django.db.models import F
from django.db.models import DecimalField
from decimal import Decimal

from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator

from django.template.loader import get_template
from xhtml2pdf import pisa
import pandas as pd
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone

from django.core.exceptions import ValidationError


from django.core.paginator import Paginator
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['CFAPerson'])
def index(request):
    authenticated_user = request.user  # Get the authenticated user
    numbers = list(range(1, 101))

    all_tickets = Item.objects.filter(created_by=authenticated_user)  # Filter tickets by the authenticated user
    tickets = all_tickets.count()
    
    open_count = all_tickets.filter(status='open').count()
    assigned_count = all_tickets.filter(status='assigned').count()
    pending_count = all_tickets.filter(status='pending').count()
    closed_count = all_tickets.filter(status='closed').count()
    inprogress_count = all_tickets.filter(status='inprogress').count()
    resolved_count = all_tickets.filter(status='Resolved').count()

    # Initialize the variables before the if-else block
    assigned_percentage = 0
    pending_percentage = 0
    closed_percentage = 0
    ticket_percentage = 0
    inprogress_percentage = 0
    open_percentage = 0
    resolved_percentage=0

    if tickets > 0:
        assigned_percentage = (assigned_count / tickets) * 100
        pending_percentage = (pending_count / tickets) * 100
        closed_percentage = (closed_count / tickets) * 100
        ticket_percentage =  100
        inprogress_percentage = (inprogress_count / tickets) * 100
        open_percentage = (open_count / tickets) * 100
        resolved_percentage = (resolved_count / tickets) * 100

    current_datetime = datetime.now(dt_timezone.utc)  # Use datetime.timezone.utc

    current_day = current_datetime.day
    current_month = current_datetime.month
    current_year = current_datetime.year
    
    context = {
        'current_day': current_day,
        'current_month': current_month,
        'current_year': current_year,
        'ticket_percentage': ticket_percentage,
        'inprogress_count': inprogress_count,
        'resolved_count':resolved_count,
        'all_tickets': all_tickets,
        'tickets': tickets,
        'closed_percentage': closed_percentage,
        'inprogress_percentage': inprogress_percentage,
        'resolved_percentage':resolved_percentage,
        'pending_count': pending_count,
        'closed_count': closed_count,
        'open_count': open_count,
        'assigned_count': assigned_count,
        'assigned_percentage': assigned_percentage,
        'pending_percentage': pending_percentage,
        'open_percentage': open_percentage,
        'numbers': numbers,
    }
    return render(request, 'CFAPerson/base.html', context)

from django.shortcuts import render, redirect, reverse
from .models import Category, Subcategory, ApprovalMatrix, Item, User
from django.utils import timezone
import re

from django.db import transaction

MAX_FILE_SIZE_MB = 2  # Maximum file size in megabytes

@login_required
@allowed_users(allowed_roles=['CFAPerson'])
def create_ticket(request):
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    approval_matrix = ApprovalMatrix.objects.all()

    context = {
        'categories': categories,
        'subcategories': subcategories,
    }

    if request.method == 'POST':
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')
        short_description = request.POST.get('short_description')
        detailed_description = request.POST.get('detailed_description')
        files = request.FILES.getlist('fileUpload[]')
        errors = []

        if category_id == 'Please select':
            errors.append('Please select a valid category.')
        elif subcategory_id == 'Please select':
            errors.append('Please select a valid subcategory.')
        elif not short_description:
            errors.append('Short description is required.')
        elif not detailed_description:
            errors.append('Detailed description is required.')
        elif not re.match(r'^[a-zA-Z0-9\s.,\'"/-]*$', short_description):
            errors.append('Short description contains invalid characters. Only letters, numbers, spaces, ., \', ", /, and - are allowed.')
        elif not re.match(r'^[a-zA-Z0-9\s.,\'"/-]*$', detailed_description):
            errors.append('Detailed description contains invalid characters. Only letters, numbers, spaces, ., \', ", /, and - are allowed.')
        else:
            # Check file sizes
            for file in files:
                if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:  # Convert MB to bytes
                    errors.append(f'File "{file.name}" exceeds the maximum size of {MAX_FILE_SIZE_MB} MB.')

            if not errors:
                try:
                    category = Category.objects.get(pk=int(category_id))
                    subcategory = Subcategory.objects.get(pk=int(subcategory_id))
                    functionality = subcategory.functionality
                    technically = subcategory.technically

                    # Retrieve or create ApprovalMatrix entry
                    with transaction.atomic():
                        approval_entries = approval_matrix.filter(functionally=functionality, technically=technically)

                        if approval_entries.exists():
                            approval_entry = approval_entries.first()
                        else:
                            # If no matching entry is found, create a new one
                            functionality = 'other'
                            technically = 'other'
                            approval_entry = ApprovalMatrix.objects.create(
                                functionally=functionality,
                                technically=technically,
                                approval='manual'
                            )

                    # Create Item instance and save it
                    item = Item(
                        category=category,
                        subcategory=subcategory,
                        short_description=short_description,
                        detailed_description=detailed_description,                        
                        functionality=functionality,
                        technically=technically,
                        approval=approval_entry,
                        created_by=request.user,
                        store_code=request.user.stores.first().store_code if request.user.is_authenticated and request.user.stores.exists() else None,
                    )
                    item.full_clean()  # Validate model fields
                    item.save(user=request.user)

                    # Create initial status history
                    StatusHistory.objects.create(
                        item=item,
                        status=item.status,  # Assuming the initial status is set before saving
                        changed_by=request.user
                    )
                    # Save FileUpload instances
                    for file in files:
                        file_upload = FileUpload(
                            item=item,
                            file=file,
                            file_size=file.size,
                            # Add other fields if needed
                        )
                        file_upload.save()

                    return redirect(reverse('CFAPerson_alltickets') + '?success=True')

                except (ValueError, Category.DoesNotExist, Subcategory.DoesNotExist) as e:
                    errors.append('Invalid category or subcategory selected.')
                except ValidationError as e:
                    errors.append(f'Validation error: {e}')
                except Exception as e:
                    errors.append(f'Error occurred while creating ticket: {e}')

        context['errors'] = errors

    return render(request, 'CFAPerson/create-ticket.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['CFAPerson'])
def all_ticket(request):
    authenticated_user = request.user  # Get the authenticated user
    categories = Category.objects.all() 
    subcategories = Subcategory.objects.all()

    all_tickets = Item.objects.filter(created_by=authenticated_user)  # Filter tickets by the authenticated user
    
    total_ticket_count = all_tickets.count()

    search_query = request.GET.get('search_query', '')
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
        if not all_tickets.exists():
            error_message = "No matching tickets found."
          

    # Create a dictionary to hold clarification histories for each ticket
    clarification_histories_dict = {}
    
    for ticket in all_tickets:
        # Use 'item' or 'item_id' instead of 'ticket'
        clarification_histories_dict[ticket.id] = SeekClarificationHistory.objects.filter(item=ticket,status_check='unclarified')
        
    # Get attachments if needed
    seek_attachments = SeekAttachment.objects.all() 

    # Rename the dictionary to seek_attachments
    seek_attachment = {}
    clarification_histories = {}
    
    for ticket in all_tickets:
        # Fetch attachments for each ticket
        attachments = SeekAttachment.objects.filter(item=ticket.id)
        seek_attachment[ticket.id] = attachments
        
        # Fetch clarification history for each ticket
        clarifications = SeekClarificationHistory.objects.filter(item=ticket)  # Use 'item' instead of 'ticket'
        clarification_histories[ticket.id] = clarifications

    # Check if success parameter is in the URL

    success_param = request.GET.get('success', False)
    success_message = success_param == 'True'
    latest_ticket = None  # Initialize latest_ticket to None
    topic = "Ticket Created Successfully"  # Set the topic here

    if success_message:
        latest_ticket = Item.objects.latest('id')  # Fetch the latest created ticket
        text = f'TICKET{latest_ticket.store_code}232400000{latest_ticket.id}' if latest_ticket else ""
    else:
        text = ""

        # Get the search query from the request's GET parameters

    # Initialize the error_message variable to None

     # Status order mapping for custom sorting
    status_order = {
        'seek-clarification': 1,
        'Resolved': 2,
        'open': 3,
        'reopen': 4,
        'inprogress': 5,
        'pending': 6,
        'closed':7,
        'assigned':8
    }

    # Apply sorting logic
    all_tickets = sorted(
        all_tickets,
        key=lambda ticket: status_order.get(ticket.status, 7)  # Default to 7 if status not found
    )

      
    return render(request, 'CFAPerson/CFAPerson_alltickets.html', {
        'all_tickets': all_tickets,
        'categories':categories,
        'subcategories':subcategories,
        'total_ticket_count': total_ticket_count,
        
        'success_message': {
            'topic': topic,
            'text': text,

        },
        'latest_ticket': latest_ticket,
        'error_message':error_message,
        'clarification_histories_dict': clarification_histories_dict,  # Pass the dictionary to the template
        'seek_attachments': seek_attachments,

        'seek_attachment': seek_attachment,  # Pass seek attachments to the template
        'clarification_histories': clarification_histories,  # Pass clarification histories to the template
    })



def test(request):
    return render(request,'widget-basic.html')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['CFAPerson'])
def CFAPerson_Tableview(request):
    # Get the authenticated user
    authenticated_user = request.user

    # Filter tickets by the authenticated user
    all_tickets = Item.objects.filter(created_by=authenticated_user).order_by('id')


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
    
    return render(request, 'CFAPerson/sptable_view.html', context)


def export_to_pdf(request):
    # Get the 'export' parameter from the request
    authenticated_user = request.user

    export_type = request.GET.get('export')

    if export_type == 'pdf':
        # Export to PDF
        template_path = 'CFAPerson/pdf_template.html'
        all_tickets = Item.objects.filter(created_by=authenticated_user).order_by('-created')
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


def export_to_excel(request):
    # Retrieve the data you want to export to Excel
    authenticated_user = request.user
    all_tickets = Item.objects.filter(created_by=authenticated_user).order_by('-created')
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
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    response['Content-Disposition'] = 'attachment; filename="ticket_data.xlsx"'

    # Write the DataFrame to the response
    df.to_excel(response, index=False)

    return response
    

def delete(request, id):
    all_tickets = Item.objects.get(id=id)
    all_tickets.delete()
    messages.success(request, 'Ticket deleted successfully!')
    return HttpResponseRedirect(reverse('CFAPerson_Tables'))


def get_ticket_details(request, ticket_id):
    try:
        ticket = Item.objects.get(id=ticket_id)
        ticket_details = {
            'category': model_to_dict(ticket.category),  # Convert Category to dictionary
            'subcategory': model_to_dict(ticket.subcategory),  # Convert Subcategory to dictionary
            'created': ticket.created.strftime('%Y-%m-%d %H:%M:%S'),
            'status': ticket.status,
            'raised_code': ticket.store_code,
            'id': ticket.id,  # Include the ticket ID in the response
            # Add more details as needed
        }

        return JsonResponse(ticket_details)

    except Item.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)

MAX_FILE_SIZE_MB = 2  # Maximum file size in megabytes
MAX_TOTAL_FILE_SIZE_MB = 2  # Maximum total file size in megabytes

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@allowed_users(allowed_roles=['CFAPerson'])
def edit_ticket(request, ticket_id):
    ticket = get_object_or_404(Item, id=ticket_id)

    if request.method == 'POST':
        # Retrieve the fields from the form
        category_id = request.POST.get('category')
        subcategory_id = request.POST.get('subcategory')

        # Retrieve the Category and Subcategory instances based on their IDs
        category = get_object_or_404(Category, id=category_id)
        subcategory = get_object_or_404(Subcategory, id=subcategory_id)

        # Assign the retrieved instances to the ticket's category and subcategory fields
        ticket.category = category
        ticket.subcategory = subcategory

        # Update other fields as needed
        ticket.short_description = request.POST.get('short_description')
        ticket.detailed_description = request.POST.get('detailed_description')

        # Handle file uploads
        uploaded_files = request.FILES.getlist('fileUpload[]')

        # Calculate the total file size of newly uploaded files
        total_new_file_size_bytes = sum(file.size for file in uploaded_files)

        # Fetch the total_file_size_kb value from the TicketFileTotalSize model
        ticket_total_size, created = TicketFileTotalSize.objects.get_or_create(ticket=ticket)
        existing_file_size_bytes = ticket.uploads.aggregate(total_size_bytes=Sum('file_size'))['total_size_bytes'] or 0

        # Calculate the total file size including both newly uploaded and existing files
        total_file_size_bytes = total_new_file_size_bytes + existing_file_size_bytes

        if total_file_size_bytes > MAX_TOTAL_FILE_SIZE_MB * 1024 * 1024:
            messages.error(request, f'Total file size exceeds {MAX_TOTAL_FILE_SIZE_MB} MB. Please reduce the file sizes or delete previous files.')
            return redirect('/CFAPersontickets/')  # Redirect to the 'CFAPerson_alltickets' page

        for uploaded_file in uploaded_files:
            if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:  # Check if the file size exceeds 2 MB
                messages.error(request, f'File "{uploaded_file.name}" exceeds the maximum size of {MAX_FILE_SIZE_MB} MB.')
                return redirect('/CFAPersontickets/')  # Redirect to the 'CFAPerson_alltickets' page

            try:
                # Create a new FileUpload instance and associate it with the ticket
                file_upload = FileUpload(item=ticket, file=uploaded_file, file_size=uploaded_file.size)
                file_upload.save()
            except ValidationError:
                # Handle validation error if needed
                pass

        # Update the total file size for the ticket in the TicketFileTotalSize model
        ticket_total_size.total_file_size_kb = total_file_size_bytes / 1024
        ticket_total_size.save()

        # Save the ticket object
        ticket.save()
        messages.success(request, 'Ticket updated successfully.')

        return redirect('/CFAPersontickets/')

    # Handle GET request or other cases
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()

    return render(request, 'CFAPerson/CFAPerson_alltickets.html', {
        'ticket': ticket, 
        'categories': categories,
        'subcategories': subcategories,
    })

def delete_attachment(request, attachment_id):
    try:
        attachment = FileUpload.objects.get(pk=attachment_id)
        attachment.file.delete()  # Delete the actual file from storage
        attachment.delete()  # Delete the attachment object from the database
        return JsonResponse({'success': True})
    except FileUpload.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Attachment not found'})


def get_ticket_history(request, ticket_id):
    try:
        ticket = get_object_or_404(Item, id=ticket_id)
        ticket_details = {
            'category': ticket.category,
            'subcategory': ticket.subcategory,
            'created': ticket.created.strftime('%Y-%m-%d %H:%M:%S'),
            'status': ticket.status,
            'raised_code': ticket.raised_code,
            'id': ticket.id,
            'created_by': ticket.created_by.username if ticket.created_by else '',
            'assignee': ticket.assignee.username if ticket.assignee else '',
            # Add more details as needed
        }
        print(f"Ticket Status: {ticket.status}")
        print(f"Ticket Details: {ticket_details}")  # Add this line for debugging

        return JsonResponse(ticket_details)

    except Item.DoesNotExist:
        return JsonResponse({'error': 'Ticket not found'}, status=404)
    except Exception as e:
        print(f"Error: {e}")
        return JsonResponse({'error': 'An error occurred'}, status=500)

         

@login_required
def change_ticket_status(request, ticket_id):
    ticket = get_object_or_404(Item, id=ticket_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        comment = request.POST.get('comment')
        
        if new_status == 'reopen':
            ticket.status = 'reopen'
            ticket.reopen_date = timezone.now()
            ticket.assignee = None  # Clear the assignee
            ticket.assigned_date = None  # Clear the assigned date
            if comment:
                if ticket.reopen_comments:
                    ticket.reopen_comments += f"\n\n{comment}"
                else:
                    ticket.reopen_comments = comment
        elif new_status == 'closed':
            ticket.status = 'closed'
            ticket.closed_date = timezone.now()
            if comment:
                if ticket.closure_comments:
                    ticket.closure_comments += f"\n\n{comment}"
                else:
                    ticket.closure_comments = comment
        
        # Save the ticket with updated status and comments
        ticket.save(user=request.user)
        return redirect('CFAPerson_alltickets')  # Adjust the redirect as needed

    return redirect('CFAPerson_alltickets')  # Adjust the redirect as needed



@login_required
def submit_clarification_view(request, ticket_id):
    # Fetch the item (ticket) based on the ticket_id
    item = get_object_or_404(Item, id=ticket_id)

    if request.method == 'POST':
        clarified_comment = request.POST.get('seek_comment').strip()
        clarified_attachments = request.FILES.getlist('attachment')  # Get uploaded files for clarified images

        if clarified_comment:
            # Update the latest clarification history with the clarified comment
            clarification_history = SeekClarificationHistory.objects.filter(item=item).last()
            if clarification_history:
                clarification_history.clarified_comment = clarified_comment
                clarification_history.status_check = 'clarified'  # Update status_check to 'clarified'

                clarification_history.save()

                # Save each clarified attachment (images)
                for file in clarified_attachments:
                    SeekAttachment.objects.create(
                        item=item,
                        clarified_image=file,  # Storing in clarified_image
                        created_by=request.user,  # Store person clarifying
                        clarification_history=clarification_history
                    )

                # Optionally update the item status to 'clarified'
                item.status='assigned'
                item.save(user=request.user)

                messages.success(request, 'Clarification submitted successfully!')


                # Redirect or render a success message, or back to the item detail page
                return redirect('CFAPerson_alltickets')  # No ticket_id argument if not needed

    # Render the ticket detail template with fetched data
    return render(request, 'CFAPerson/CFAPerson_alltickets.html', {
        'item': item,
    })


def login_new(request):
    return render(request,'Login/login_new.html')