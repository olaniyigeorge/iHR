# iHR App Development Plan

## Backend: FastAPI

### 1. Authentication System
- [✔] **Setup Project Structure:**
  - [✔] Create a new FastAPI project.
  - [✔] Define the folder structure (`/app`, `/routers`, `/models`, `/schemas`, `/utils`).

- [✔] **Database Setup:**
  - [✔] Install SQLAlchemy and PostgreSQL driver.
  - [✔] Configure a Sqlite3 databse for development and a PostgreSQL database for production.
  - [✔] Set up models for `User` and other entities.

- [✔] **User Authentication:**
  - [✔] Create `User` model with fields (`id`, `username`, `email`, `password`).
  - [✔] Hash passwords using `passlib`.
  - [✔] Implement a `/auth/register` endpoint for user registration.
  - [✔] Implement a `/auth/token` endpoint for token login using OAuth2 with JWT.
  - [✔] Implement token validation and create a dependency to get the current user.

- [ ] **Role-based Access:**
  - [ ] Add a `role` field to the `User` model (e.g., admin, user).
  - [ ] Implement middleware or utility to enforce role-based access control.

### 2. Interview Simulation API
- [ ] **Dynamic Question Generation:**
  - [ ] Create a model for `InterviewScenario` with fields (`id`, `industry`, `role`, `difficulty`).
  - [ ] Integrate with OpenAI API (or Hugging Face) to generate questions dynamically.
  - [ ] Implement an endpoint `/interviews/questions` to fetch questions.

- [ ] **Simulate Conversational Flow:**
  - [ ] Implement a WebSocket endpoint `/interviews/simulate` for real-time Q&A.
  - [ ] Use AI (e.g., OpenAI) to generate responses to user answers.

- [ ] **Stress Testing:**
  - [ ] Design a question pipeline with follow-up logic.
  - [ ] Include challenging questions based on user responses.

### 3. Feedback System
- [ ] **Feedback Analysis:**
  - [ ] Use AI for analyzing tone, grammar, and confidence (optional: voice input).
  - [ ] Store feedback results in a `Feedback` table.

- [ ] **Scorecard API:**
  - [ ] Define metrics (e.g., communication, problem-solving).
  - [ ] Create an endpoint `/feedback/scorecard` to return a detailed scorecard.

### 4. Progress Dashboard API
- [ ] **User Progress Tracking:**
  - [ ] Create a `UserProgress` model to store progress data (e.g., `interview_date`, `score`, `feedback`).
  - [ ] Implement endpoints `/dashboard/progress` for fetching progress data.

- [ ] **Visual Insights API:**
  - [ ] Compute aggregates (e.g., average score over time).
  - [ ] Prepare data for frontend visualization.

### 5. Customization Features
- [ ] **Industry and Role Selection:**
  - [ ] Create a table for predefined industries and roles.
  - [ ] Implement endpoints `/settings/industries` and `/settings/roles`.

- [ ] **Difficulty Settings:**
  - [ ] Add support for difficulty levels in the question generator.

### 6. Content Recommendation
- [ ] **Recommendation System:**
  - [ ] Use a simple tagging mechanism for articles and resources.
  - [ ] Implement an endpoint `/recommendations` to fetch personalized suggestions.

### 7. Deployment
- [ ] **Dockerize the Backend:**
  - [ ] Write a Dockerfile for FastAPI.
  - [ ] Use Docker Compose to set up PostgreSQL, Redis (optional), and the FastAPI service.

- [ ] **Testing and CI/CD:**
  - [ ] Write unit and integration tests for each API.
  - [ ] Set up CI/CD pipelines (GitHub Actions, GitLab CI, etc.).

---

## Frontend: Next.js

### 1. Authentication
- [ ] **Setup Next.js Project:**
  - [ ] Create a new Next.js project.
  - [ ] Set up TailwindCSS or another UI library.

- [ ] **Login and Registration:**
  - [ ] Create pages for login (`/login`) and registration (`/register`).
  - [ ] Implement forms to collect user input.
  - [ ] Use Axios to call backend endpoints.

- [ ] **Token Handling:**
  - [ ] Store JWT tokens in cookies or localStorage.
  - [ ] Implement logic to attach tokens to requests.

### 2. Interview Simulation UI
- [ ] **Question-Answer Flow:**
  - [ ] Create a page `/interviews` for the simulator.
  - [ ] Fetch questions from `/interviews/questions` API and display them one by one.
  - [ ] Add real-time chat using WebSockets.

- [ ] **Stress Testing:**
  - [ ] Implement UI for follow-up questions (e.g., timed responses).

### 3. Progress Dashboard
- [ ] **Visualize Progress:**
  - [ ] Create a `/dashboard` page.
  - [ ] Use Chart.js or Recharts to display progress graphs.

- [ ] **Achievements and Badges:**
  - [ ] Display milestones and achievements with icons.

### 4. Customization
- [ ] **Settings Page:**
  - [ ] Create a `/settings` page for selecting industries, roles, and difficulty levels.
  - [ ] Fetch and update user preferences via API.

### 5. Content Recommendations
- [ ] **Resource Recommendations Page:**
  - [ ] Create a `/resources` page to display recommended articles and courses.

### 6. Deployment
- [ ] **Dockerize the Frontend:**
  - [ ] Write a Dockerfile for the Next.js app.

- [ ] **Integrate with Backend:**
  - [ ] Ensure proper communication between frontend and backend APIs.

---

## Step-by-Step Implementation Order

### Backend
1. Authentication (Registration/Login/Token Handling).
2. Question generation API.
3. Feedback API.
4. Dashboard API.
5. Customization endpoints.
6. Recommendations API.

### Frontend
1. Authentication (Login/Signup pages).
2. Interview Simulator UI.
3. Progress Dashboard.
4. Settings and Customization.
5. Recommendations Page.
