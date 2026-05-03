# Presentation Notes - E-Commerce Lite

**Course:** Design of Multi-Tier Internet Applications  
**Student:** Myroslav Abdeljawwad (ID 74448)  
**Theme:** E-Commerce Lite  
**Duration:** 10-12 minutes

## Slide outline

### Slide 1: What the project is

Say:

> "This is a small e-commerce app I built for the course. It has a frontend, a Flask API, and a database layer."

Show the diagram from `docs/architecture.md`.

### Slide 2: Main design choices

- I kept it as one Flask app instead of splitting it into services.
- The frontend is vanilla JS.
- The API is versioned under `/api/v1`.
- Auth uses JWT tokens because it was simple to wire into the frontend.

### Slide 3: Security and roles

- users log in with username and password
- passwords are stored as hashes
- `admin` can manage catalog data and view all orders
- `customer` can place orders and view own orders
- protected routes return `401` or `403` depending on the case

### Slide 4: Data and reliability

- main entities: User, Category, Product, Order, OrderItem
- order history is kept even if a product is deleted later
- `/health` is for liveness
- `/ready` checks the database connection
- product list responses use a small in-memory cache

### Slide 5: Running and testing

- local run with SQLite
- Docker Compose with PostgreSQL
- pytest test suite
- GitHub Actions CI file

## Demo plan

### Happy path

Customer:

1. Open the app.
2. Browse products.
3. Add an item to the cart.
4. Log in as `customer1 / customer123`.
5. Place an order.
6. Open **My Orders**.
7. Click **Pay (simulated)**.

Admin:

1. Log out.
2. Log in as `admin / admin123`.
3. Open the admin page.
4. Create a category or product.
5. Show the order list.

### Access-control example

1. Stay logged in as `customer1`.
2. Try an admin-only request like `DELETE /api/v1/products/1`.
3. Show that it returns `403`.

### Failure example

1. Stop the database container.
2. Call `GET /ready`.
3. Show that it returns `503`.
4. Start the database again.
5. Call `GET /ready` again and show recovery.

## Possible questions

**Why one Flask app instead of microservices?**  
Because the project was small enough that one app was easier to build, run, and explain.

**Why JWT instead of sessions?**  
It was the simplest option for this frontend/API setup.

**How do you stop customers from using admin routes?**  
Protected routes check the token and role before the action runs.

**What happens if stock is too low?**  
The order is rejected and the API returns an error instead of creating the order.

**What is still unfinished or weak?**  
The cache is basic, payment is only simulated, and some route/service boundaries could still be cleaned up.

**How are the tests organized?**  
There are API tests and service-level tests.

## Backup plan

- If Docker has issues, run locally with SQLite.
- If the live demo breaks, show the tests and walk through the architecture.
- Keep Postman or browser dev tools ready for the auth/error examples.

## Timing

- Intro and architecture: 3 minutes
- Demo: 3 minutes
- Failure/access-control example: 1-2 minutes
- Questions: 3-4 minutes

## Defense reminders

Be ready to explain:

- what each tier does
- why the project uses one Flask app
- where auth happens
- how `401` and `403` differ
- what `/health` and `/ready` are for
- what still needs improvement
