from django.http import HttpResponse
from django.shortcuts import render,redirect
import cx_Oracle

import HelperClass.Encrypt_Decrypt_Pass as ED_Operation


#EDIT
# login
user_info = {}  # holds user data across pages


# Create your views here.
def login(request):
    return render(request, "auth/LogInOrSignUp.html")

def signup(request):
    return render(request, "auth/SignUp.html")
def demo(request):
    return render(request, "demo.html")


# homepage URLs
def admin_home(request):
    #return render(request, "add html file", {'name': user_info['f_name'] + ' ' + user_info['l_name']})
    return HttpResponse("add admin_home")


def customer_home(request):
    #return render(request, "homepage/UserHome.html", {'name': user_info['f_name'] + ' ' + user_info['l_name']})
    return HttpResponse("add customer_home")


 # log in

def submit(request):
    username = request.POST['username']
    password = request.POST['pass']
    usertype = request.POST['usertype']
   
    
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='xe')
    conn = cx_Oracle.connect(user='HRS_OURDATABASE', password='12345', dsn=dsn_tns)

    c = conn.cursor()

    # TODO: connect database and verify
    if usertype == "admin":
        statement = "SELECT ADMIN_ID,PASSWORD,FIRST_NAME, LAST_NAME from HRS_OURDATABASE.ADMIN WHERE USERNAME=" + "\'" + username + "\'"
        c.execute(statement)
        if c:
            x = c.fetchone()
            return_id = x[0]
            return_password = x[1]
            return_f_name = x[2]
            return_l_name = x[3]

            user_info['pk'] = return_id
            user_info['f_name'] = return_f_name
            user_info['l_name'] = return_l_name
           
            user_info['usertype'] = usertype
            decoded_password=ED_Operation.Encrypt_Decrypt_Passwords(return_password).decryptPassword()
           
            if decoded_password == password:
                return HttpResponse("Need to add admin_homepage")
            else:
                return HttpResponse("Wrong Pass")
        else:
            return HttpResponse("Database Error or You don't exist")

    elif usertype == "customer":
        statement = "SELECT CUSTOMER_ID, PASSWORD, FIRST_NAME, LAST_NAME from HRS_OURDATABASE.CUSTOMER WHERE USERNAME=" + "\'" + username + "\'"
       
        c.execute(statement)
        if c:
            x = c.fetchone()
            
            return_id = x[0]
            return_password = x[1]
            return_f_name = x[2]
            return_l_name = x[3]

            user_info['pk'] = return_id
            user_info['f_name'] = return_f_name
            user_info['l_name'] = return_l_name
           
            user_info['usertype'] = "customer"

            decoded_password=ED_Operation.Encrypt_Decrypt_Passwords(return_password).decryptPassword()

            if decoded_password == password:
                return HttpResponse("Need to add customer_homepage")
            else:
                return HttpResponse("Wrong Pass")
        else:
            return HttpResponse("Database Error or You don't exist")
    return render(request, "auth/LogInOrSignUp.html")


#SignUpSubmit

