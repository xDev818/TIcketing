
from ast import Dict
from collections import namedtuple
from pydoc import stripid
import string
from datetime import datetime

from django.shortcuts import render
from django.http import HttpRequest,HttpResponse




import mysql.connector
from mysql.connector import Error,cursor
from django.contrib import messages


# generate guuid 
import uuid

#reference for Encryption 


def glConnection():
    try:
            
            mysqlDB = mysql.connector.connect(host='localhost',
                                user='root',
                                password='Aa123456_',
                                database='DBTicket')
            return mysqlDB
    except Error as e:
            print("Error while connecting to MySQL (cursorfunc) --> ", e)
            return None



    

#1.) reference for urls path()
def index(request):

        #request.session['uID'] = 0
        #request.session.modified = True

        try:
            if 'uID' in request.session:

                userID = request.session['uID']

                rec = cursorUser("","","USER",int(userID),"")
                
                if rec is not None:

                    return render(request,"index.html",{'data' : rec})
                else:
                    return render(request,"index.html")
            else:
                return render(request,"index.html")
        except Error as e:
            print(e)
            return render(request,"index.html")

def login(request):

    return render(request,"login.html")

def logout(request):

    del request.session['uID']
    del request.session['name']
    request.session.modified = True


    usrrec = cursorUser("","","LOGIN",0,"")

    if usrrec is not None:
       
        request.session['uID'] = 0
        request.session['name'] = ""
        request.session.modified = True

        return render(request,"index.html", {'data' : usrrec})


### Ticket modules 

