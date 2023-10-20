"""WebTicket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.views.generic.base import TemplateView

from . import views

urlpatterns = [
    
    #2.) ito ang gamitin kung 
    # base sa reference from django.views.generic.base import TemplateView

    path('admin/', admin.site.urls),
    path("login",views.login,name="login"),
    path('usrlogin',views.usrlogin,name="usrlogin"),
    path("logout", views.logout, name="logout"),


    path("",views.index,name="index"),
    #path('about',views.about,name="about"),
    path('contact',views.contact,name="contact"),
    path('register',views.loadregister,name="register"),
    path('loadselecteduser',views.loadselectedUser,name="loadselecteduser"),
    #path('loadusers',views.loadusers,name="loadusers"),
    

    path('saveRegister',views.saveRegister,name="saveRegister"),
    path('updateuser',views.updateRegister,name="updateuser"),
    path('users',views.loadUserProfile,name="users"),


    ## List of Users
    path('userlist',views.Listofusers,name="userlist"),
    path('approveuser/<int:selecteduserid>',views.approveuser,name="approveuser"),
    path('deactivateuser/<int:selecteduserid>',views.deactivateuser,name="deactivateuser"),

    ### TicketStatus
    path('ticketstatus',views.ticketstatus,name="ticketstatus"),
    path('viewTicket/<int:ticketID>',views.viewTicket,name="viewTicket"),
    path('assign/<int:ticketID>',views.assign,name="assign"),
    path('uAssign/<int:ticketID>',views.uAssign,name="uAssign"),

    ### Ticket Start Date and End Date assignment
    path('ticketdetails/<int:ticketID>',views.ticketdetails,name="ticketdetails"),
    path('assigndate/<int:ticketID>/<int:assignID>',views.dateassign,name="assigndate"),
    path('updatedateticketdate',views.updateassigndate,name="updatedateticketdate"),
    path('activity/<int:ticketID>/<int:assignID>/<int:createdBy>',views.myactivity,name="activity"),
    path('updateactivity',views.updateactivity,name="updateactivity"),
    #path('closeactivity',views.closeticket,name="closeactivity"),

    path('department',views.department,name="department"),
    path('loaddepartment/<int:deptID>',views.load_department,name="loaddepartment"),
    path('updateDepartment',views.update_Department,name="updateDepartment"),
    path('deleteDepartment/<int:deptid>',views.delete_department,name="deleteDepartment"),
    
    path('position',views.position,name="position"),
    path('deleteposition/<int:posID>',views.delete_positions,name="deleteposition"),
    path('updateposition',views.update_Position,name="updateposition"),
    path('loadposition/<int:posID>',views.load_Position,name="loadposition"),

    path('ticket',views.ticket,name="ticket"),
    path('loadticket/<int:ticketID>',views.load_ticket,name="loadticket"),
    path('deleteticket/<int:ticketID>',views.delete_ticket,name="deleteticket"),
    path('updateticket',views.update_ticket,name="updateticket"),

    path('userType',views.userType,name="userType"),
    path('loaduserType/<int:typeID>',views.load_userType,name="loaduserType"),
    path('deleteusertype/<int:typeID>',views.delete_userType,name="deleteusertype"),
    path('updateusertype',views.update_userType,name="updateusertype"),

    path('priority',views.priority,name="priority"),
    path('load_priority/<int:priorityID>',views.load_priority,name="load_priority"),
    path('deletepriority/<int:priorityID>',views.delete_priority,name="deletepriority"),
    path('updatepriority',views.update_priority,name="updatepriority"),

    path('tickettype',views.Tickettype,name="tickettype"),
    path('load_tickettype/<int:tickettypeID>',views.load_tickettype,name="load_tickettype"),
    path('deletetickettype/<int:tickettypeID>',views.delete_tickettype,name="deletetickettype"),
    path('updatetickettype',views.update_tickettype,name="updatetickettype"),

    path('tickettypestatus',views.tickettypestatus,name="tickettypestatus"),
    path('load_tickettypestatus/<int:ticketstatID>',views.load_tickettypestatus,name="load_tickettypestatus"),
    path('deletetickettypestatus/<int:ticketstatID>',views.delete_tickettypestatus,name="deletetickettypestatus"),
    path('updatetickettypestatus',views.update_tickettypestatus,name="updatetickettypestatus"),

]   

