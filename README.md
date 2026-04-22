# GoFundMe Connect

## Smart University Funding Platform

GoFundMe Connect is a comprehensive web application designed to bridge the gap between university students in need of financial support and potential sponsors. This platform facilitates transparent and efficient funding opportunities, particularly for students at the University of Zululand.

## Features

### For Students
- **Secure Registration**: Students can register using their official university email (@stu.unizulu.ac.za)
- **Funding Applications**: Apply for SRC (Student Representative Council) funding and external sponsorships
- **Dashboard**: Track application status and funding opportunities
- **Profile Management**: Update personal and academic information

### For Sponsors
- **Organization Registration**: Sponsors can create accounts and specify their organization
- **Funding Opportunities**: Browse and support student applications
- **Dashboard**: Manage sponsored projects and track contributions

### For Administrators
- **System Management**: Oversee all users, applications, and funding opportunities
- **Funding Creation**: Post new SRC and external funding opportunities
- **Application Review**: Manage and approve student applications
- **Reporting**: Monitor platform usage and funding distribution

### Key Features
- **JWT Authentication**: Secure token-based authentication for all user roles
- **Payment Integration**: Support for PayPal and PayFast payment gateways
- **Email Notifications**: Automated email communication for important updates
- **Responsive Design**: Mobile-friendly interface for all devices
- **Real-time Updates**: Live tracking of application and funding status

## Technology Stack

### Backend
- **Flask**: Python web framework for API development
- **MySQL**: Relational database for data storage
- **JWT**: JSON Web Tokens for secure authentication
- **Flask-CORS**: Cross-origin resource sharing support

### Frontend
- **HTML5/CSS3**: Modern responsive web design
- **JavaScript**: Client-side interactivity
- **Jinja2**: Server-side templating

### External Services
- **PayPal SDK**: Payment processing integration
- **Gmail SMTP**: Email notification service

## Installation

### Prerequisites
- Python 3.8 or higher
- MySQL Server
- Git

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/LindiweNolwazi/FinalYearProject.git
   cd FinalYearProject
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Database Setup**
   - Create a MySQL database named `Final_Year_Project`
   - Update database credentials in `db_config.py` and `app.py`
   - Run the schema creation scripts (if provided)

5. **Configure Payment Gateways**
   - Update PayPal credentials in `app.py`
   - Configure PayFast settings if using

6. **Email Configuration**
   - Update Gmail SMTP settings in `app.py` (use app passwords for security)

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Access the application**
   - Open your browser and navigate to `http://localhost:5000`

## Database Schema

The application uses the following main tables:
- `students`: Student user information and profiles
- `sponsors`: Sponsor organization details
- `admins`: Administrative user accounts
- `funding_opportunities`: Available funding programs
- `applications`: Student funding applications

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login

### Funding
- `GET /funding/list` - List all funding opportunities
- `GET /funding/src` - SRC funding opportunities
- `GET /funding/external` - External sponsorship opportunities

### Applications
- `GET /student/applications` - Student's applications
- `POST /student/apply` - Submit funding application

### User Management
- `GET /student/profile` - Get student profile
- `PUT /student/profile` - Update student profile

## Usage

1. **Student Registration**: Students register with university email and complete profile
2. **Browse Opportunities**: View available SRC and external funding
3. **Submit Applications**: Apply for relevant funding opportunities
4. **Track Progress**: Monitor application status through dashboard
5. **Sponsor Engagement**: Sponsors can review and fund approved applications

## Security Features

- Password hashing with SHA-256
- JWT token authentication with expiration
- Role-based access control
- Input validation and sanitization
- SQL injection prevention
- CORS protection

## Development

### Project Structure
```
FinalYearProject/
├── app.py                 # Main Flask application
├── db_config.py          # Database configuration
├── create_admin.py       # Admin user creation script
├── update_schema.py      # Database schema updates
├── requirements.txt      # Python dependencies
├── static/               # Static assets (CSS, JS, images)
├── templates/            # HTML templates
└── README.md            # Project documentation
```

### Running Tests
```bash
# Add test commands if implemented
pytest
```

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is developed as part of a final year project at the University of Zululand.

## Contact

For questions or support, please contact the development team.

## Acknowledgments

- University of Zululand for providing the project context
- Flask community for the excellent web framework
- All contributors and testers</content>
<parameter name="filePath">d:\pictures\GoFundMe Connect\README.md