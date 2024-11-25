# forms.py
from django import forms
from tickets.models import Category, Subcategory,ApprovalMatrix
from django.contrib.auth.models import User, Group
import re

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']


class SubcategoryForm(forms.ModelForm):
    class Meta:
        model = Subcategory
        fields = ['category', 'name', 'functionality', 'technically']



class ApprovalMatrixForm(forms.ModelForm):
    class Meta:
        model = ApprovalMatrix
        fields = ['functionally', 'technically', 'approval']

    def clean(self):
        cleaned_data = super().clean()
        functionally = cleaned_data.get('functionally')
        technically = cleaned_data.get('technically')

        if ApprovalMatrix.objects.filter(functionally=functionally, technically=technically).exists():
            raise forms.ValidationError('The combination of functionality, technicality, and approval already exists.')

        return cleaned_data

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group
from django.core.validators import EmailValidator

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(validators=[EmailValidator()])
    groups = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        label="Select Group",
        widget=forms.Select(attrs={'id': 'id_groups'})

    )

    def clean_username(self):
        username = self.cleaned_data.get("username")

        # Ensure the username contains only alphabetic characters
        if not re.match("^[a-zA-Z]+$", username):
            raise forms.ValidationError("Username should only contain alphabetic characters (no numbers or special characters).")
        
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists. Please choose a different one.")
        return username

    def clean_password1(self):
        password = self.cleaned_data.get("password1")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 != password2:
            raise forms.ValidationError("Passwords do not match.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['groups'].empty_label = "Select an option"
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data.get('email')  # Set the email field
        group = self.cleaned_data.get('groups')  # Get the selected group
        if commit:
            user.save()
            user.groups.add(group)  # Assign the user to the selected group
        return user




        # Add your custom validation logic here if needed
