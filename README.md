# BuzzBox Email Service
BuzzBox is a modern, scalable email service platform built on top of Poste.io, implementing a microservice clean architecture using FastAPI. By leveraging Poste.io's powerful mail server capabilities, BuzzBox extends its functionality with advanced user management, security features, and comprehensive administration tools.

## About Poste.io Integration
Poste.io serves as the core mail server infrastructure, providing:

- Reliable SMTP, IMAP, and POP3 services
- Built-in spam protection
- TLS encryption
- Domain management
- Mail queue management

## 🌟 Features
### Email Management
- Send and receive emails with multiple attachments
- Organized inbox and sent box management
- Contact list management
- File attachment support
- User-friendly email composition interface

### User Features
- Customizable user profiles with profile pictures
- Status indicators (e.g., "A 21 yo developer.")
- Contact management system
- Recovery email setup
- User reporting system
- Profile information updates  

### Security & Authentication
- Secure password management

- Password reset functionality
     - Forgot password recovery
     - Password change option


- IAM (Identity and Access Management) core service
- Recovery email system
### Administration

- Admin panel with comprehensive reporting
- User management and moderation
- Ban/suspension system
- Report handling system

## 🏗️ Architecture
### Microservices
- IAM Service: Handles authentication and authorization
- Email Core Service: Manages email operations
- Media Service: Handles file and media management

## Technology Stack
- ### Backend Framework: FastAPI
- ### Databases:
- PostgreSQL: Primary relational database
- MongoDB: Document storage for email attachments and profile pictures
- ### Email Server: Poste.io
- ### Architecture Pattern: Clean Architecture
