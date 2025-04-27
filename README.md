## **How to Run the Project**
1. Clone the Repository
2. Open your terminal and run:
   ```bash
   docker compose up
   ```

## **BNPL Payment Plan Simulator: Backend Technical Plan**
The rest document outlines the technical specifications and design decisions for the Django backend, updated to use a custom User model.

### **1\. Assumptions**

* **Core Tech:** PostgreSQL DB, Django/DRF framework, JWT authentication.  
* **Roles:** 'Merchant' and 'User' roles defined by a role field on a custom User model.  
* **Logic:**   
  * Installments are equal monthly payments. Default currency 'ريال'.  
  * Plans are unique per client (can’t be reused).  
  * All merchants can see all users.  
  * A user can’t be both a merchant and a user.  
* **Environment:** Docker/Docker Compose for services (Backend, DB, Frontend). Standard error handling (HTTP codes/JSON).  
* **Security (MitM):** MitM attack prevention is out of scope for dev testing; deployment **requires** HTTPS.  
* **Frontend:** A single React application will serve both user roles (merchants and users).

### **2\. Database Models (models.py)**

We will use Django's ORM with the following models:

| Model | Fields | Description |
| :---- | :---- | :---- |
| User | Extends AbstractBaseUser & PermissionsMixin. Includes email (unique, used as USERNAME\_FIELD), is\_active (BooleanField, default True), is\_staff (BooleanField, default False). **Adds ROLE\_CHOICES \= \[('merchant', 'Merchant'), ('user', 'User')\], role (CharField, choices=ROLE\_CHOICES).** Manages user accounts.  | **Custom User model** (lives in accounts app). Email is the unique identifier. The role field directly defines if the user is a 'Merchant' or 'User'. Requires a custom UserManager to handle user creation (especially create\_superuser). |
| PaymentPlan | merchant (**ForeignKey to settings.AUTH\_USER\_MODEL**, limit\_choices\_to={'role': 'merchant'}), user\_id (EmailField), total\_amount (DecimalField), number\_of\_installments (IntegerField), start\_date (DateField), status ('Active'/'Paid'), created\_at, updated\_at | (Lives in plans app) Represents a BNPL plan. **Crucially, merchant FK now points to the custom User model (settings.AUTH\_USER\_MODEL) and limits choices based on the role field.** Status updates automatically via Signals. |
| Installment | plan (ForeignKey to PaymentPlan), due\_date, amount, status ('Pending'/'Paid'/'Late'), created\_at, updated\_at | (Lives in plans app) Represents a single installment. |

*Note: Requires setting AUTH\_USER\_MODEL \= 'accounts.User' in settings.py **early** in the project.*

### **3\. Docker & Docker Compose**

* **Dockerfile:** Defines the Python 3.11-slim environment, installs dependencies from requirements.txt, copies code, exposes port 8000\.  
* **docker-compose.yml:** (Simplified version requested)  
  * db service: PostgreSQL 15-alpine, named volume postgres\_data, environment variables for DB setup (use .env).  
  * backend service: Builds from Dockerfile, mounts local ./backend to /app, exposes port 8000, environment variables for DB connection & Django settings (use .env), depends\_on: \[db\]. Startup command: python manage.py runserver 0.0.0.0:8000.  
  * networks: Defines bnpl\_network.  
  * volumes: Defines postgres\_data.  
* **Requires .env file:** For storing secrets (DJANGO\_SECRET\_KEY, POSTGRES\_PASSWORD, etc.). Add to .gitignore.

### **4\. Testing Strategy**

* **Unit Tests:** Validate custom UserManager, models (User, PaymentPlan, Installment), installment generation logic, signal handlers, custom permission classes.  
* **Integration Tests (DRF APITestCase):** Test API endpoints, auth flows (registration, signin, role checks), end-to-end scenarios (create plan \-\> user signin \-\> pay installment), IDOR prevention.

### **5\. API Endpoints (DRF)**

Authorization relies on checking the request.user.role field via permission classes.

