# inventory-management
This is a inventory management system

# How to Setup
1. Clone Project
```
git clone https://github.com/sajib1066/inventory-management.git
```

2. Go To Project Directory
```
cd TicketingProject
```
3. Create Virtual Environment
```
python3 -m venv Ticketingenv
```
4. Active Virtual Environment
```
source Ticketingenv/bin/activate
```
5. Install Requirements File
```
pip install -r requirements.txt
```
6. Migrate Database
```
python manage.py migrate
```
7. Create Super User
```
python manage.py createsuperuser
```
8. Run Project
```
python manage.py runserver
```

9. Next To do
```
    1.) update Create ticket same as departments or position - done

    2.) separate the ticket status for IT Part against user
            - working on ticket status 
                - common users - done
                - Support , Service Desk , Admin -- working on myactivity module ( start and end date and remarks ) - Done
                - update the activity - working 

    3.) new UI for IT Part to update the date start and end
    4.) new UI and tables regarding ticket details responses by IT against user response ( like chat    box type)
    5.) new UI for user to update the close ticket 
```