def ticket(request):
    try:
        userID = request.session['uID']
        rec = cursorUser("","","USER",int(userID),"")

        if rec is not None:
            # Load the TicketType here 
            tickettype = comboLoading("Ticket")
            mytickets = cursorUser("","","UserTicket",int(userID),0)
            return render(request,"ticket.html",{'data' : rec,'tickettype': tickettype,'tickets': mytickets })
        else:
            messagecontent = "Alert"
            error_message = "No Users in Ticket."
            userProfile = cursorUser("","","USER",int(userID),"")
            return render(request,"ticket.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})


    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading Priority."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"ticket.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def load_ticket(request,ticketID):
    try:
        userID = request.session['uID']

        conn = glConnection()
        varcursor = conn.cursor()

        #same parameters to all query
        
        sqlselect = ("select ticketID,title, NULLIF(description,'') as description from tblTickets where ticketID = %s ")
        parameters = (int(ticketID),)
        varcursor.execute(sqlselect,parameters)

        selected = namedtuplefetchall(varcursor)

        userProfile = cursorUser("","","USER",int(userID),"")
        tickettype = comboLoading("Ticket")
        mytickets = cursorUser("","","UserTicket",int(userID),0)


        conn.close()
        conn = None

        return render(request,"ticket.html",{'data' : userProfile,'tickettype': tickettype,'tickets': mytickets,'selected_tickets': selected})
        #return render(request,"ticket.html",{'data': userProfile,'priorities': priorities,'selected_priorities': selected})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in selecting Priority."
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"ticket.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def delete_ticket(request,ticketID):
    try:
        userID = request.session['uID']

        conn = glConnection()
        varcursor = conn.cursor()

        userProfile = cursorUser("","","USER",int(userID),"")
        
        sqlselect = ("select * from tbltickets where createdBy = %s "
            + "and ticketID= %s "
            + "and statusID = 1 "
            + "and assignUserID is not null")
        parameters = (int(userID),int(ticketID))
        varcursor.execute(sqlselect,parameters)
        chkrec = namedtuplefetchall(varcursor)

        if len(chkrec) == 0:

            sqlselect = ("delete from tblTickets "
                    + "where ticketID = %s")
            parameters = (int(ticketID),)
            varcursor.execute(sqlselect,parameters)
            conn.commit()
            conn.close()

            mytickets = cursorUser("","","UserTicket",int(userID),int(ticketID))
            ticket_type = comboLoading("TicketType")

            return render(request,"ticket.html",{'data' : userProfile,'tickettype': ticket_type,'tickets': mytickets})

        else:
            messagecontent = "Alert"
            error_message = " You can only delete Ticket without assigned Personnel.\n Please contact IT Service Desk"

            mytickets = cursorUser("","","UserTicket",int(userID),int(ticketID))
            ticket_type = comboLoading("TicketType")
            return render(request,"ticket.html",{'data':userProfile,'tickettype': ticket_type,'tickets': mytickets,'messagecontent':messagecontent,'error_message': error_message})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in deleting Ticket Type Status."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"tickettypestatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

    finally:
        conn.close()
        conn = None

def update_ticket(request):
    try:
        if request.method == 'POST':

            userID = request.session['uID']

            ticketID = request.POST['ticketID']
            strTitle = request.POST['title']
            strDesc = request.POST['description']
            TicketTypeID = request.POST['ticketTypeID']
            iStatus = "1" #Open
            dnow = datetime.now()

            updateconn = glConnection()
            updatecursor = updateconn.cursor()

            if len(ticketID) > 0:
                ## update selected departments 
                sqlselect = ("update tblTickets set title = %s,"
                    + "description = %s,"
                    + "dateLastupdated = %s, "
                    + "tickettypeID = %s, "
                    + "updateBy = %s "
                    + "where ticketID = %s")
                parameters = (strTitle,strDesc,dnow,int(TicketTypeID), int(userID),int(ticketID))
                updatecursor.execute(sqlselect,parameters)
                updateconn.commit()
            else:

                sqlselect = "insert into tblTickets(title,description,datecreated,statusID,ticketTypeID,createdBy) values (%s,%s,%s,%s,%s,%s);"
                parameters = [
                ( strTitle,strDesc,dnow,int(iStatus),int(TicketTypeID),int(userID))
                ]
                updatecursor.executemany(sqlselect,parameters)
                updateconn.commit()
                updateconn.close()

            mytickets = cursorUser("","","UserTicket",int(userID),"")
            print(mytickets)

            ticket_type = comboLoading("TicketType")
            userProfile = cursorUser("","","USER",int(userID),"")

            return render(request,"ticket.html",{'data' : userProfile,'tickettype': ticket_type,'tickets': mytickets,})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in updating selected Ticket Type Status."
        print(e)
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"ticket.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})


def dateassign(request,ticketID,assignID):

    try:
        userID = request.session['uID']
        userType = request.session['userType']
        userProfile = cursorUser("","","USER",int(userID),"")

        TicketStat = LoadTicketstatus(userID,userType)

        if userID == assignID:
            ## do the startdate and enddate
            ticketID = ticketID
            return render(request,"startendticket.html",{'data':userProfile,'ticket': ticketID})
            
        else:
            messagecontent = "Alert"
            error_message = " Only assigned IT can update start/end the ticket."
            return render(request,"ticketstatus.html",{'data':userProfile,'ticketstat': TicketStat,'messagecontent':messagecontent,'error_message': error_message})

    except Error as e:
            messagecontent = "Alert"
            error_message = " Error in updating start/end ticket. "
            userProfile = cursorUser("","","USER",int(userID),"")
            return render(request,"ticketstatus.html",{'data':userProfile,'ticketstat': TicketStat,'messagecontent':messagecontent,'error_message': error_message})

def myactivity(request,ticketID,assignID,createdBy):

    try:
        userID = request.session['uID']
        userType = request.session['userType']
        userProfile = cursorUser("","","USER",int(userID),"")

        if userID == assignID or userID == createdBy:
            ## do the startdate and enddate
            strticketID = ticketID
            strassignID = assignID
            strcreatedBy = createdBy

            statusdetails = comboLoading("TicketStatus")
            remarkdetails = cursorUser("","","RemarkDetails",int(userID),int(ticketID))
            return render(request,"ticketactivity.html",{'data':userProfile, 'remarkdetails': remarkdetails,'statusdetails':statusdetails, 'ticketid': strticketID,'assignID': strassignID,'createdBy': strcreatedBy })
            
        else:
            TicketStat = LoadTicketstatus(userID,userType)

            openrec = cursorUser("","","Open",int(userID),"")
            closerec = cursorUser("","","Close",int(userID),"")

            messagecontent = "Alert"
            error_message = " Ticket Activity can be update by creator or assign IT."

            return render(request,"ticketstatus.html",{'data' : userProfile,'ticketstat': TicketStat,'openrec': openrec,'closerec': closerec,'messagecontent':messagecontent,'error_message': error_message })
    except Error as e:
            messagecontent = "Alert"
            error_message = " Error in updating start/end ticket. "
            userProfile = cursorUser("","","USER",int(userID),"")
            return render(request,"ticketstatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def updateassigndate(request):

    try:
        userID = request.session['uID']
        userType = request.session['userType']
        userProfile = cursorUser("","","USER",int(userID),"")

        updateconn = glConnection()
        updatecursor = updateconn.cursor()

        if request.method == 'POST':

            ticketID = request.POST['ticketid']

            startdate = request.POST['start']
            enddate = request.POST['end']

            if len(startdate) > 0:

                if len(enddate) > 0:

                    startdate = datetime.strptime(request.POST['start'],'%Y-%m-%d')
                    enddate = datetime.strptime(request.POST['end'],'%Y-%m-%d')
                    strdate = datetime.now()

                    if(enddate >= startdate):

                        sqlselect = ("update tblTickets set startdate = %s,"
                            + "enddate = %s "
                            + "where ticketID = %s")
                        parameters = (startdate,enddate,int(ticketID))
                        updatecursor.execute(sqlselect,parameters)
                        updateconn.commit()
                        updateconn.close()
                        updateconn = None

                        TicketStat = LoadTicketstatus(userID,userType)
                        openrec = cursorUser("","","Open",int(userID),"")
                        closerec = cursorUser("","","Close",int(userID),"")

                        return render(request,"ticketstatus.html",{'data' : userProfile,'ticketstat': TicketStat,'openrec': openrec,'closerec': closerec })
                    else:
                        startdate = request.POST['start']
                        enddate = request.POST['end']
                        messagecontent = "Alert"
                        error_message = " End date must be equal or greater than Start Date."
                        return render(request,"startendticket.html",{'data':userProfile,'ticket': ticketID,'startdate':startdate,'enddate':enddate, 'messagecontent':messagecontent,'error_message': error_message})

                else:
                    messagecontent = "Alert"
                    error_message = " Select End date."
                    return render(request,"startendticket.html",{'data':userProfile,'ticket': ticketID,'startdate':startdate,'enddate':enddate,'messagecontent':messagecontent,'error_message': error_message})

            else:
                messagecontent = "Alert"
                error_message = "Select  Start Date."
                return render(request,"startendticket.html",{'data':userProfile,'ticket': ticketID,'messagecontent':messagecontent,'error_message': error_message})

            
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in updating start/end ticket. "
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"startendticket.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def updateactivity(request):
    try:
       
        btn = request.POST['Update']

        userID = int(request.session['uID'])
        userType = request.session['userType']
        userProfile = cursorUser("","","USER",int(userID),"")

        strremarks = request.POST['remarks']
        ticketID = int(request.POST['ticketID'])
        strassignID = int(request.POST['assignID'])
        icreatedBy = int(request.POST['createdBy'])
        dnow = datetime.now()

        print(request.POST['statusID'])
        iStat = int(request.POST['statusID'])
        dnow = datetime.now()

        updateconn = glConnection()
        updatecursor = updateconn.cursor()

        if btn == 'Remarks':

            if len(strremarks) > 0:

                sqlselect = "insert into tblTicketDetails(ticketID,createdBy,remark,datecreated) values(%s,%s,%s,%s);"
                parameters = [(ticketID,userID,strremarks,dnow)]
                updatecursor.executemany(sqlselect,parameters)
                updateconn.commit()
                updateconn.close()
                updateconn = None

                statusdetails = comboLoading("TicketStatus")
                remarkdetails = cursorUser("","","RemarkDetails",int(userID),int(ticketID))
                return render(request,"ticketactivity.html",{'data':userProfile, 'remarkdetails': remarkdetails,'statusdetails':statusdetails, 'ticketid': ticketID,'assignID': strassignID,'createdBy': icreatedBy })
            else:
                messagecontent = "Alert"
                error_message = " Remarks must not be empty."
                userProfile = cursorUser("","","USER",int(userID),"")
                remarkdetails = cursorUser("","","RemarkDetails",int(userID),int(ticketID))
                statusdetails = comboLoading("TicketStatus")
                return render(request,"ticketactivity.html",{'data':userProfile, 'remarkdetails': remarkdetails,'statusdetails': statusdetails, 'ticketid': ticketID,'assignID': strassignID,'createdBy': icreatedBy })

        elif btn == 'Close':
            print(btn)
            print ("Trying to click close button")
            if len(strremarks) > 0:
                    sqlselect = "insert into tblTicketDetails(ticketID,createdBy,remark,datecreated) values(%s,%s,%s,%s);"
                    parameters = [(ticketID,userID,strremarks,dnow)]
                    updatecursor.executemany(sqlselect,parameters)
                    updateconn.commit()
                    updateconn.close()
                    updateconn = None

                    #print("done insert details ")

                    updateconn = glConnection()
                    updatecursor = updateconn.cursor()

                    sqlselect = ("update tblTickets set statusID = %s,"
                            + "dateClosed = %s "
                            + "WHERE ticketID = %s")
                    parameters = (iStat,dnow,ticketID)
                    updatecursor.execute(sqlselect,parameters)
                    updateconn.commit()
                    updateconn.close()
                    updateconn = None

                    updateconn = glConnection()
                    updatecursor = updateconn.cursor()
                    strremarks = " closing ticket ID (" + str(ticketID) + ")"
                    sqlselect = "insert into tblRemarks(remarks,datecreated,createdBy) values(%s,%s,%s);"
                    parameters = [(strremarks,dnow,userID)]
                    updatecursor.executemany(sqlselect,parameters)
                    updateconn.commit()
                    updateconn.close()
                    updateconn = None

                    #print("done insert remarks ")

                    TicketStat = LoadTicketstatus(userID,userType)
                    openrec = cursorUser("","","Open",int(userID),"")
                    closerec = cursorUser("","","Close",int(userID),"")

                    return render(request,"ticketstatus.html",{'data' : userProfile,'ticketstat': TicketStat,'openrec': openrec,'closerec': closerec})
            else:
                    messagecontent = "Alert"
                    error_message = " Remarks cannot be empty."
                    userProfile = cursorUser("","","USER",int(userID),"")
                    statusdetails = comboLoading("TicketStatus")
                    remarkdetails = cursorUser("","","RemarkDetails",int(userID),int(ticketID))
                    return render(request,"ticketactivity.html",{'data':userProfile, 'remarkdetails': remarkdetails,'statusdetails':statusdetails, 'ticketid': ticketID,'assignID': strassignID,'createdBy': icreatedBy })       
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in inserting records.  -- " + e
        userProfile = cursorUser("","","USER",int(userID),"")
        remarkdetails = cursorUser("","","RemarkDetails",int(userID),int(ticketID))
        statusdetails = comboLoading("TicketStatus")
        return render(request,"ticketactivity.html",{'data':userProfile, 'remarkdetails': remarkdetails,'statusdetails':statusdetails, 'ticketid': ticketID,'assignID': strassignID,'createdBy': icreatedBy,'messagecontent':messagecontent,'error_message': error_message })

def closeticket(request):
    try:
        #if request.method == 'POST':
        #    request.form[]

        print ("try closing ")
        userID = int(request.session['uID'])
        userType = request.session['userType']
        userProfile = cursorUser("","","USER",int(userID),"")

        strremarks = request.POST['remarks']
        ticketID = int(request.POST['ticketID'])
        strassignID = int(request.POST['assignID'])
        icreatedBy = int(request.POST['createdBy'])
        print(request.POST['statusID'])
        #iStat = int(request.POST['statusID'])
        dnow = datetime.now()

        updateconn = glConnection()
        updatecursor = updateconn.cursor()

        if userID == icreatedBy:

            if len(strremarks) > 0:
                    sqlselect = "insert into tblTicketDetails(ticketID,createdBy,remark,datecreated) values(%s,%s,%s,%s);"
                    parameters = [(ticketID,userID,strremarks,dnow)]
                    updatecursor.executemany(sqlselect,parameters)
                    updateconn.commit()
                    updateconn.close()
                    updateconn = None

                    updateconn = glConnection()
                    updatecursor = updateconn.cursor()

                    sqlselect = ("update tblTickets set statusID = %s "
                            + "WHERE ticketID = %s ")
                    parameters = (1,ticketID)
                    updatecursor.execute(sqlselect,parameters)
                    updateconn.commit()
                    updateconn.close()
                    updateconn = None

                    updateconn = glConnection()
                    updatecursor = updateconn.cursor()
                    strremarks = " closing ticket ID (" + str(ticketID) + ")"
                    sqlselect = "insert into tblRemarks(remarks,datecreated,createdBy) values(%s,%s,%s);"
                    parameters = [(strremarks,dnow,userID)]
                    updatecursor.executemany(sqlselect,parameters)
                    updateconn.commit()
                    updateconn.close()
                    updateconn = None

                    TicketStat = LoadTicketstatus(userID,userType)

                    openrec = cursorUser("","","Open",int(userID),"")
                    closerec = cursorUser("","","Close",int(userID),"")

                    return render(request,"ticketstatus.html",{'data' : userProfile,'ticketstat': TicketStat,'openrec': openrec,'closerec': closerec})
            else:
                messagecontent = "Alert"
                error_message = " Remarks cannot be empty."
                userProfile = cursorUser("","","USER",int(userID),"")
                statusdetails = comboLoading("TicketStatus")
                remarkdetails = cursorUser("","","RemarkDetails",int(userID),int(ticketID))
                return render(request,"ticketactivity.html",{'data':userProfile, 'remarkdetails': remarkdetails,'statusdetails':statusdetails, 'ticketid': strticketID,'assignID': strassignID,'createdBy': strcreatedBy })
        else:
                messagecontent = "Alert"
                error_message = " Ticket can be close by creator."
                userProfile = cursorUser("","","USER",int(userID),"")
                statusdetails = comboLoading("TicketStatus")
                remarkdetails = cursorUser("","","RemarkDetails",int(userID),int(ticketID))
                return render(request,"ticketactivity.html",{'data':userProfile, 'remarkdetails': remarkdetails,'statusdetails':statusdetails, 'ticketid': strticketID,'assignID': strassignID,'createdBy': strcreatedBy })
 

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in inserting records.  -- " + e
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"ticketactivity.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})


### end of ticket modules 


### Ticket Status 

def LoadTicketstatus(icreated,userType):

    try:
        ticketConn = glConnection()
        ticketcursor = ticketConn.cursor()

        if userType == "Admin":

            sqlStatement = ("SELECT tblTickets.ticketID,tblTickets.title,tblTickets.description,tblTickets.createdby,cast(tblTickets.datecreated as Date) as nDate,cast(tblTickets.startdate as Date) as Sdate,cast(tblTickets.enddate as Date) as Edate,tblTickets.statusID,tblTickets.tickettypeID,"
                        + "IFnull(tblTickets.assignuserid,'0') as assignuserid, IFnull(tblTickets.priorityID,'0') as priorityID,"
                        + "tblTicketType.name as Category,tblpriority.priorityname,tblTicketStatus.statusName," 
                        + "TblUsers.name as DisplayName " 
                        + "FROM DBTicket.tblTickets "
                        + "inner join tblTicketType "
                        + "on tblTickets.tickettypeID = tblTicketType.typeID "
                        + "Left join tblPriority "
                        + "on tblTickets.priorityID = tblpriority.priorityid " 
                        + "left join tblUsers " 
                        + "on tblTickets.assignUserID = tblUsers.ID " 
                        + "LEFT JOIN tblTicketStatus "
                        + "ON tblTickets.statusID = tblTicketStatus.statusID "
                        + "where tblTickets.statusid =1 ")
            ticketcursor.execute(sqlStatement)

        elif (userType == "Support"):
        # or (userType == "Service Desk"):
            sqlStatement = ("SELECT tblTickets.ticketID,tblTickets.title,tblTickets.description,tblTickets.createdby,cast(tblTickets.datecreated as Date) as nDate,cast(tblTickets.startdate as Date) as Sdate,cast(tblTickets.enddate as Date) as Edate,tblTickets.statusID,tblTickets.tickettypeID,"
                        + "IFnull(tblTickets.assignuserid,'0') as assignuserid, IFnull(tblTickets.priorityID,'0') as priorityID,"
                        + "tblTicketType.name as Category,tblpriority.priorityname,tblTicketStatus.statusName," 
                        + "TblUsers.name as DisplayName " 
                        + "FROM DBTicket.tblTickets "
                        + "inner join tblTicketType "
                        + "on tblTickets.tickettypeID = tblTicketType.typeID "
                        + "Left join tblPriority "
                        + "on tblTickets.priorityID = tblpriority.priorityid " 
                        + "left join tblUsers " 
                        + "on tblTickets.assignUserID = tblUsers.ID " 
                        + "LEFT JOIN tblTicketStatus "
                        + "ON tblTickets.statusID = tblTicketStatus.statusID "
                        + "LEFT JOIN tblUsertype "
                        + "ON tblUsers.userTypeID=tblUsertype.userTypeID "
                        + "where tblTickets.statusid = '1' "
                        + "and tblTickets.assignuserid = %s" )
                        #+ "and tblTickets.createdby = %s)")
            tuple = (int(icreated),)
            ticketcursor.execute(sqlStatement,tuple)


        elif userType == "Service Desk":
            sqlStatement = ("SELECT tblTickets.ticketID,tblTickets.title,tblTickets.description,tblTickets.createdby,cast(tblTickets.datecreated as Date) as nDate,cast(tblTickets.startdate as Date) as Sdate,cast(tblTickets.enddate as Date) as Edate,tblTickets.statusID,tblTickets.tickettypeID,"
                    + "IFnull(tblTickets.assignuserid,'0') as assignuserid, IFnull(tblTickets.priorityID,'0') as priorityID,"
                    + "tblTicketType.name as Category,tblpriority.priorityname,tblTicketStatus.statusName," 
                    + "TblUsers.name as DisplayName " 
                    + "FROM DBTicket.tblTickets "
                    + "inner join tblTicketType "
                    + "on tblTickets.tickettypeID = tblTicketType.typeID "
                    + "Left join tblPriority "
                    + "on tblTickets.priorityID = tblpriority.priorityid " 
                    + "left join tblUsers " 
                    + "on tblTickets.assignUserID = tblUsers.ID " 
                    + "LEFT JOIN tblTicketStatus "
                    + "ON tblTickets.statusID = tblTicketStatus.statusID "
                    + "LEFT JOIN tblUsertype "
                    + "ON tblUsers.userTypeID=tblUsertype.userTypeID "
                    + "where tblTickets.statusid = '1' ")
                    #+ "or (tblTickets.createdby = %s or  tblTickets.assignuserid = %s)")
            tuple = (int(icreated),int(icreated))
            ticketcursor.execute(sqlStatement)

        else: # Ordinary users 
            sqlStatement = ("SELECT tblTickets.ticketID,tblTickets.title,tblTickets.description,tblTickets.createdby,cast(tblTickets.datecreated as Date) as nDate,cast(tblTickets.startdate as Date) as Sdate,cast(tblTickets.enddate as Date) as Edate,tblTickets.statusID,tblTickets.tickettypeID,"
                    + "tblTickets.assignuserid, tblTickets.priorityID, tblTicketType.name as Category,tblpriority.priorityname,tblTicketStatus.statusName," 
                    + "TblUsers.name as DisplayName " 
                    + "FROM DBTicket.tblTickets "
                    + "LEFT join tblTicketType "
                    + "on tblTickets.tickettypeID = tblTicketType.typeID "
                    + "LEFT join tblPriority "
                    + "on tblTickets.priorityID = tblpriority.priorityid " 
                    + "left join tblUsers " 
                    + "on tblTickets.assignUserID = tblUsers.ID " 
                    + "LEFT JOIN tblTicketStatus "
                    + "ON tblTickets.statusID = tblTicketStatus.statusID "
                    + "LEFT JOIN tblUsertype "
                    + "ON tblUsers.userTypeID=tblUsertype.userTypeID "
                    + "where (tblTickets.statusid = '1' AND tblTickets.createdby = %s) ")
            parameters = (int(icreated),)
            ticketcursor.execute(sqlStatement,parameters)
    
        return namedtuplefetchall(ticketcursor)

    except Error as e:
        print("error in loading ticket")
        print(e)

def ticketstatus(request):
    try:    
        userID = request.session['uID']
        userType = request.session['userType']

        TicketStat = LoadTicketstatus(userID,userType)


        rec = cursorUser("","","USER",int(userID),"")

        openrec = cursorUser("","","Open",int(userID),"")
        closerec = cursorUser("","","Close",int(userID),"")

    
        if len(rec) > 0:

            return render(request,"ticketstatus.html",{'data' : rec,'ticketstat': TicketStat,'openrec': openrec,'closerec': closerec })
        else:

            messagecontent = "Alert"
            error_message = " No Ticket(s) created."
            userProfile = cursorUser("","","USER",int(userID),"")
            return render(request,"ticketstatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

        #else:
        #    return HttpResponse('users do not match, nned to crete page for error ')

            #return render(request,"index.html")
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading User Type."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"ticketstatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def assign(request,ticketID):
 
        try:
            #assignUserID,priorityID,
            userID = request.session['uID']
            userType = request.session['userType']
            userProfile = cursorUser("","","USER",int(userID),"")
            
            

            if userType == "Admin" or userType == "Service Desk":
                # do the assignment of user
                users = cursorUser("","","LoadUsersAssign","","")
                priorities = cursorUser("","","LoadPriority","","")
                selectedticket = cursorUser("","","tickets","",int(ticketID))
               
                if len(userProfile) > 0:
                        #'priorities': priorities,'ticketdata': selectedticket
                        return render(request,"assignTicket.html",{'data' : userProfile,'Users': users,'priorities': priorities,'ticketdata': selectedticket})
                        #,'priorities': priorities,'ticketdata': selectedticket})
                        #return render(request,"test.html",{'data' : rec,'users': users})
                else:
                    TicketStat = LoadTicketstatus(userID,userType)
                    messagecontent = "Alert"
                    error_message = " No Ticket(s) created."
                    return render(request,"assignTicket.html",{'data' : userProfile,'ticketstat': TicketStat})
            else:
                    messagecontent = "Alert"
                    error_message = " Only IT Service Desk can assign support personnel."
                    TicketStat = LoadTicketstatus(userID,userType)
                    return render(request,"ticketstatus.html",{'data':userProfile,'ticketstat': TicketStat,'messagecontent':messagecontent,'error_message': error_message})


        except Error as e:
            messagecontent = "Alert"
            error_message = e
            userProfile = cursorUser("","","USER",int(userID),"")
            return render(request,"ticketstatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def viewTicket(request,ticketID):

    try :

        if 'uID' in request.session:
            userID = request.session['uID']
            userProfile = cursorUser("","","USER",int(userID),"")

            
            userType = request.session["userType"]
            
            selectedticket = cursorUser("","","ticketSelected",int(userID),int(ticketID))

            if len(selectedticket) > 0:

                tickettype = comboLoading("TicketType")
                #cursorUser("","","TICKET",int(userID),"")
                
                if len(userProfile) > 0:

                    tickettype = comboLoading("Ticket")
                    mytickets = cursorUser("","","UserTicket",int(userID),0)
                    
                    conn = glConnection()
                    varcursor = conn.cursor()

                    #same parameters to all query
                    
                    sqlselect = ("select ticketID,title, NULLIF(description,'') as description from tblTickets where ticketID = %s ")
                    parameters = (int(ticketID),)
                    varcursor.execute(sqlselect,parameters)

                    selected = namedtuplefetchall(varcursor)

                    userProfile = cursorUser("","","USER",int(userID),"")
                    tickettype = comboLoading("Ticket")
                    mytickets = cursorUser("","","UserTicket",int(userID),0)

                    conn.close()
                    conn = None

                    return render(request,"ticket.html",{'data' : userProfile,'tickettype': tickettype,'tickets': mytickets,'selected_tickets': selected})
                else:
                    #response to page on Error
                   
                    messagecontent = "Alert"
                    error_message = "No Ticket selected."
                    return render(request,"ticketstatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

            else:

                error_message = "Message: You can only update the Ticket that you created."
                #return render(request,"viewTicket.html", {'data': rec,'ticket_type': tickettype,'ticketdata': selectedticket,'error_message': error_message })
                TicketStat = LoadTicketstatus(userID,userType)
                openrec = cursorUser("","","Open",int(userID),"")
                closerec = cursorUser("","","Close",int(userID),"")

                if len(userProfile) > 0:

                    return render(request,"ticketstatus.html",{'data' : userProfile,'ticketstat': TicketStat,'openrec': openrec,'closerec': closerec,'error_message': error_message })
                else:
                    messagecontent = "Alert"
                    error_message = "No Users in Ticket"
                    return render(request,"ticketstatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

        else:
            return render(request,"index.html",)

    except Error as e:
            messagecontent = "Alert"
            error_message = e
            return render(request,"ticketstatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def uAssign(request,ticketID):

    if request.method == 'POST':

        try:
            
            userID = request.session['uID']
            userType = request.session['userType']
           
            assignUserID = request.POST['userID']
            priorityID = request.POST['priority']

            strdateCreated = datetime.now()

            updateConn = glConnection()
            updatecursor = updateConn.cursor()
            sqlselect = ("update dbticket.tblTickets set tblTickets.assignuserID = %s,"
            + "tblTickets.priorityID = %s,"
            + "tblTickets.updateBy = %s,"
            + "tblTickets.dateLastUpdated = %s "
            + "where tblTickets.ticketID = %s")
            
            parameters = (int(assignUserID),int(priorityID),int(userID),strdateCreated,int(ticketID))

            updatecursor.execute(sqlselect,parameters)
            updateConn.commit()

            userProfile = cursorUser("","","USER",int(userID),"")

            error_message = "Message: You can only update the Ticket that you created."
            #return render(request,"viewTicket.html", {'data': rec,'ticket_type': tickettype,'ticketdata': selectedticket,'error_message': error_message })
            TicketStat = LoadTicketstatus(userID,userType)
            openrec = cursorUser("","","Open",int(userID),"")
            closerec = cursorUser("","","Close",int(userID),"")

            return render(request,"ticketstatus.html",{'data' : userProfile,'ticketstat': TicketStat,'openrec': openrec,'closerec': closerec,'error_message': error_message })

            #if len(rec) > 0:
            #return render(request,"ticketstatus.html",{'data' : userProfile,'ticketstat': TicketStat })
            # else:
            #     return HttpResponse('No Users in Ticket')
        except Error as e:
            messagecontent = "Alert"
            error_message = e
            userProfile = cursorUser("","","USER",int(userID),"")
            return render(request,"ticketstatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

### End of Ticket Status


### Ticket Details 

def ticketdetails(request,ticketID):
    try:
        print()

    except Error as e:
        print()

def activity(request):
    try:
        print()

    except Error as e:
        print()
### end of Ticket details 



def about(request):
    try:
        userID = request.session['uID']

        rec = cursorUser("","","USER",int(userID),"")
            
        if rec is not None:
            return render(request,"about.html",{'data': rec })
    except Error as e:
        print(e)
        return HttpResponse(" Error in About")

### List of users
def Listofusers(request):
    try:
            userID = request.session['uID']

            userProfile = cursorUser("","","USER",int(userID),"")
            listofusers = comboLoading("ListofUsers")

            return render(request,"users.html",{'data': userProfile,'listofusers': listofusers})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading User Type."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"UserType.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def approveuser(request,selecteduserid):
    try:
            userID = request.session['uID']

            updateconn = glConnection()
            varcursor = updateconn.cursor()

            sqlselect = ("update tblusers set isApproved = '1' "
                    + "where tblusers.id = %s")
            parameters = (int(selecteduserid),)
            varcursor.execute(sqlselect,parameters)
            updateconn.commit()

            userProfile = cursorUser("","","USER",int(userID),"")
            listofusers = comboLoading("ListofUsers")
            
            return render(request,"users.html",{'data': userProfile,'listofusers': listofusers})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading User Type."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"users.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})
    finally:
        updateconn.close()
        updateconn = None

def deactivateuser(request,selecteduserid):
    try:
            userID = request.session['uID']

            updateconn = glConnection()
            varcursor = updateconn.cursor()

            sqlselect = ("update tblusers set tblusers.isApproved = '0' "
                    + "where tblusers.id = %s")
            parameters = (int(selecteduserid),)
            varcursor.execute(sqlselect,parameters)
            updateconn.commit()

            userProfile = cursorUser("","","USER",int(userID),"")
            listofusers = comboLoading("ListofUsers")

            return render(request,"users.html",{'data': userProfile,'listofusers': listofusers})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading User Type."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"users.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})
    finally:
        updateconn.close()
        updateconn = None

### end of List of Users

### Positions Functions

def position(request):
    try:
            userID = request.session['uID']

            userProfile = cursorUser("","","USER",int(userID),"")
            departments = comboLoading("Position")
         

            return render(request,"positions.html",{'data': userProfile,'positions': departments})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading Positions."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"department.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def delete_positions(request,posID):
    try:
        userID = request.session['uID']

        deleteconn = glConnection()
        deletecursor = deleteconn.cursor()

        sqlselect = ("delete from tblPositions "
                + "where id = %s")
        parameters = (int(posID),)
        deletecursor.execute(sqlselect,parameters)
        deleteconn.commit()

        departments = comboLoading("Position")
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"positions.html",{'data': userProfile,'positions': departments})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in deleting selected Department.  "
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"positions.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def update_Position(request):
    try:
        if request.method == 'POST':

            userID = request.session['uID']

            posid = request.POST['posID']
            name = request.POST['positionname']
            desc = request.POST['description']

            userProfile = cursorUser("","","USER",int(userID),"")

            updateconn = glConnection()
            updatecursor = updateconn.cursor()

            if len(posid) > 0: 
                sqlselect = ("update tblPositions set positionname = %s,"
                    + "description = %s "
                    + "where  id = %s")
                parameters = (name,desc,int(posid))
                updatecursor.execute(sqlselect,parameters)
                updateconn.commit()
            else:
                sqlselect = ("insert into tblPositions(positionname,description) values(%s,%s)")
                parameters = [(name,desc)]
                updatecursor.executemany(sqlselect,parameters)
                updateconn.commit()
                updateconn.close()

             ## Loading of departments
            position = comboLoading("Position")

        return render(request,"positions.html",{'data': userProfile,'positions': position})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in updating selected Positions."
        print(e)
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"positions.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def load_Position(request,posID):
    try:
        userID = request.session['uID']

        deptconn = glConnection()
        pcursor = deptconn.cursor()

        #same parameters to all query
        
        sqlselect = ("select id,positionname, NULLIF(description,'-') as description from tblPositions where id = %s "
            + "order by positionname")
        parameters = (int(posID),)
        pcursor.execute(sqlselect,parameters)

        selected = namedtuplefetchall(pcursor)

        userProfile = cursorUser("","","USER",int(userID),"")
        positions = comboLoading("Position")

        deptconn.close()
        deptconn = None


        return render(request,"positions.html",{'data': userProfile,'positions': positions,'selected_position': selected})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in selecting Position."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"positions.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

### end of positions 


### Department functions
def delete_department(request,deptid):
    try:
        userID = request.session['uID']

        deleteconn = glConnection()
        deletecursor = deleteconn.cursor()

        sqlselect = ("delete from tblDepartments "
                + "where  deptid = %s")
        parameters = (int(deptid),)
        deletecursor.execute(sqlselect,parameters)
        deleteconn.commit()

        departments = comboLoading("Department")
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"department.html",{'data': userProfile,'departments': departments})


    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in deleting selected Department.  "
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"department.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def update_Department(request):
    try:
        if request.method == 'POST':

            userID = request.session['uID']

            depid = request.POST['deptID']
            name = request.POST['departmentname']
            desc = request.POST['description']

            userProfile = cursorUser("","","USER",int(userID),"")

            updateconn = glConnection()
            updatecursor = updateconn.cursor()

            if len(depid) > 0:
                ## update selected departments 
                sqlselect = ("update tblDepartments set departmentname = %s,"
                    + "description = %s "
                    + "where  deptid = %s")
                parameters = (name,desc,int(depid))
                updatecursor.execute(sqlselect,parameters)
                updateconn.commit()
            else:
                sqlselect = ("insert into tblDepartments(departmentname,description) values(%s,%s)")
                parameters = [(name,desc)]
                updatecursor.executemany(sqlselect,parameters)
                updateconn.commit()
                updateconn.close()

             ## Loading of departments
            departments = comboLoading("Department")


        return render(request,"department.html",{'data': userProfile,'departments': departments})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in updating selected Departments."
        print(e)
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"department.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def load_department(request,deptID):
    try:
        userID = request.session['uID']

        deptconn = glConnection()
        deptcursor = deptconn.cursor()

        #same parameters to all query
        
        sqlselect = ("select deptid,departmentName, NULLIF(description,'-') as description from tblDepartments where deptid = %s "
            + "order by DepartmentName")
        parameters = (int(deptID),)
        deptcursor.execute(sqlselect,parameters)

        selected = namedtuplefetchall(deptcursor)

        userProfile = cursorUser("","","USER",int(userID),"")
        departments = comboLoading("Department")

        deptconn.close()
        deptconn = None

        return render(request,"department.html",{'data': userProfile,'departments': departments,'selected_dept': selected})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in selecting Departments."
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"department.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def department(request):
    try:
            userID = request.session['uID']

            userProfile = cursorUser("","","USER",int(userID),"")
            departments = comboLoading("Department")

            return render(request,"department.html",{'data': userProfile,'departments': departments})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading Departments."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"department.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

### end of department 

### UserType 
def userType(request):
    try:
            userID = request.session['uID']

            userProfile = cursorUser("","","USER",int(userID),"")
            usertype = comboLoading("UserTypes")

            return render(request,"UserType.html",{'data': userProfile,'userTypes': usertype})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading User Type."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"UserType.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def load_userType(request,typeID):
    try:
        userID = request.session['uID']

        deptconn = glConnection()
        deptcursor = deptconn.cursor()

        #same parameters to all query
        
        sqlselect = ("select userTypeID,userType, NULLIF(description,'-') as description from tblUsertype where userTypeID = %s "
            + "order by userType")
        parameters = (int(typeID),)
        deptcursor.execute(sqlselect,parameters)

        selected = namedtuplefetchall(deptcursor)

        userProfile = cursorUser("","","USER",int(userID),"")
        usertypes = comboLoading("UserTypes")

        deptconn.close()
        deptconn = None

        return render(request,"UserType.html",{'data': userProfile,'userTypes': usertypes,'selected_usertype': selected})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in selecting User Type."
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"UserType.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def delete_userType(request,typeID):
    try:
        userID = request.session['uID']

        deleteconn = glConnection()
        deletecursor = deleteconn.cursor()

        sqlselect = ("delete from tblUsertype "
                + "where  userTypeID = %s")
        parameters = (int(typeID),)
        deletecursor.execute(sqlselect,parameters)
        deleteconn.commit()

        usertype = comboLoading("UserTypes")
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"UserType.html",{'data': userProfile,'userTypes': usertype})


    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in deleting selected User Type.  "
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"UserType.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def update_userType(request):
    try:
        if request.method == 'POST':

            userID = request.session['uID']

            typeID = request.POST['typeID']
            name = request.POST['typename']
            desc = request.POST['description']

            userProfile = cursorUser("","","USER",int(userID),"")

            updateconn = glConnection()
            updatecursor = updateconn.cursor()

            if len(typeID) > 0:
                ## update selected departments 
                sqlselect = ("update tblUsertype set userType = %s,"
                    + "description = %s "
                    + "where  userTypeID = %s")
                parameters = (name,desc,int(typeID))
                updatecursor.execute(sqlselect,parameters)
                updateconn.commit()
            else:
                sqlselect = ("insert into tblUsertype(userType,description) values(%s,%s)")
                parameters = [(name,desc)]
                updatecursor.executemany(sqlselect,parameters)
                updateconn.commit()
                updateconn.close()

             ## Loading of departments
            usertypes = comboLoading("UserTypes")


        return render(request,"UserType.html",{'data': userProfile,'userTypes': usertypes})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in updating selected User Category."
        print(e)
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"UserType.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

### End of User Type

### Tickettype
def Tickettype(request):
    try:
            userID = request.session['uID']

            userProfile = cursorUser("","","USER",int(userID),"")
            tickettypes = comboLoading("TicketType")
            print("ticket success ")

            return render(request,"tickettype.html",{'data': userProfile,'tickettypes': tickettypes})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading Ticket Type."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"tickettype.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def load_tickettype(request,tickettypeID):
    try:
        userID = request.session['uID']

        conn = glConnection()
        varcursor = conn.cursor()

        #same parameters to all query
        
        sqlselect = ("select typeID,name, NULLIF(description,'-') as description from tblTicketType where typeID = %s "
            + "order by name")
        parameters = (int(tickettypeID),)
        varcursor.execute(sqlselect,parameters)

        selected = namedtuplefetchall(varcursor)

        userProfile = cursorUser("","","USER",int(userID),"")
        tickettypes = comboLoading("TicketType")

        conn.close()
        conn = None

        return render(request,"tickettype.html",{'data': userProfile,'tickettypes': tickettypes,'selected_tickettypes': selected})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in selecting Ticket Type."
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"tickettype.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def delete_tickettype(request,tickettypeID):
    try:

        userID = request.session['uID']

        conn = glConnection()
        varcursor = conn.cursor()

        sqlselect = ("delete from tblTicketType "
                + "where typeID = %s")
        parameters = (int(tickettypeID),)
        varcursor.execute(sqlselect,parameters)
        conn.commit()

        tickettypes = comboLoading("TicketType")
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"tickettype.html",{'data': userProfile,'tickettypes': tickettypes})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in deleting Ticket Type.  "
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"tickettype.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

    finally:
        conn.close()
        conn = None

