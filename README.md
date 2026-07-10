# Blogsphere
A feature-rich blogging platform built with Django.<br>
This project was originally developed during my Django learning journey and later refactored,<br> 
documented, and improved as part of my portfolio.


## Features

### Authentication & User Management
- Custom User Model
- Registration & Login
- User Profiles
- Edit Profile
- Role-Based Access


### Blogging System
- Create Posts
- Edit Posts
- Delete Posts
- Draft Support
- Published Posts
- Post Moderation Workflow


### Author System
- Author Request Submission
- Request Review by Admin
- Approve / Reject Requests
- Email Notifications


### Social Features
- Follow / Unfollow Users
- User Followers & Following Lists
- Post Likes
- Saved Posts


### Comment System
- Nested Comments
- Multi-level Replies
- Comment Moderation


### Dashboard
- Admin Dashboard
- Author Dashboard
- User Dashboard


### Search
- Search Posts
- Author Post Listing


### Notifications
- Email Notifications
- Post Deletion Alerts


### Technical Features
- Django Signals
- AJAX / Fetch API
- Custom Template Tags
- CKEditor5 Integration
- Media Uploads


## Technologies Used
- Python
- Django
- SQLite
- HTML
- CSS
- JavaScript
- CKEditor5
- Bootstrap


## Project Structure
`/accounts`<br>
`/blog`<br>
`/config`<br>
`/media`<br>
`/static`<br>
`/templates`


## Installation
Clone the repository:
```bash
git clone https://github.com/QUANTORIS01/blogsphere.git
```


Create virtual environment:
```bash
python -m venv .venv
```


Activate environment:
```bash
source .venv/bin/activate
```


Install Dependencies:
```bash
pip install -r requirements.text
```


Run migrations:
```bash
python manage.py migrate
```


Run server:
```bash
pyhton manage.py runserver
```


## Learning Objectives
```markdown
This project was built as a practical Django learning project.
The main goal was to gain hands-on experience with:

- Django Models
- Views
- Forms
- Authentication
- Authorization
- Signals
- Template Tags
- AJAX
- Email Handling
- Role Management
- Content Moderation
```


## Future Improvements
- Real-time notifications
- REST API
- Async tasks with Celery
- Advanced search
- Docker support
- PostgreSQL support


## Author
Developed by QUANTORIS