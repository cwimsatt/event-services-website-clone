# Event Services Website

A dynamic event services website featuring a media portfolio system with content management capabilities. The platform implements a portfolio gallery with category filtering and float-based sequence sorting for precise content ordering, alongside an events display system with responsive image optimization.

## Key Features

- Flask web framework with Flask-Admin CMS integration
- Portfolio gallery with category management system
- Event showcase with float-based sequence sorting (3 decimal precision)
- Responsive image optimization
- Data migration framework for sequence management
- Structured site navigation system

## Tech Stack

- **Backend**: Python/Flask
- **Database**: PostgreSQL
- **Frontend**: HTML5, CSS3, JavaScript
- **CMS**: Flask-Admin
- **Image Processing**: Pillow
- **Version Control**: Git

## Project Structure

```
├── instance/               # Instance-specific files
├── migrations/            # Database migrations
├── static/               # Static files (CSS, JS, images)
│   ├── css/
│   ├── images/
│   ├── js/
│   └── uploads/
├── templates/            # HTML templates
│   ├── admin/           # Admin panel templates
│   └── ...              # Main site templates
└── ...
```

## Setup and Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables
4. Initialize the database:
   ```bash
   flask db upgrade
   ```
5. Run the application:
   ```bash
   python main.py
   ```

## Development

- The project uses Flask-Migrate for database migrations
- Static files are organized in the static directory
- Templates follow a modular structure
- Admin interface is accessible at /admin

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
