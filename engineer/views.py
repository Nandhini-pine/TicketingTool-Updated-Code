from django.shortcuts import render,redirect,get_object_or_404
from tickets.models import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.db.models import Q
from django.http import JsonResponse
import json
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator

from django.template.loader import get_template
from xhtml2pdf import pisa
import pandas as pd
from datetime import datetime

from django.utils import timezone


from user_module.decorators import allowed_users

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Engineer'])
def engineer_dashboard(request):
    engineer = request.user  # Get the currently logged-in engineer user
    engineer_tickets = Item.objects.filter(assignee=engineer)
    total_engineer_tickets = engineer_tickets.count()

    open_tickets = Item.objects.filter(status='open', assignee=engineer)
    assigned_tickets = Item.objects.filter(status='assigned', assignee=engineer)
    closed_tickets = Item.objects.filter(status='closed', assignee=engineer)
    resolved_tickets = Item.objects.filter(status='Resolved', assignee=engineer)

    pending_tickets = Item.objects.filter(status='pending', assignee=engineer)
    inprogress_tickets = Item.objects.filter(status='inprogress', assignee=engineer)

    all_tickets = engineer_tickets
    tickets = all_tickets.count()
   
    open_tickets_count = open_tickets.count()
    assigned_tickets_count = assigned_tickets.count()
    closed_tickets_count = closed_tickets.count()
    resolved_tickets_count = resolved_tickets.count()

    pending_tickets_count = pending_tickets.count()
    inprogress_tickets_count = inprogress_tickets.count()

    open_count = all_tickets.filter(status='open').count()
    assigned_count = assigned_tickets.filter(status='assigned').count()
    pending_count = all_tickets.filter(status='pending').count()
    closed_count = all_tickets.filter(status='closed').count()
    resolved_count = all_tickets.filter(status='Resolved').count()

    inprogress_count = all_tickets.filter(status='inprogress').count()
    
    if total_engineer_tickets > 0:
        open_percentage = (open_count / total_engineer_tickets) * 100
        assigned_percentage = (assigned_count / total_engineer_tickets) * 100
        pending_percentage = (pending_tickets_count / total_engineer_tickets) * 100
        closed_percentage = (closed_count / total_engineer_tickets) * 100
        resolved_percentage = (resolved_count / total_engineer_tickets) * 100
        ticket_percentage = (tickets / tickets) * 100
        inprogress_percentage = (inprogress_count / total_engineer_tickets) * 100
        engineer_tickets_percentage = (total_engineer_tickets / total_engineer_tickets) * 100

    else:
        assigned_percentage = 0
        pending_percentage = 0
        closed_percentage = 0
        inprogress_percentage = 0
        open_percentage=0
        open_count=0
        closed_count = 0
        ticket_percentage = 0
        inprogress_count = 0
        assigned_count=0
        pending_count=0
        resolved_percentage=0
        engineer_tickets_percentage=0
    
    context = {
        'assigned_tickets_count': assigned_tickets_count,
        'assigned_tickets': assigned_tickets,
        'assigned_percentage':assigned_percentage,
        'pending_percentage':pending_percentage,
        'closed_percentage':closed_percentage,
        'resolved_percentage':resolved_percentage,

        'ticket_percentage':ticket_percentage,
        'inprogress_percentage':inprogress_percentage,
        'pending_tickets_count':pending_tickets_count,
        'closed_tickets_count':closed_tickets_count,
        'resolved_tickets_count':resolved_tickets_count,

        'inprogress_tickets_count':inprogress_tickets_count,
        'all_tickets':all_tickets,
        'pending_count':pending_count,
        'open_percentage':open_percentage,
        'resolved_percentage':resolved_percentage,

        'total_engineer_tickets': total_engineer_tickets,  # Add the total engineer's tickets to the context
        'engineer_tickets_percentage':engineer_tickets_percentage,

    }
    
    return render(request, 'Engineer/engineer_dashboard.html', context)

