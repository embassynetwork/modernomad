from django.contrib.auth.models import User
from django import forms
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _
from django.template import Template, Context
from modernomad.core.models import UserProfile, Use, Booking, EmailTemplate, Resource, Location, LocationMenu, Subscription, Subscription
from django.contrib.sites.models import Site

from django.contrib.auth.forms import UserCreationForm, UserChangeForm


def create_username(first_name, last_name, suffix=""):
    username = slugify("%s %s" % (first_name, last_name))

    if username == "":
        username = "unnamed"

    # Max username length is 30, so this gives us 9999 suffixes to make unique
    # usernames. Probably enough.
    username = username[:25]

    if suffix:
        username = "%s-%s" % (username, suffix)
    return username


class UserProfileForm(forms.ModelForm):
    # this is used in the profile edit page.
    ''' This form manually incorporates the fields corresponding to the base
    User model, associated via the UserProfile model via a OneToOne field, so
    that both models can be updated via the same form. '''

    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }

    # username = forms.CharField(widget=forms.HiddenInput(attrs={'required': 'false'}))
    first_name = forms.CharField(label=_('First Name'), widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'true', 'placeholder': 'first name'}))
    last_name = forms.CharField(label=_('Last Name'), widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'true', 'placeholder': 'last name'}))
    email = forms.EmailField(label=_("E-mail"), max_length=75, widget=forms.TextInput(attrs={'class': 'form-control', 'required': 'true', 'placeholder': 'email'}))
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'form-control', 'required': 'true', 'placeholder': 'password'}), label=_("New Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'form-control', 'required': 'true', 'placeholder': 'password (again)'}), label=_("New Password (again)"))

    class Meta:
        model = UserProfile
        exclude = ['user', 'status', 'image_thumb', 'customer_id', 'last4', 'primary_accounts']
        # fields = ['first_name', 'last_name', 'email', 'username', 'password1', 'password2', 'image', 'bio', 'links']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': '2', 'required': 'true'}),
            'links': forms.TextInput(attrs={'class': 'form-control'}),
            'projects': forms.Textarea(attrs={'class': 'form-control', 'rows': '2', 'required': 'true'}),
            'sharing': forms.Textarea(attrs={'class': 'form-control', 'rows': '2', 'required': 'true'}),
            'discussion': forms.Textarea(attrs={'class': 'form-control', 'rows': '2', 'required': 'true'}),
            'referral': forms.TextInput(attrs={'class': 'form-control', 'required': 'true', 'placeholder': 'referral'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'required': 'true', 'placeholder': 'city'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'phone'}),
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        # self.instance will always be an instance of UserProfile. if this
        # is an existing object, then populate the initial values.
        if self.instance.id is not None:
            # initialize the form fields with the existing values from the model.
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name

            # self.fields['username'].initial = self.instance.user.username
            # Since validation isn't working, make this readonly for now -JLS
            # self.fields['email'] = forms.EmailField(widget=forms.TextInput(attrs={'class':'form-control', 'readonly':True}))
            self.fields['email'].initial = self.instance.user.email

            self.fields['password1'] = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'form-control', 'placeholder': 'password'}), label=_("New Password"))
            self.fields['password1'].required = False
            self.fields['password2'] = forms.CharField(widget=forms.PasswordInput(render_value=False, attrs={'class': 'form-control', 'placeholder': 'password'}), label=_("New Password (again)"))
            self.fields['password2'].required = False

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'])
        return password2

    def clean_email(self):
        email = self.cleaned_data['email']
        if not self.instance.id:
            if email and User.objects.filter(email=email):
                raise forms.ValidationError('There is already a user with this email. If this is your account and you need to recover your password, you can do so from the login page.')
        return email

    def clean(self):
        # Generate a (unique) username, if one is needed (ie, if the user is new)
        if 'username' not in self.cleaned_data:
            tries = 1
            username = create_username(
                self.cleaned_data['first_name'],
                self.cleaned_data['last_name']
            )
            while User.objects.filter(username=username).count() > 0:
                tries = tries + 1
                username = create_username(
                    self.cleaned_data['first_name'],
                    self.cleaned_data['last_name'],
                    suffix=tries
                )
            self.cleaned_data['username'] = username

    def clean_links(self):
        # validates and formats the urls, returning a string of comma-separated urls
        links = self.cleaned_data['links']
        if len(links) > 0:
            raw_link_list = links.split(',')
            # the UrlField class has some lovely validation code written already.
            url = forms.URLField()
            cleaned_links = []
            for l in raw_link_list:
                try:
                    cleaned = url.clean(l.strip())
                    cleaned_links.append(cleaned)
                except forms.ValidationError:
                    # customize the error raised by UrlField.
                    raise forms.ValidationError('At least one of the URLs is not correctly formatted.')
            links = ", ".join(cleaned_links)
        return links

    def create_user(self):
        "Creates the User object"
        if not self.is_valid():
            raise Exception('The form must be valid in order to save')

        first = self.cleaned_data['first_name'].strip().title()
        if len(first) == 0:
            raise forms.ValidationError("First Name Required.")
        last = self.cleaned_data['last_name'].strip().title()
        if len(last) == 0:
            raise forms.ValidationError("Last Name Required.")
        email = self.cleaned_data['email'].strip().lower()
        if len(email) == 0:
            raise forms.ValidationError("Email Required.")
        if User.objects.filter(email=email).count() > 0:
            raise forms.ValidationError("Email address '%s' already in use." % email)

        # Username generated in clean method
        username = self.cleaned_data['username']

        user = User(username=username, first_name=first, last_name=last, email=email)
        password = self.clean_password2()
        user.set_password(password)
        user.save()
        return user

    def save(self, commit=True):
        # save the UserProfile (if editing an existing instance, it will be updated)
        profile = super(UserProfileForm, self).save(commit=False)
        # then update the User model with the values provided
        try:
            # Editing
            user = User.objects.get(pk=profile.user.pk)
            if self.cleaned_data.get('email'):
                user.email = self.cleaned_data.get('email')
            if self.cleaned_data['first_name']:
                user.first_name = self.cleaned_data.get('first_name')
            if self.cleaned_data['last_name']:
                user.last_name = self.cleaned_data.get('last_name')
            if self.cleaned_data.get('password2'):
                # set_password hashes the selected password
                user.set_password(self.cleaned_data['password2'])
            user.save()
        except:
            # Adding
            user = self.create_user()
            profile.user = user

        profile.save()
        return user


