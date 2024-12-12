from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from user_module.decorators import allowed_users
from tickets.models import *
from django.contrib.auth.models import User,Group
from django.http import JsonResponse
from django.db.models import Q 
from django.contrib import messages
import json
from django.http import HttpResponse
from django.core.paginator import Paginator

from django.template.loader import get_template
from xhtml2pdf import pisa
import pandas as pd
from datetime import datetime, timezone as dt_timezone

from django.utils import timezone

# Create your views here.

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@allowed_users(allowed_roles=['Manager'])
def Manager_base(request):
    all_tickets = Item.objects.all()
    all_tickets_count = Item.objects.all().count()
    open_tickets = Item.objects.filter(status='open')
    
    closed_tickets = Item.objects.filter(status='closed').count()
    pending_tickets = Item.objects.filter(status='pending').count()
    assigned_tickets = Item.objects.filter(status='assigned').count()
    inprogress_tickets = Item.objects.filter(status='inprogress').count()
    resolved_tickets = Item.objects.filter(status='Resolved').count()
    reopen_tickets = Item.objects.filter(status='reopen').count()

    open_tickets_count = Item.objects.filter(status='open').count()
    engineer_group = Group.objects.get(name='Engineer')  # Get the 'Engineer' group
    engineers = User.objects.filter(groups=engineer_group) # Filter engineers by group

    open_tickets_progress = (open_tickets_count / all_tickets_count) * 100 if all_tickets_count > 0 else 0
    closed_tickets_progress = (closed_tickets / all_tickets_count) * 100 if all_tickets_count > 0 else 0
    pending_tickets_progress = (pending_tickets / all_tickets_count) * 100 if all_tickets_count > 0 else 0
    assigned_tickets_progress = (assigned_tickets / all_tickets_count) * 100 if all_tickets_count > 0 else 0
    inprogress_tickets_progress = (inprogress_tickets / all_tickets_count) * 100 if all_tickets_count > 0 else 0
    resolved_tickets_progress = (resolved_tickets / all_tickets_count) * 100 if all_tickets_count > 0 else 0
    reopen_tickets_progress = (reopen_tickets / all_tickets_count) * 100 if all_tickets_count > 0 else 0
    all_tickets_progress = (all_tickets_count / all_tickets_count) * 100 if all_tickets_count > 0 else 0

    current_datetime = datetime.now(dt_timezone.utc)

    current_day = current_datetime.day
    current_month = current_datetime.month
    current_year = current_datetime.year

    context = {
        'current_day': current_day,
        'current_month': current_month,
        'current_year': current_year,
        'open_tickets_count': open_tickets_count,
        'all_tickets_progress':all_tickets_progress,
        'inprogress_tickets_progress':inprogress_tickets_progress,
        'open_tickets_progress':open_tickets_progress,
        'closed_tickets_progress':closed_tickets_progress,
        'pending_tickets_progress':pending_tickets_progress,
        'assigned_tickets_progress':assigned_tickets_progress,
        'open_tickets':open_tickets,
        'engineers': engineers,
        'closed_tickets':closed_tickets,
        'all_tickets':all_tickets,
        'pending_tickets':pending_tickets,
        'all_tickets_count':all_tickets_count,
        'resolved_tickets_progress':resolved_tickets_progress,
        'reopen_tickets_progress':reopen_tickets_progress,
         # Pass the selected ticket to the template
    }
    return render(request, 'Manager/Manager-base.html', context)



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@allowed_users(allowed_roles=['Manager'])

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@allowed_users(allowed_roles=['Manager'])
def assign_ticket(request, id):
    item = get_object_or_404(Item, id=id)

    if request.method == 'POST':
        assignee_id = request.POST.get('assignee')

        if assignee_id:
            assignee = User.objects.get(pk=assignee_id)
            item.assignee = assignee
            item.status = 'assigned'
            item.assigned_date = timezone.now()
            item.status_changed_by_manager = request.user

            item.save(user=request.user)
            
            # Generate the ticket text
            ticket_text = f'TICKET{item.store_code}232400000{item.id}'
            success_message = json.dumps({'type': 'success', 'ticket_id': item.id, 'text': ticket_text})
            
            messages.success(request, success_message)
        else:
            error_message = json.dumps({'type': 'error', 'text': 'No assignee selected.'})
            messages.error(request, error_message)

    return redirect('manager_alltickets')

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@allowed_users(allowed_roles=['Manager'])
def all_tickets(request):
    engineers = User.objects.filter(groups__name='Engineer')
    engineers_count = engineers.count()  # Count the number of engineers

    all_items = Item.objects.all()
    total_item_count = Item.objects.all().count()
    all_tickets = Item.objects.all()
    success_param = request.GET.get('success', False)
    success_message = success_param == 'True'
    latest_ticket = None  # Initialize latest_ticket to None
    topic = "Ticket Created Successfully"  # Set the topic here

    search_query = request.GET.get('search_query', '')
 
    # Initialize the error_messages variable to None
    error_messages = None  # Changed from error_message (singular) to error_messages (plural)

    if search_query:
        all_tickets = all_tickets.filter(
            Q(id__icontains=search_query) |  # Search by ticket number
            Q(status__iexact=search_query) |  # Search by status (case-insensitive)
            Q(category__name__icontains=search_query) |  # Search by category name (case-insensitive)
            Q(subcategory__name__icontains=search_query)
        )

       

        # Check if the search result is empty
        if not all_tickets:
            error_messages = "No matching tickets found."  # Changed to error_messages (plural)
        else:
            # Reset error_messages when search results are found
            error_messages = None

    statuses = [
        "Open",
        "Assigned",
        "Seek-clarification",
        "Assigned",
        "Inprogress",
        "Pending",
        "Resolved",
        "Closed"
    ]

   
    if success_message:
        latest_ticket = Item.objects.latest('id')  # Fetch the latest created ticket
        text = f'TicketAWO1200000{latest_ticket.id}' if latest_ticket else ""
    else:
        text = ""

      # Get the search query from the request's GET parameters
   

   # Status order mapping for custom sorting
    status_order = {
        'open': 1,
        'reopen': 2,
        'seek-clarification': 3,
        'assigned': 4,
        'inprogress': 5, 
        'pending':6,
        'closed':7,
        'Resolved':8
    }

    

    # Apply sorting logic
    all_tickets = sorted(
        all_tickets,
        key=lambda ticket: status_order.get(ticket.status, 7)  # Default to 7 if status not found
    )

    # Rename the dictionary to seek_attachments
    seek_attachments = {}
    clarification_histories = {}
    status_histories = {}  # Dictionary to store status history for each ticket
    tickets_status_history = {}

    for ticket in all_tickets:
        # Fetch attachments for each ticket
        attachments = SeekAttachment.objects.filter(item=ticket.id)
        seek_attachments[ticket.id] = attachments
        
        # Fetch clarification history for each ticket
        clarifications = SeekClarificationHistory.objects.filter(item=ticket)  # Use 'item' instead of 'ticket'
        clarification_histories[ticket.id] = clarifications

        status_histories = StatusHistory.objects.filter(item=ticket).order_by('changed_at')
        tickets_status_history[ticket.id] = status_histories
        

    engineer_data = []
    for engineer in engineers:
        assigned_tickets_count = Item.objects.filter(assignee=engineer).count()
        engineer_data.append({'engineer': engineer, 'assigned_tickets_count': assigned_tickets_count})



    # If a search query is provided, filter the tickets by ticket number or status
    

    # Fetch attachments for each ticket
    ticket_attachments = {}
    for ticket in all_tickets:
        attachments = FileUpload.objects.filter(item=ticket.id)
        ticket_attachments[ticket.id] = attachments
    
    context = {
        'all_items': all_items,  # Update the variable name
        'engineer_data': engineer_data,  # Pass engineer data to the template

        'total_item_count': total_item_count,  # Update the variable name
        'engineers': engineers,
        'all_tickets': all_tickets,
        'success_message': {
            'topic': topic,
            'text': text,
        },
        'statuses': statuses,
        
        'latest_ticket': latest_ticket,
        'ticket_attachments': ticket_attachments,  # Pass ticket attachments to the template
        'error_messages':error_messages,
        'seek_attachments': seek_attachments,  # Pass seek attachments to the template
        'clarification_histories': clarification_histories,  # Pass clarification histories to the template
        'tickets_status_history': tickets_status_history,
        'engineers_count': engineers_count,  # Pass the engineers count to the template


    }
    return render(request, 'Manager/manager_alltickets.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@allowed_users(allowed_roles=['Manager'])
def manager_tableview(request):
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
    
    return render(request, 'Manager/manager_tables.html', context)

def manager_export_to_pdf(request):
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

def manager_export_to_excel(request):
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
    
def delete_ticket(request, ticket_id):
    try:
        ticket = Item.objects.get(pk=ticket_id)
        ticket.delete()
    except Item.DoesNotExist:
        pass  # Handle the case where the ticket does not exist

    return redirect('manager_tables')

def get_ticket_details(request, ticket_id):
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
@login_required
@allowed_users(allowed_roles=['Manager'])
def engineers_count(request):
    engineers = User.objects.filter(groups__name='Engineer')

    # Calculate the assigned tickets count for each engineer
    engineer_data = []
    for engineer in engineers:
        assigned_tickets_count = Item.objects.filter(assignee=engineer).count()
        engineer_data.append({'engineer': engineer, 'assigned_tickets_count': assigned_tickets_count})

    context = {
        'engineers_data': engineer_data,  # Pass the list of engineer data to the template
    }

    return render(request, 'Manager/engineers_count.html', context)



def get_ticket_datas(request):
    # Fetch the dynamic data from your database or any other source
    all_tickets = Item.objects.all()
    auto_tickets_count = all_tickets.filter(approval__approval='auto').count()
    manual_tickets_count = all_tickets.filter(approval__approval='manual').count()
    data = {
        'auto_tickets_count': auto_tickets_count,
        'manual_tickets_count': manual_tickets_count,
    }
    return JsonResponse(data)











