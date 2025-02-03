# Ticketing System

Welcome to the **Ticketing System** project! 🎟️ This application allows users to manage, create, and resolve support tickets. It's designed to improve customer service operations and streamline workflows.

This repository contains the development version of the system, which is actively being worked on and improved.

---

## Features 🚀

- **Create Tickets**: Users can submit tickets with descriptions of their issues.
- **View Tickets**: View active, closed, and pending tickets.
- **Assign Tickets**: Support agents can be assigned tickets for resolution.
- **Ticket Management**: Prioritize, update, and resolve tickets.
- **User Authentication**: Secure login system for users and admins.

---

## Development Setup ⚙️

### Prerequisites

Ensure you have the following software installed on your machine:

- **- Python 3.9+** (LTS version recommended)  

[//]: # (  Download: [https://nodejs.org/]&#40;https://nodejs.org/&#41;)

[//]: # (  )
[//]: # (- **npm** &#40;Node Package Manager&#41;  )

[//]: # (  Should be included with Node.js installation.)

[//]: # ()
[//]: # (- **Database**  )

[//]: # (  - This project uses [MongoDB]&#40;https://www.mongodb.com/&#41;. Set up a local or cloud instance, such as MongoDB Atlas.)

### Clone the Repository

Start by cloning this repository to your local machine:

```bash
git clone https://github.com/FArooghOghba/TicketingSystem.git
```

### Switch to the Development Branch

Since you're working on the **development branch**, be sure to check out that branch:

```bash
git checkout development
```

### Set up virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate  # Windows

### Install Dependencies
Navigate into the project folder and install the necessary dependencies:

```bash
pip install -r requirements/dev_requirements.txt
```

### Set up Environment Variables

Create a `.env` file in the root directory and set the necessary environment variables for your project. Below is an example `.env` setup:

```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:password@localhost/ticketing
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```
---

## Running the Application 🚀

### Start the Backend Server

Once everything is set up, start the backend server using:

```bash
python src/manage.py runserver
```

The server will run on [http://localhost:8000](http://localhost:5000) by default. 

---

## API Documentation 📚

The Ticketing System exposes several RESTful endpoints for interacting with tickets. Below is a quick overview of the available API routes.

### **Authentication**

#### POST `/api/auth/login`
Login for users and admins.

Request Body:
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

#### POST `/api/auth/register`
Register a new user (Admin or Support Agent).

Request Body:
```json
{
  "name": "John Doe",
  "email": "user@example.com",
  "password": "your_password",
  "role": "customer" // or "admin"
}
```

### **Tickets**

#### GET `/api/tickets`
Get all tickets.

#### GET `/api/tickets/:id`
Get a specific ticket by ID.

#### POST `/api/tickets`
Create a new ticket.

Request Body:
```json
{
  "title": "Issue with system",
  "description": "Details about the issue",
  "priority": "high"
}
```

#### PUT `/api/tickets/:id`
Update ticket details (e.g., assign to an agent).

#### DELETE `/api/tickets/:id`
Delete a specific ticket.

---

## Contributing 🛠️

We welcome contributions to improve this ticketing system! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new feature branch: `git checkout -b feature/your-feature-name`.
3. Make your changes.
4. Commit your changes: `git commit -am 'Add new feature'`.
5. Push to the branch: `git push origin feature/your-feature-name`.
6. Open a pull request.

### Guidelines

- Write clear commit messages.
- Ensure that your code follows the existing coding style.
- Include tests for new features or bug fixes.
- If adding a new feature, please update this README with instructions.

---

## License 📜

This project is licensed under the MIT License – see the [LICENSE](LICENSE) file for details.

---

## Contact ✉️

For any questions or suggestions, feel free to reach out via:

- Email: [faroogh.oghba@gmail.com](mailto:your-email@example.com)
- GitHub: [https://github.com/FArooghOghba](https://github.com/FArooghOghba)

---

## Acknowledgements 💡

Special thanks to all the contributors and the open-source community for their amazing work and support!

---

Feel free to adjust any of the details above according to your specific setup and workflows.