def update_tickettype(request):
    try:
        if request.method == 'POST':

            userID = request.session['uID']

            typeID = request.POST['tickettypeID']
            name = request.POST['ticketname']
            desc = request.POST['description']

            userProfile = cursorUser("","","USER",int(userID),"")

            conn = glConnection()
            varcursor = conn.cursor()

            if len(typeID) > 0:
                ## update selected departments 
                sqlselect = ("update tblTicketType set name = %s,"
                    + "description = %s "
                    + "where  typeID = %s")
                parameters = (name,desc,int(typeID))
                varcursor.execute(sqlselect,parameters)
                conn.commit()

            else:
                sqlselect = ("insert into tblTicketType(name,description) values(%s,%s)")
                parameters = [(name,desc)]
                varcursor.executemany(sqlselect,parameters)
                conn.commit()
                

             ## Loading of departments
            tickettypes = comboLoading("TicketType")


        return render(request,"tickettype.html",{'data': userProfile,'tickettypes': tickettypes})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in updating selected Ticket Type."
        print(e)
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"tickettype.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})
    finally:
        conn.close()
        conn = None

### end of Tickettype

### Priority
def priority(request):
    try:
            userID = request.session['uID']

            userProfile = cursorUser("","","USER",int(userID),"")
            priority = comboLoading("Priority")

            return render(request,"priority.html",{'data': userProfile,'priorities': priority})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading Priority."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"priority.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def load_priority(request,priorityID):
    try:
        userID = request.session['uID']

        conn = glConnection()
        priocursor = conn.cursor()

        #same parameters to all query
        
        sqlselect = ("select priorityID,PriorityName, NULLIF(description,'-') as description from tblPriority where priorityID = %s "
            + "order by PriorityName")
        parameters = (int(priorityID),)
        priocursor.execute(sqlselect,parameters)

        selected = namedtuplefetchall(priocursor)

        userProfile = cursorUser("","","USER",int(userID),"")
        priorities = comboLoading("Priority")

        conn.close()
        conn = None

        return render(request,"priority.html",{'data': userProfile,'priorities': priorities,'selected_priorities': selected})
    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in selecting Priority."
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"priority.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def delete_priority(request,priorityID):
    try:
        userID = request.session['uID']

        conn = glConnection()
        varcursor = conn.cursor()

        sqlselect = ("delete from tblPriority "
                + "where  priorityID = %s")
        parameters = (int(priorityID),)
        varcursor.execute(sqlselect,parameters)
        conn.commit()

        priorities = comboLoading("Priority")
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"priority.html",{'data': userProfile,'priorities': priorities})


    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in deleting Priority.  "
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"priority.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

    finally:
        conn.close()
        conn = None

