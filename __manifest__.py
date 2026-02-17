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
    "reports/reservation_report.xml",
    "reports/repport_template.xml",
    "wizards/reservation_report_wizard_view.xml",
    "views/reservation_views.xml",

    "views/reservation_menus.xml",
]

}

