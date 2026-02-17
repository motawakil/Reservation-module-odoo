{
"name" : "Reservation",
"version" : "1.0",          
"depends" : ['base', 'mail','sale', 'product','portal','website'],
"author" : "Motaouakel",
"summary" : "Manage reservations",
"description" : "A module to manage reservations.",         
"category" : "Uncategorized",       
"application" : True,
"installable": True,
"data": [
    'security/security.xml',
    'security/ir.model.access.csv',
    "data/reservation_actions.xml" ,
    "data/sequence_reservation.xml",
    "repport/reservation_report_templates.xml",
    "repport/reservation_report.xml",
    "views/reservation_views.xml",
    "views/reservation_menus.xml",
]

}

