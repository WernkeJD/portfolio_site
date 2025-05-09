from django.http import HttpResponse, HttpRequest, JsonResponse
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.conf import settings

from .forms import ContactForm

# Create your views here.

def home(request):
    # Retrieve success or error messages from session
    success_message = request.session.pop('success_message', None)
    error_message = request.session.pop('error_message', None)

    form = ContactForm()
    
    return render(request, 'home.html', {
        'form': form,
        'success_message': success_message,
        'error_message': error_message,
    })

def contact_form(request: HttpRequest)-> JsonResponse:
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            subject = f"Message from {name}"
            message_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"

            try:
                send_mail(subject, message_body, settings.EMAIL_HOST_USER, [settings.DEFAULT_FROM_EMAIL])
                # Store the success message in session
                request.session['success_message'] = "Your message has been sent successfully!"
            except Exception as e:
                # If there's an error, store an error message in session
                request.session['error_message'] = f"An error occurred: {str(e)}"
        else:
            # If form is invalid, store error message in session
            request.session['error_message'] = "Form data is invalid."

        # Redirect to home page after processing the form
        return redirect('home')
    else:
        form = ContactForm()
