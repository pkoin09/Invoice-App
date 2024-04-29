# INVOICE APP

## [Video Demo](https://youtu.be/s51mmgBzb-I)

### Description

This repository is for an "invoice app" that allows users to list services and generate PDF invoices based on time. It helps users keep track of services and generate invoices that may be sent to clients. This is beneficial for freelancers who are starting out and on a budget.

P.S: _App was developed as a final project for Harvard University's CS50. It serves as a proof-of-concept and showcases the skills and knowledge gained during the program. However, please note that it is not a fully-fledged, real-life project. The codebase may contain imperfections and inefficiencies typical of a student project._

### Table of Contents (Optional)

- [INVOICE APP](#invoice-app)
  - [Video Demo](#video-demo)
  - [Description](#description)
  - [Table of Contents (Optional)](#table-of-contents-optional)
  - [Install](#install)
  - [Usage](#usage)
  - [Permissions](#permissions)
  - [Files](#files)
  - [Templates Folder](#templates-folder)
  - [Static Folder](#static-folder)
  - [Output folder](#output-folder)
  - [Python files.](#python-files)
  - [Requirements](#requirements)
  - [Credits](#credits)
  - [License](#license)

#### Install

To minimize potential conflicts, it is suggested to install the required libraries (dependencies) within a virtual environment. This isolation allows for a consistent and controlled development environment.

- Create the virtual env
  `python3 -m venv venv`
  I used 'python3' and 'pip3' for this project, but i believe 'python' and 'pip' would work as well. The last 'venv' is the name of the virtual environment, can be any name.
- Activate the venv
  `source venv/bin/activate`
- Install the requirements
  `pip3 install -r requirements.txt`
- check all are installed
  `pip3 freeze`

#### Usage

To start using the app, run
`flask run`
Register for an account. The first user has root admin privileges, while the rest of the users have default permissions. Admins can change permissions for users from "default" to either "staff" or "super". The root admin permissions cannot be changed, otherwise there is a risk of being locked out of the app if no other admins exist.

After you are registered, add services under the 'Manage My Services' page. They will now be shown to new users (clients).
If/when a client books an appointment, booking details will be shown in the 'Dashboard' page. See video demo for more info.

P.S.
The App is currently set to use in-memory database ":memory:" so as to clear cache after use and will help in saving space. It can be changed in file 'app.py' line #38 to "invoice.db" (or any name) to allow storage. User's session might also be cleared after PDF creation while using the in-memory db. If so, you would need to re-register.

#### Permissions

1. Super
   Admin-level permission. Can change permission levels, view own dashboard, create services to offer, book services, and create invoices.

2. Staff
   Can do everything the admin can do, but cannot change user permissions.

3. Default
   Can book services only. Can only be done after registration.

#### Files

##### Templates Folder

1. Register.html
   Allows the user to register for an account with default permission unless the user is the very first one. Username, password and a confirmation password are required. Redirects to login if successful.
2. Login.html
   Authenticates user view access is granted by permission level. Redirects to booking page.
3. Booking.html
   Gives a view of all the services offered by all staff and admins. Users can then book a service from here. The Attaches (service provider) name is also shown here. Attaches name cannot be changed, as the preferred staff may not have the experience or know-how to provide the chosen service. Redirects to thanks.
4. Thanks.html
   Success confirmation for booking the service. The service status is then marked as booked.
5. Dashboard.html
   Shows the services offered by the logged-in admin/staff. It has three sections. - Upcoming appointments - In progress - Invoiced

On upcoming appointments, hours are edited per service in a modal. This design choice was made to gain the user's attention to prevent mistakes at the cost of multiple clicks. Service status is updated from 'booked' to 'in progress'. This design choice assumes not all services are paid per service, bi-weekly, or monthly, etc. Redirects to the invoice preview. 6. Invoice.html
Provides a preview of clients items, totals, and sub-total that the signed-in staff or admin provides as services. Users can then select the client from the drop-down and then click the 'create invoice' button to generate an invoice PDF. The dropdown is in case there are multiple clients. Selecting one would filter items per client. On invoice generation, the service status is marked as 'complete'. 7. Admin.html
A page for admin users to change user permissions. 8. Apology.html
A helper page that displays errors in a memegen image. 9. Layout.html
Contains the default head section, navigation, logo, and footer in one file to avoid repetition.

##### Static Folder

1. Styles.css
   Main invoice app styling.
2. Invoices.css
   Contains the invoice PDF styling.
3. Script.js
   Contains the JS scripts for modals used, filtering tables by value, and adding up the subtotal of the invoice.

#### Output folder

1. invoice.pdf
   Contains a copy of the last PDF to be run.

##### Python files

1. App.py
   Main file containing all the app's logic.
2. Helpers.py
   Contains helper files for memegen creation, error handling, currency conversion, and a decorator function for routing users to the login page if the user has no 'user_id' in session (not logged in).

##### Requirements

1. requirements.txt
   Lists libraries required by the app.

#### Credits

1. [CS50](https://cs50.harvard.edu): layout, helpers
2. [Weasyprint](https://weasyprint.org): invoice PDF styling.

#### License

Licensed under the general [MIT license](./LICENSE.md).