class LocationSettingsForm(forms.ModelForm):
    class Meta:
        model = Location
        # Not sure about Timezones and Bank Information.  Not including for now - JLS
        fields = ['name', 'slug', 'address', 'latitude', 'longitude',  'max_booking_days', 'welcome_email_days_ahead', 'house_access_code',
                  'ssid', 'ssid_password', 'email_subject_prefix', 'check_out', 'check_in', 'visibility']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'size': '32'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'size': '16'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'size': '64'}),
            'latitude': forms.TextInput(attrs={'class': 'form-control', 'size': '16'}),
            'longitude': forms.TextInput(attrs={'class': 'form-control', 'size': '16'}),
            'max_booking_days': forms.TextInput(attrs={'class': 'form-control', 'size': '16'}),
            'welcome_email_days_ahead': forms.TextInput(attrs={'class': 'form-control', 'size': '8'}),
            'house_access_code': forms.TextInput(attrs={'class': 'form-control', 'size': '32'}),
            'ssid': forms.TextInput(attrs={'class': 'form-control', 'size': '32'}),
            'ssid_password': forms.TextInput(attrs={'class': 'form-control', 'size': '32'}),
            'email_subject_prefix': forms.TextInput(attrs={'class': 'form-control', 'size': '32'}),
            'check_out': forms.TextInput(attrs={'class': 'form-control', 'size': '8'}),
            'check_in': forms.TextInput(attrs={'class': 'form-control', 'size': '8'}),
        }


class LocationUsersForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['house_admins', ]


class LocationContentForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['short_description', 'stay_page', 'announcement', 'front_page_stay', 'front_page_participate', 'image']
        widgets = {
            'short_description': forms.Textarea(attrs={'class': 'form-control', 'rows': '16', 'cols': '100', 'required': 'true'}),
            'stay_page': forms.Textarea(attrs={'class': 'form-control', 'rows': '16', 'cols': '100', 'required': 'true'}),
            'announcement': forms.Textarea(attrs={'class': 'form-control', 'rows': '16', 'cols': '100', 'required': 'true'}),
            'front_page_stay': forms.Textarea(attrs={'class': 'form-control', 'rows': '16', 'cols': '100', 'required': 'true'}),
            'front_page_participate': forms.Textarea(attrs={'class': 'form-control', 'rows': '16', 'cols': '100', 'required': 'true'}),
        }


class BootstrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BootstrapModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class LocationMenuForm(BootstrapModelForm):
    class Meta:
        model = LocationMenu
        exclude = ['location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'size': '32'}),
        }


class LocationPageForm(forms.Form):
    def __init__(self, *args, **kwargs):
        location = kwargs.pop('location', None)
        super(LocationPageForm, self).__init__(*args, **kwargs)
        if location:
            self.fields['menu'].queryset = LocationMenu.objects.filter(location=location)

    menu = forms.ModelChoiceField(queryset=None, empty_label=None)
    slug = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'size': '32'}))
    title = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'size': '32'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': '16', 'cols': '72', 'required': 'true'}))


def all_users():
    return [(u.id, "%s %s" % (u.first_name, u.last_name)) for u in User.objects.all()]

class LocationRoomForm(forms.ModelForm):
    change_backers = forms.MultipleChoiceField(choices=all_users, required=False)
    new_backing_date = forms.DateField(required=False)

    class Meta:
        model = Resource
        exclude = ['location']
        widgets = {
            'description': forms.Textarea(attrs={'rows': '3'}),
        }

    def __init__(self, *args, **kwargs):
        super(LocationRoomForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if field_name == 'change_backers':
                field.widget.attrs['class'] += ' chosen-select'
            elif field_name == 'new_backing_date':
                field.widget.attrs['class'] += ' datepicker'


class BookingUseForm(forms.ModelForm):
    '''Form for Use model with comment field added in (assumes an associated booking).'''
    comments = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control form-group"}), required=False)

    class Meta:
        model = Use
        exclude = ['created', 'updated', 'user', 'last_msg', 'status', 'location', 'accounted_by']
        widgets = {
            'arrive': forms.DateInput(attrs={'class': 'datepicker form-control form-group'}),
            'depart': forms.DateInput(attrs={'class': 'datepicker form-control form-group'}),
            'arrival_time': forms.TextInput(attrs={'class': 'form-control form-group'}),
            'resource': forms.Select(attrs={'class': 'form-control form-group'}),
            'purpose': forms.TextInput(attrs={'class': 'form-control form-group'}),
            'comments': forms.Textarea(attrs={'class': 'form-control form-group'}),
        }
        labels = {'resource': 'Room'}

    def __init__(self, location, *args, **kwargs):
        super(BookingUseForm, self).__init__(*args, **kwargs)
        if not location:
            raise Exception("No location given!")
        if self.instance.pk:
            if not hasattr(self.instance, 'booking'):
                raise Exception("This form requires a Booking object to be associated with the Use")
            self.fields['comments'].initial = self.instance.booking.comments

        self.location = location
        self.fields['resource'].choices = self.location.rooms_with_future_capacity_choices()

    def clean(self):
        cleaned_data = super(BookingUseForm, self).clean()
        arrive = cleaned_data.get('arrive')
        depart = cleaned_data.get('depart')
        if (depart - arrive).days > self.location.max_booking_days:
            self._errors["depart"] = self.error_class(
                ['Sorry! We only accept booking requests greater than %s in special circumstances. Please limit your request to %s or shorter, and add a comment if you would like to be consdered for a longer stay.' % (self.location.max_booking_days, self.location.max_booking_days)]
            )
        return cleaned_data


class AdminBookingForm(forms.ModelForm):
    class Meta:
        model = Use
        exclude = ['created', 'updated', 'user', 'last_msg', 'status', 'location']


class PaymentForm(forms.Form):
    name = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': "form-control", 'type': 'email'}))
    card_number = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control"}))
    cvc = forms.IntegerField(widget=forms.TextInput(attrs={'class': "form-control", 'type': 'number'}))
    expiration_month = forms.IntegerField(label='(MM)', widget=forms.TextInput(attrs={'class': "form-control", 'type': 'number'}))
    expiration_year = forms.IntegerField(label='(YYYY)', widget=forms.TextInput(attrs={'class': "form-control", 'type': 'number'}))
    amount = forms.FloatField(label="Amount", widget=forms.TextInput(attrs={'class': "form-control inline", 'type': 'number', 'min': '0', 'step': '0.01'}))
    comment = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control"}), required=False)

    def __init__(self, *args, **kwargs):
        # have to call super first, which initializes the 'fields' dictionary

        try:
            default_amount = kwargs.pop('default_amount')
        except:
            default_amount = None
        super(PaymentForm, self).__init__(*args, **kwargs)
        if default_amount:
            self.fields['amount'].initial = default_amount


class StripeCustomerCreationForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    card_number = forms.CharField()
    cvc = forms.IntegerField()
    expiration_month = forms.IntegerField(label='(MM)')
    expiration_year = forms.IntegerField(label='(YYYY)')


class EmailTemplateForm(forms.Form):
    ''' We don't actually make this a model form because it's a derivative
    function of a model but not directly constructed from the model fields
    itself.'''
    sender = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly', 'class': "form-control"}))
    recipient = forms.EmailField(widget=forms.TextInput(attrs={'class': "form-control"}))
    footer = forms.CharField(widget=forms.Textarea(attrs={'readonly': 'readonly', 'class': "form-control"}))
    subject = forms.CharField(widget=forms.TextInput(attrs={'class': "form-control"}))
    body = forms.CharField(widget=forms.Textarea(attrs={'class': "form-control"}))


class BookingEmailTemplateForm(EmailTemplateForm):

    def __init__(self, tpl, booking, location):
        ''' pass in an EmailTemplate instance, and a booking object '''

        domain = Site.objects.get_current().domain
        # calling super will initialize the form fields
        super(BookingEmailTemplateForm, self).__init__()

        # add in the extra fields
        self.fields['sender'].initial = location.from_email()
        self.fields['recipient'].initial = "%s, %s" % (booking.use.user.email, location.from_email())
        self.fields['footer'].initial = forms.CharField(
                widget=forms.Textarea(attrs={'readonly': 'readonly'})
            )
        self.fields['footer'].initial = '''--------------------------------\nYour booking is from %s to %s.\nManage your booking at https://%s%s.''' % (booking.use.arrive, booking.use.depart, domain, booking.get_absolute_url())

        # both the subject and body fields expect to have access to all fields
        # associated with a booking, so all booking model fields are
        # passed to the template renderer, even though we don't know (and so
        # that we don't have to know) which specific fields a given template
        # wants to use).

        template_variables = {
            'created': booking.created,
            'updated': booking.updated,
            'status': booking.use.status,
            'user': booking.use.user,
            'arrive': booking.use.arrive,
            'depart': booking.use.depart,
            'arrival_time': booking.use.arrival_time,
            'room': booking.use.resource,
            'num_nights': booking.use.total_nights(),
            'purpose': booking.use.purpose,
            'comments': booking.comments,
            'welcome_email_days_ahead': location.welcome_email_days_ahead,
            'reservation_url': "https://"+domain+booking.get_absolute_url()
        }

        self.fields['subject'].initial = '['+location.email_subject_prefix+'] ' + Template(tpl.subject).render(Context(template_variables)) + ' (#' + str(booking.id) + ')'
        self.fields['body'].initial = Template(tpl.body).render(Context(template_variables))


class SubscriptionEmailTemplateForm(EmailTemplateForm):

    def __init__(self, tpl, subscription, location):
        ''' pass in an EmailTemplate instance, and a subscription object '''

        domain = Site.objects.get_current().domain
        # calling super will initialize the form fields
        super(SubscriptionEmailTemplateForm, self).__init__()

        # add in the extra fields
        self.fields['sender'].initial = location.from_email()
        self.fields['recipient'].initial = "%s, %s" % (subscription.user.email, location.from_email())
        self.fields['footer'].initial = forms.CharField(widget=forms.Textarea(attrs={'readonly': 'readonly'}))
        self.fields['footer'].initial = '''--------------------------------\nYour membership id is %d. Manage your membership from your profile page https://%s/people/%s.''' % (subscription.id, domain, subscription.user.username)

        # both the subject and body fields expect to have access to all fields
        # associated with a booking, so all booking model fields are
        # passed to the template renderer, even though we don't know (and so
        # that we don't have to know) which specific fields a given template
        # wants to use).

        template_variables = {
            'subscription': subscription,
        }

        self.fields['subject'].initial = '['+location.email_subject_prefix+'] ' + Template(tpl.subject).render(Context(template_variables)) + ' (#' + str(subscription.id) + ')'
        self.fields['body'].initial = Template(tpl.body).render(Context(template_variables))


class AdminSubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        exclude = ['created', 'updated', 'created_by', 'location', 'bills', 'user']
