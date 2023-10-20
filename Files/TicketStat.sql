SELECT ticketID,title,description,createdby,cast(datecreated as Date) as nDate,cast(startdate as Date) as Sdate,cast(enddate as Date) as Edate,statusID,tickettypeID,
assignuserid, TblUsers.name as Username,tblTicketType.name as Category,tblTickets.priorityID,tblpriority.priorityname
FROM DBTicket.tblTickets
inner join tblTicketType
on tblTickets.tickettypeID = tblTicketType.typeID
Left join tblPriority
on tblTickets.priorityID = tblpriority.priorityid
left join tblUsers 
on tblTickets.assignUserID = tblUsers.ID
where createdby = '10'
and statusid = '1';