def update_priority(request):
    try:
        if request.method == 'POST':

            userID = request.session['uID']

            priorityID = request.POST['priorityID']
            name = request.POST['priorityname']
            desc = request.POST['description']

            userProfile = cursorUser("","","USER",int(userID),"")

            updateconn = glConnection()
            updatecursor = updateconn.cursor()

            if len(priorityID) > 0:
                ## update selected departments 
                sqlselect = ("update tblPriority set PriorityName = %s,"
                    + "description = %s "
                    + "where  priorityID = %s")
                parameters = (name,desc,int(priorityID))
                updatecursor.execute(sqlselect,parameters)
                updateconn.commit()
            else:
                sqlselect = ("insert into tblPriority(PriorityName,description) values(%s,%s)")
                parameters = [(name,desc)]
                updatecursor.executemany(sqlselect,parameters)
                updateconn.commit()
                updateconn.close()

             ## Loading of departments
            priorities = comboLoading("Priority")


        return render(request,"priority.html",{'data': userProfile,'priorities': priorities})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in updating selected Priority."
        print(e)
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"priority.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

### end of priority


### Ticket Type Status 
def tickettypestatus(request):
    try:
            userID = request.session['uID']

            userProfile = cursorUser("","","USER",int(userID),"")
            tickettypestatus = comboLoading("TicketStatus")

            return render(request,"tickettypestatus.html",{'data': userProfile,'tickettypestatus': tickettypestatus})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in loading Ticket Category Status."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"tickettypestatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