@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Engineer'])
def all_tickets(request):
    engineer = request.user  # Get the currently logged-in engineer user
    assigned_tickets = Item.objects.filter( assignee=engineer)
    all_tickets = Item.objects.all()
    search_query = request.GET.get('search_query', '')  
    success_param = request.GET.get('success', False)
    success_message = success_param == 'True'
    latest_ticket = None  
    topic = "Ticket Created Successfully" 
    error_message = None  

    # If a search query is provided, filter the tickets by ticket number or status
    if search_query:
        assigned_tickets = assigned_tickets.filter(
            Q(id__icontains=search_query) |  # Search by ticket number
            Q(status__iexact=search_query) |  # Search by status (case-insensitive)
            Q(category__name__icontains=search_query) |  # Search by category name (case-insensitive)
            Q(subcategory__name__icontains=search_query)
        )

        # Check if the search result is empty
        if not assigned_tickets.exists():
            error_message = "No matching tickets found."

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
    
    # Rename the dictionary to seek_attachments
    seek_attachments = {} 
    clarification_histories = {}
    
    for ticket in assigned_tickets:
        # Fetch attachments for each ticket
        attachments = SeekAttachment.objects.filter(item=ticket.id)
        seek_attachments[ticket.id] = attachments
        
        # Fetch clarification history for each ticket
        clarifications = SeekClarificationHistory.objects.filter(item=ticket)  # Use 'item' instead of 'ticket'
        clarification_histories[ticket.id] = clarifications
    user=request.user
    print("logged_user:",user)
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
    assigned_tickets = sorted(
        assigned_tickets,
        key=lambda ticket: status_order.get(ticket.status, 7)  # Default to 7 if status not found
    )

    context = {
        'assigned_tickets': assigned_tickets,
        'ticket_attachments': ticket_attachments,  # Pass ticket attachments to the template
        'error_message':error_message,
        'success_message': {
            'topic': topic,
            'text': text,
        },
        'latest_ticket': latest_ticket,
        'messages': messages.get_messages(request) , # Include the messages here
        'seek_attachments': seek_attachments,  # Pass seek attachments to the template
        'clarification_histories': clarification_histories,  # Pass clarification histories to the template
    }
    
    return render(request, 'Engineer/engineer_alltickets.html', context)

 
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required
@allowed_users(allowed_roles=['Engineer'])
def update_status(request, item_id):

    if request.method == 'POST':
        engineer = request.user  # Get the currently logged-in engineer user

        try:
            item = Item.objects.get(pk=item_id)
            

            # Check if the engineer is assigned to the ticket
            if item.assignee == engineer:
                new_status = request.POST.get('status')
                print(f"New Status: {new_status}")  # Debugging line

                # Validate the new status against allowed values
                allowed_statuses = ['inprogress', 'pending', 'Resolved','seek-clarification']

                if new_status in allowed_statuses:
                    # Update the item status
                    item.status = new_status

                    # Set the resolved_date field to the current time when status is set to 'Resolved'
                    if new_status == 'Resolved':
                        item.resolved_date = timezone.now()

                    # Save resolver_comments if provided in the form
                    resolver_comments = request.POST.get('resolver_comments', '').strip()
                    if resolver_comments:
                        current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
                        resolver_name = engineer.username
                        formatted_comment = f"Comment by {resolver_name} on {current_time}: {resolver_comments}"
                        # Append the new comment to the existing comments
                        if item.resolver_comments and formatted_comment not in item.resolver_comments:
                            item.resolver_comments += "\n" + formatted_comment
                        else:
                            item.resolver_comments = formatted_comment
                                                
                    # Save seek clarification comments and attachments if the status is 'seek-clarification'
                 
                    if new_status == 'seek-clarification':
                        seek_comments = request.POST.get('seek_comments', '').strip()
                        seek_attachments = request.FILES.getlist('attachments')  # Get uploaded files as a list
                        print(f"Seek Attachments: {seek_attachments}")  # Debugging line

                        if not seek_comments:  # If seek_comments is empty or whitespace
                            messages.error(request, json.dumps({
                                'type': 'error',
                                'text': 'Seek clarification comments are required when changing status to seek-clarification.'
                            }))
                            return redirect('engineer_alltickets')

                        # Log the seek clarification comment with timestamp in SeekClarificationHistory model
                        clarification_history = SeekClarificationHistory.objects.create(
                            item=item,
                            seek_comment=seek_comments,
                            created_by=engineer  # Engineer who is updating the status
                        )

                        # Save each attachment with the created clarification_history
                        for file in seek_attachments:
                            SeekAttachment.objects.create(
                                item=item,
                                clarification_image=file,
                                created_by=engineer,
                                clarification_history=clarification_history  # Associate attachment with clarification history
                            )

                    # Save the updated item
                    item.save(user=request.user)
                    messages.success(request, json.dumps({
                        'type': 'success',
                        'text': f'TICKET{item.store_code}000{item.id}'
                    }))
                else:
                    messages.error(request, 'Invalid status value.')
            else:
                messages.error(request, 'You are not assigned to this ticket.')

        except Item.DoesNotExist:
            messages.error(request, 'Ticket not found.')
        except Exception as e:
            # Print the exception in the command line for debugging
            print(f"Error: {e}")

    return redirect('engineer_alltickets')



@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@login_required()
@allowed_users(allowed_roles=['Engineer'])
def table_view(request):
    engineer = request.user  # Get the currently logged-in engineer user

    all_tickets = Item.objects.filter(assignee=engineer).order_by('id')

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
    
    return render(request, 'Engineer/engineer_tables.html', context)

def engineer_export_to_pdf(request):
    # Get the 'export' parameter from the request
    current_user = request.user

    export_type = request.GET.get('export')

    if export_type == 'pdf':
        # Export to PDF
        template_path = 'StorePerson/pdf_template.html'
        all_tickets = Item.objects.filter(assignee=current_user).order_by('-created')
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

def engineer_export_to_excel(request):
    # Retrieve the data you want to export to Excel
    current_user = request.user

    all_tickets = Item.objects.filter(assignee=current_user).order_by('-created')

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
    


def get_ticket_details(request, ticket_id):
    try:
        ticket = Item.objects.get(id=ticket_id)
        ticket_details = {

            'category': ticket.category,

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