| Endpoint | Method | Role(s) | Input (request.data or URL param) | Output (Success: 2xx) | Description |
| :---- | :---- | :---- | :---- | :---- | :---- |
| /api/accounts/register/ | POST | Any | email, password, role ('merchant' or 'user') | User details (excluding sensitive info), success message. | Registers a new user using the custom User model. Sets the role field based on input. |
| /api/accounts/signin/ | POST | Any | email, password | JWTs (access, refresh), user\_role ('merchant' or 'user'). | Authenticates a user (using email), returns tokens and the role from the user object. |
| /api/plans/ | POST | Merchant | user\_id, total\_amoun, number\_of\_installments, start\_date | Created PaymentPlan with nested Installment list. | Creates plan and installments. Accessible only to authenticated users with role='merchant'. |
| /api/plans/ | GET | Merchant / User | (None \- Filtered by auth user) | List of relevant PaymentPlan objects (with installments). | Retrieves plans based on user role: Merchants (role='merchant') see plans where merchant=request.user; Users (role='user') see plans where user\_email=request.user.email. Filtering logic within the viewset/serializer needs to check request.user.role and apply the correct filter. |
| /api/installments/{id}/pay/ | POST | User | (Installment ID {id} in URL) | Updated Installment (status: 'Paid'). | Pays an installment. Accessible only to authenticated users with role='user'. Validates the installment {id} belongs to a plan associated with the request.user.email (via installment.plan.user\_email) and that the installment status is 'Pending'. Prevents paying already 'Paid' installments or installments belonging to other users. If all installments are 'Paid' change the status of the plan to 'Paid' |
| /api/accounts/me/ | GET | Any | None | User details (excluding sensitive info) | Returns authenticated user's profile. 401 if not authenticated. |

### **6\. Authentication & Authorization**

* **Authentication:** JWT via /api/accounts/signin/. Uses email as the identifier. djangorestframework-simplejwt handles token generation and validation.  
* **Authorization:** Managed using **custom DRF Permission classes** that check request.user.role.  
  * Classes like IsMerchant, IsUserRole, IsAssociatedUserForPlan will be created.  
  * IsMerchant: Checks return request.user.is\_authenticated and request.user.role \== 'merchant'  
  * IsUserRole: Checks return request.user.is\_authenticated and request.user.role \== 'user'  
  * Permission classes applied to ViewSets/Views control access. Object-level permissions check ownership/association (e.g., user can only pay installments linked to their email).

### **6\. Authentication & Authorization**

* **Authentication:** JWT via /api/accounts/signin/. Uses email as the identifier. djangorestframework-simplejwt handles token generation and validation.  
* **Authorization:** Managed using DRF Permission classes that check user’s ownership to a resource. The role in the user model is used to differentiate between merchant and user access for resources.   
* Classes like IsMerchant, IsUserRole, IsAssociatedUserForPlan will be created.  
  * IsMerchant: Checks if the user belongs to the "Merchant" group.  
  * IsUserRole: Checks if the user belongs to the "User" group.  
  * Permission classes applied to ViewSets/Views control access. Object-level permissions check ownership/association (e.g., users can only pay installments linked to their “ID”).

### **7\. Updating Installments**
* There will be a cron job triggered by celery-beat every day at 12:05 am Saudi time to update intallments status to `Due` or `late`.
* There will be a cron job triggered everyday 9 am Saudi time to notify users about upcoming installments due in the next 3 days.

### **8\. API Documentation (Swagger)**

* Integrate drf-yasg or drf-spectacular for auto-generated OpenAPI schema and interactive Swagger/Redoc UI (e.g., at /api/swagger/).

### **10\. Frontend Consideration**

* A **single React application** will serve as the dashboard for both Merchants and Users.  
* The frontend will differentiate the UI/UX based on the user\_role received from the backend after signin.  
* CORS (Cross-Origin Resource Sharing) must be configured correctly on the Django backend (using django-cors-headers) to allow requests from the React app's origin.