def load_tickettypestatus(request,ticketstatID):
    try:
        userID = request.session['uID']

        conn = glConnection()
        varcursor = conn.cursor()

        #same parameters to all query
        
        sqlselect = ("select statusID,statusName, NULLIF(description,'-') as description from tblTicketStatus where statusID = %s "
            + "order by statusName")
        parameters = (int(ticketstatID),)
        varcursor.execute(sqlselect,parameters)

        selected = namedtuplefetchall(varcursor)

        userProfile = cursorUser("","","USER",int(userID),"")
        tickettypestatus = comboLoading("TicketStatus")

        return render(request,"tickettypestatus.html",{'data': userProfile,'tickettypestatus': tickettypestatus,'selected_tickettypestatus': selected})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in selecting Ticket Type Status."
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"tickettypestatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})
    finally:
        conn.close()
        conn = None

def delete_tickettypestatus(request,ticketstatID):
    try:
        userID = request.session['uID']

        conn = glConnection()
        varcursor = conn.cursor()

        sqlselect = ("delete from tblTicketStatus "
                + "where  statusID = %s")
        parameters = (int(ticketstatID),)
        varcursor.execute(sqlselect,parameters)
        conn.commit()

        tickettypestatus = comboLoading("TicketStatus")
        userProfile = cursorUser("","","USER",int(userID),"")

        return render(request,"tickettypestatus.html",{'data': userProfile,'tickettypestatus': tickettypestatus})


    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in deleting Ticket Type Status."
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"tickettypestatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})

    finally:
        conn.close()
        conn = None