def signupSubmit(request):
    usertype = request.POST['User']
    firstname = request.POST['fname']
    lastname = request.POST['lname']
    email = request.POST['email']
    
   
    
    city =request.POST['city']
    country=request.POST['country']
    username=request.POST['username']

    input_password = request.POST['pass']

    confirm_in = request.POST['cpass']
    if input_password != confirm_in:
        return HttpResponse("password and confirm password does not match!")

    encoded_password=ED_Operation.Encrypt_Decrypt_Passwords(input_password).encryptPassword()
    if usertype == 'admin':
        dsn_tns=cx_Oracle.makedsn('localhost','1521',service_name='xe')
        conn = cx_Oracle.connect(user='HRS_OURDATABASE', password='12345', dsn=dsn_tns)
        c = conn.cursor()
        
        
        
        statement = "INSERT INTO HRS_OURDATABASE.ADMIN(FIRST_NAME, LAST_NAME, GMAIL,CITY,COUNTRY,USERNAME,PASSWORD) VALUES (" + "\'" + firstname + \
                    "\', " + "\'" + lastname + "\'," + "\'" + email + "\', " + "\'" +city + "\', " + "\'" + country + "\'," + "\'" + username + "\', " + "\'" +encoded_password+ "\'" + ")"
        
        c.execute(statement)
        conn.commit()

    elif usertype == 'customer':
        dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='xe')
        conn = cx_Oracle.connect(user='HRS_OURDATABASE', password='12345', dsn=dsn_tns)
        c = conn.cursor()
        statement = "INSERT INTO HRS_OURDATABASE.CUSTOMER(FIRST_NAME, LAST_NAME, GMAIL, CITY,COUNTRY,USERNAME,PASSWORD) VALUES (" + "\'" + firstname + \
                    "\', " + "\'" + lastname + "\'," + "\'" + email + "\', " + "\'" + city + "\', " + "\'" +country+ "\'," + "\'" + username + "\', " + "\'" +encoded_password+ "\'" + ")"
        c.execute(statement)
        conn.commit()
        
    return redirect("login")

       
        


class ReservationListView(PermissionRequiredMixin, generic.ListView, generic.FormView):
    """
        View for list of reservations.
        Implements generic ListView.
        """
    model = Reservation
    # queryset field selects the objects to be displayed by the query.
    # Here, the objects are displayed by reservation date time in descending order
    queryset = Reservation.objects.all().order_by('-reservation_date_time')
    title = _("Reservation List")
    paginate_by = 5
    allow_empty = True
    form_class = CheckInRequestForm
    success_url = reverse_lazy('check_in-list')
    permission_required = 'main.can_view_reservation'
    extra_context = {'title': title}

    @transaction.atomic
    def form_valid(self, form):
        try:
            with transaction.atomic():
                checkin = form.save(commit=False)
                checkin.user = self.request.user
                checkin.save()
        except IntegrityError:
            raise Http404
        return super().form_valid(form)


class ReservationDetailView(PermissionRequiredMixin, generic.DetailView):
    """
    View for detail of reservation
    Implements generic DetailView
    """
    model = Reservation
    title = _("Reservation Information")
    permission_required = 'main.can_view_reservation'
    raise_exception = True
    extra_context = {'title': title}

class RoomListView(PermissionRequiredMixin, generic.ListView):
    """
    View for list of rooms.
    Implements generic ListView.
    """
    model = Room  # Chooses the model for listing objects
    paginate_by = 5  # By how many objects this has to be paginated
    title = _("Room List")  # This is used for title and heading
    permission_required = 'main.can_view_room'

    # By default only objects of the model are sent as context
    # However extra context can be passed using field extra_context
    # Here title is passed.

    extra_context = {'title': title}

    # By default:
    # template_name = room_list
    # if you want to change it, use field template_name
    # here don't do this, since it is already done as default.
    # for own views, it can be done.

    def get_queryset(self):
        filter_value = self.request.GET.get('filter', 'all')
        if filter_value == 'all':
            filter_value = 0
        elif filter_value == 'avail':
            filter_value = 1
        try:
            new_context = Room.objects.filter(availability__in=[filter_value, 1])
        except ValidationError:
            raise Http404(_("Wrong filter argument given."))
        return new_context

    def get_context_data(self, **kwargs):
        context = super(RoomListView, self).get_context_data(**kwargs)
        context['filter'] = self.request.GET.get('filter', 'all')
        return context


class RoomDetailView(PermissionRequiredMixin, generic.DetailView):
    """
    View for detail of room
    Implements generic DetailView
    """
    # The remaining are same as previous.
    model = Room
    title = _("Room Information")
    permission_required = 'main.can_view_room'
    extra_context = {'title': title}



    
   

       
        
    
        
        