def update_tickettypestatus(request):
    try:
        if request.method == 'POST':

            userID = request.session['uID']

            tickettypestatusID = request.POST['ticketstatID']
            name = request.POST['tickettypename']
            desc = request.POST['description']
            dnow = datetime.datetime.now() 

            userProfile = cursorUser("","","USER",int(userID),"")

            updateconn = glConnection()
            updatecursor = updateconn.cursor()

            if len(tickettypestatusID) > 0:
                ## update selected departments 
                sqlselect = ("update tblTicketStatus set statusName = %s,"
                    + "description = %s,"
                    + "dateLastupdated = %s,"
                    + "updateBy = %s "
                    + "where statusID = %s")
                parameters = (name,desc,dnow,int(userID),int(tickettypestatusID))
                updatecursor.execute(sqlselect,parameters)
                updateconn.commit()
            else:
                sqlselect = ("insert into tblTicketStatus(statusName,description,dateLastupdated,updateBy) values(%s,%s,%s,%s)")
                parameters = [(name,desc,dnow,int(userID))]
                updatecursor.executemany(sqlselect,parameters)
                updateconn.commit()
                updateconn.close()

             ## Loading of departments
            tickettypestatus = comboLoading("TicketStatus")


        return render(request,"tickettypestatus.html",{'data': userProfile,'tickettypestatus': tickettypestatus})

    except Error as e:
        messagecontent = "Alert"
        error_message = " Error in updating selected Ticket Type Status."
        print(e)
        userProfile = cursorUser("","","USER",int(userID),"")
        return render(request,"tickettypestatus.html",{'data':userProfile,'messagecontent':messagecontent,'error_message': error_message})


### end of TicketStatus


def contact(request):
    return render(request,"contact.html")




### Ticket ( Assign user support and Priority )


### end of Ticket modules   

### reusable functions 
#bypass ORM 

## create a  reusable connection function
def cursorUser(username,password,str,uid,ticketID):

       # tusrcursor = cursor.MySQLCursor()

        try:
            mysqlDB = glConnection()
            #db_info = mysqlDB.get_server_info()
            tusrcursor = mysqlDB.cursor()

            if str == "LOGIN":
                #sqlselect = """select  * from tblUsers where username= %s and password = %s LIMIT 1"""
                sqlselect = ("SELECT tblusers.id,tblusers.name,tblUsertype.userType FROM DBTicket.tblusers "
                    + "INNER JOIN tblUsertype on tblusers.userTypeID = tblUsertype.userTypeID "
                    + "where tblusers.username = %s "
                    + "and tblusers.password = %s "
                    + "and tblusers.isApproved = 1 "
                    + "and tblusers.is_Active = 1 LIMIT 1")   
                tuple1 = (username,password)
                tusrcursor.execute(sqlselect,tuple1)
               # print(" Executing usrlogin")
            elif str == "USER":
                sqlselect = ("SELECT tblusers.id,tblusers.name,tblUsertype.userType,"
                        + "tblusers.username,tblusers.password,tblusers.email,"
                        + "tblusers.departmentid,tblusers.is_active,tblusers.positionID,tblusers.userTypeID,"
                        + "tblusers.isApproved "
                        + "FROM DBTicket.tblusers "
                        + "INNER JOIN tblUsertype on tblusers.userTypeID = tblUsertype.userTypeID "
                        + "where tblusers.id = %s "
                        + "and tblusers.is_Active = 1 "
                        + "and tblusers.isApproved = 1")   
                tuple1 = (int(uid),)
                tusrcursor.execute(sqlselect,tuple1)


            elif str == "ticketSelected":
                sqlselect = ("select  * from tblTickets where ticketID = %s " 
                    + "and createdby = %s")
                tuple1 = (int(ticketID),int(uid))
                tusrcursor.execute(sqlselect,tuple1)
                

            elif str == "tickets":
                sqlselect = ("select  * from tblTickets where ticketID = %s ")
                tuple1 = (int(ticketID),)
                tusrcursor.execute(sqlselect,tuple1)
            
            elif str == "UserTicket":

                sqlselect = ("SELECT tblTickets.ticketID, tblTickets.title,tblTickets.description,tblTicketType.name " 
                    + "FROM DBTicket.tblTickets "
                    + "INNER JOIN tblTicketType "
                    + "ON tblTickets.tickettypeID = tblTicketType.typeID " 
                    + "where tblTickets.createdby = %s "
                    + "order by tblTickets.title")
                tuple1 = (int(uid),)

                tusrcursor.execute(sqlselect,tuple1)


            elif str == "LoadUsersAssign":
                sqlselect =("select  tblUsers.id,tblUsers.name,tblUsertype.userType from tblUsers "
                    + "INNER JOIN tblUsertype "
                    + "ON tblUsers.userTypeID = tblUsertype.userTypeID "
                    + "where tblUsertype.userType <> 'User' "
                    + "and tblUsertype.userType <> 'Admin' "
                    + "order by tblUsertype.userType")
                tusrcursor.execute(sqlselect)
                
            elif str == "LoadPriority":
                sqlselect = ("SELECT tblPriority.priorityID,tblPriority.PriorityName FROM DBTicket.tblPriority "
                    + "ORDER BY tblPriority.PriorityName")                
                tusrcursor.execute(sqlselect) 

            elif str == "Open":
              
                sqlselect = ("SELECT count(tblTickets.ticketID) as open "
                    + "FROM DBTicket.tblTickets "
                    + "inner join tblTicketType "
                    + "on tblTickets.tickettypeID = tblTicketType.typeID "
                    + "Left join tblPriority "
                    + "on tblTickets.priorityID = tblpriority.priorityid "
                    + "left join tblUsers "
                    + "on tblTickets.assignUserID = tblUsers.ID "
                    + "LEFT JOIN tblTicketStatus "
                    + "ON tblTickets.statusID = tblTicketStatus.statusID "
                    + "LEFT JOIN tblUsertype "
                    + "ON tblUsers.userTypeID=tblUsertype.userTypeID "
                    + "where tblTickets.statusid = '1' ")
                   # + "and (tblTickets.createdby = %s or tblTickets.assignuserid = %s)")   
                strval = (int(uid),int(uid))          
                tusrcursor.execute(sqlselect)

            elif str == "Close":
                sqlselect = ("SELECT count(tblTickets.ticketID) as close "
                    + "FROM DBTicket.tblTickets "
                    + "inner join tblTicketType "
                    + "on tblTickets.tickettypeID = tblTicketType.typeID "
                    + "Left join tblPriority "
                    + "on tblTickets.priorityID = tblpriority.priorityid "
                    + "left join tblUsers "
                    + "on tblTickets.assignUserID = tblUsers.ID "
                    + "LEFT JOIN tblTicketStatus "
                    + "ON tblTickets.statusID = tblTicketStatus.statusID "
                    + "LEFT JOIN tblUsertype "
                    + "ON tblUsers.userTypeID=tblUsertype.userTypeID "
                    + "where tblTickets.statusid = '2' ")
                    #+ "and (tblTickets.createdby = %s or tblTickets.assignuserid = %s)")   
                strval = (int(uid),int(uid))         
                tusrcursor.execute(sqlselect)

            elif str == "RemarkDetails":
                sqlselect = ("SELECT tblTickets.ticketID,tblTicketDetails.detailID,"
                    + "tblTickets.startdate as Start,tblTickets.enddate as End,"
                    + "tblusers.name,tblTicketDetails.remark,"
                    + "date_format(tblTicketDetails.datecreated,'%m/%d/%Y') As Date  FROM DBTicket.tblTickets " 
                    + "INNER JOIN DBTicket.tblTicketDetails "
                    + "ON DBTicket.tblTickets.ticketID = DBTicket.tblTicketDetails.ticketID "
                    + "INNER JOIN DBTicket.tblusers "
                    + "ON DBTicket.tblTicketDetails.createdBy = DBTicket.tblusers.ID "
                    + "WHERE tblTickets.ticketID= %s "
                    + "ORDER BY tblTicketDetails.datecreated")
                strval = (int(ticketID),)         
                tusrcursor.execute(sqlselect,strval)
            return namedtuplefetchall(tusrcursor)

        except Error as e:
            print("Error while connecting to MySQL (cursorfunc) --> ", e)
            return None

        finally:
            mysqlDB.close()
            mysqlDB=None

def comboLoading(str):
    try:
        regsconn = glConnection()
            #db_info = regsconn.get_server_info()

        regscursor = regsconn.cursor()

        if str == "Department":

            sqlDepartment = """select deptid,departmentName,NULLIF(description,'-') as description from tblDepartments order by departmentName"""
            regscursor.execute(sqlDepartment)
            irec = namedtuplefetchall(regscursor)
        
        elif str == "ListofUsers":
            sqlstatement = ("SELECT tblusers.id,username,email,name,is_Active,isApproved,tblDepartments.departmentName, "
                + "tblPositions.positionName,tblUsertype.userType FROM DBTicket.tblusers "
                + "INNER JOIN tblDepartments ON "
                + "tblusers.departmentID = tblDepartments.deptid "
                + "INNER JOIN tblPositions ON "
                + "tblusers.positionID = tblPositions.id "
                + "INNER JOIN tblUsertype ON "
                + "tblusers.userTypeID = tblUsertype.userTypeID")	  
            regscursor.execute(sqlstatement)
            irec = namedtuplefetchall(regscursor)

        elif str == "Position":
            sqlPositions = """select id,positionname,NULLIF(description,'-') as description from tblPositions order by positionName"""
            regscursor.execute(sqlPositions)
            irec = namedtuplefetchall(regscursor)

        elif str == "UserType":
            sqluserType = ("SELECT userTypeID,userType,NULLIF(description,'-') as description FROM DBTicket.tblUsertype "
                + "where tblUsertype.userType <> 'Admin' "
                + "ORDER BY userType")
            regscursor.execute(sqluserType)
            irec = namedtuplefetchall(regscursor)

        elif str == "UserTypes":
            sqluserType = ("SELECT userTypeID,userType,NULLIF(description,'-') as description FROM DBTicket.tblUsertype "
                + "ORDER BY userType")
            regscursor.execute(sqluserType)
            irec = namedtuplefetchall(regscursor)

        elif str == "TicketType":
            sqluserType = ("SELECT typeID,name,NULLIF(description,'-') as description FROM DBTicket.tblTicketType "
                + "ORDER BY name")
            regscursor.execute(sqluserType)
            irec = namedtuplefetchall(regscursor)
        
        elif str == "Ticket":
            sqlselect = """select  * from tblTicketType ORDER BY NAME"""
            #tuple1 = (int(uid),)
            regscursor.execute(sqlselect)
            irec = namedtuplefetchall(regscursor)

        elif str == "Priority":
            sqluserType = ("SELECT priorityID,PriorityName,NULLIF(description,'-') as description FROM DBTicket.tblPriority "
                + "ORDER BY PriorityName")
            regscursor.execute(sqluserType)
            irec = namedtuplefetchall(regscursor)
        
        elif str == "TicketStatus":
            sqluserType = ("SELECT statusID,statusName,NULLIF(description,'-') as description FROM DBTicket.tblTicketStatus "
                + "ORDER BY statusName")
            regscursor.execute(sqluserType)
            irec = namedtuplefetchall(regscursor)

        return irec 

        
    except Error as e:
        print("Error in combo : " + e)

def dictfetch(cursor):
    desc = cursor.description
    return [
        Dict(zip(col[0] for col in desc), row)
        for row in cursor.fetchall()
    ]

def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

### end of reusable function 

### User Registration and login 

def usrlogin(request):

    try:
        if request.method == 'POST':
        # username = request.POST.get('username') same lang sa baba
            myuser = request.POST['username']
            mypass = request.POST['password']
            error_message = "Invalid username or password"

            try:
                usrrec = cursorUser(myuser,mypass,"LOGIN",0,"")
                print(usrrec)
                for row in usrrec:
                    #print(row[0])
                    request.session['name'] = row[1]
                    request.session['uID'] = row[0]
                    request.session['userType'] = row[2]
                    request.session.modified = True

                if len(usrrec) > 0:
                    #
                    return render(request,"index.html", {'data' : usrrec})
                else:
                    return render(request,"login.html", {'data' : usrrec,'error_message': error_message})
                    #return HttpResponse('Rango says: since you are not authenticated')
            
            except Error as e:
                print(" Error in usrlogin --> ", e)
                error_message = " Error in Login, Pls. contact IT Support"
                return render(request,"login.html", {'data' : usrrec,'error_message': error_message})
        else:
            return render(request,"index.html")
    except Error as e:
        error_message = " Error in Login, Pls. contact IT Support"
        return render(request,"login.html", {'data' : usrrec,'error_message': error_message})

def loadregister(request):
    #if request.method == 'POST':
        try:

            #userID = request.session['uID']
            
            deptrec = comboLoading("Department")

            postrec = comboLoading("Position")
            
            userType = comboLoading("UserType")

            #if userID == 0:
            return render(request,"register.html", {'departments' : deptrec, 'positions': postrec,'userType': userType })
            #else:
            #    userinfo = cursorUser("","","USER",int(userID))
            #    return render(request,"updateuser.html", {'departments' : deptrec, 'positions': postrec,'userType': userType,'data': userinfo})

        except Error as e:
            print(" User not Authorized --> ", e)

def updateRegister(request):
    
    if request.method == 'POST':

        print("start update")
        
        try:
            userID = request.session['uID']
            # variables from register.html
            strusername = request.POST['username']
            strpassword = request.POST['password']
            stremail = request.POST['email']
            strdisplay = request.POST['display']
            deptid = request.POST['depid']
            posid = request.POST['posid']
            iusertypeid = request.POST['usertype']
            iActive = "1"

            updateregsconn = glConnection()
            regscursor = updateregsconn.cursor()

            sqlDepartment = ("UPDATE tblUsers set username = %s, "
                        + "password = %s, "
                        + "email = %s, "
                        + "name = %s, "
                        + "is_Active = %s, "
                        + "departmentID = %s, "
                        + "positionID = %s, "
                        + "userTypeID = %s "
                        + "where id = %s")
            rec = [( strusername,strpassword,stremail,strdisplay,iActive,deptid,posid,iusertypeid,userID)]

            regscursor.executemany(sqlDepartment,rec)
            updateregsconn.commit()
            updateregsconn.close()
            updateregsconn=None

            userType = request.session['userType']

            TicketStat = LoadTicketstatus(userID,userType)

            rec = cursorUser("","","USER",int(userID),"")
            
            if len(rec) > 0:

                return render(request,"ticketstatus.html",{'data' : rec,'ticketstat': TicketStat })
            else:

                return HttpResponse('No Users in Ticket')

        except Error as e:
            print(e)

def saveRegister(request):

    if request.method == 'POST':

        userID = request.session['uID']

        # variables from register.html
        strusername = request.POST['username']
        strpassword = request.POST['password']
        stremail = request.POST['email']
        strdisplay = request.POST['display']
        deptid = request.POST['depid']
        posid = request.POST['posid']
        iusertypeid = request.POST['usertype']
        iActive = "1"

        try:
            saveregsconn = glConnection()

            #insert values to tblUsers
            regscursor = saveregsconn.cursor()



            sqlDepartment = "insert into tblUsers(username,password,email,name,is_Active,departmentID,positionID,userTypeID) values (%s,%s,%s,%s,%s,%s,%s,%s);"
            rec = [(strusername,strpassword,stremail,strdisplay,iActive,deptid,posid,iusertypeid)]

            regscursor.executemany(sqlDepartment,rec)
            saveregsconn.commit()
            saveregsconn.close()

            saveregsconn=None

            return render(request,"login.html")


        except Error as e:
            print(" Error in Save Register --> ", e)
        finally:
            # Do nothing
            print(" Save Register MySQL connection is closed")

def loadselectedUser(request):
    try:
        userID = request.session['uID']
        userType = request.session['userType']

       # TicketStat = LoadTicketstatus(userID,userType)

        deptrec = comboLoading("Department")

        postrec = comboLoading("Position")
            
        userType = comboLoading("UserType")

        rec = cursorUser("","","USER",int(userID),"")

        if len(rec) > 0:
            
            return render(request,"updateuser.html",{'data' : rec,'departments' : deptrec, 'positions': postrec,'userType': userType })
        else:

            return HttpResponse('Error in loading selected users')


    except Error as e:
        print()

### end of Registration and login

def loadUserProfile(request):
    try:

        userID = request.session['uID']
        userinfo = cursorUser("","","USER",int(userID),"")

        return render(request,"user.html", {'data' : userinfo})
        print()
    except Error as e:
        print()


