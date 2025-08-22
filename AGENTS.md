# Todo-app docs for Agents to read

## Description
"todo-app" is a cross-platform Todo list app that will help you manage your tasks and stay organized. Here are the main features it will support:

- Create, edit, and delete tasks easily.
- Organize your tasks into different lists (like "Work", "Personal", or "Shopping").
- Add due dates and start times to your tasks.
- Get reminders for upcoming tasks so you never miss anything important.
- Mark tasks as complete and archive them for later reference.
- Set priorities to focus on what matters most.
- Add tags and color-code your tasks for better organization.
- Use a calendar or time picker to quickly set dates.
- Understand natural language dates (like "tomorrow at 5pm") and highlight them for you.
- Search and filter your tasks to find exactly what you need.
- Get instant updates when tasks change, thanks to real-time alerts.
- Work across different devices and platforms, with a simple and friendly interface.

This app is designed to make managing your to-dos simple, flexible, and efficient!

## Technical details
This app is split into two separate parts; a backend and frontend. 

The backend will be written in Python, with a FastAPI intermediary layer for CRUD (create, read, update delete) of tasks. A locally running HTTP server, uvicorn, will allow interaction with FastAPI in order to facilitate CRUD.

The frontend will initially be written in Python Kivy. This will provide the user interface which will interact with the backend via HTTP calls for CRUD. Once all or nearly all the features are complete, the intention is to replace the Python Kivy frontend with React Native, which is also cross-platform but a much better framework (the author is much more familiar with Python/Kivy than with React/JavaScript, hence why Kivy is being used first).

## TODO List for Codex Agent

### 1. Testing
- [ ] **Write unit tests** for backend API endpoints (CRUD for tasks).
- [ ] **Write integration tests** for the full stack (Kivy frontend <-> FastAPI backend).
- [ ] **Test WebSocket alert functionality** (connection, broadcast, disconnect).
- [ ] **Test database migrations and initialization.**

### 2. Kivy GUI Improvements
- [ ] **Ensure Kivy GUI works in GitHub Codespaces** (headless mode, Xvfb setup, documentation).
- [ ] **Add a calendar/time picker widget** for the task date field in the Kivy UI.
- [ ] **Improve error handling and user feedback** in the Kivy app.
- [ ] **Add loading indicators and empty state screens.**

### 3. Task Model & Features
- [ ] **Add support for multiple lists** (e.g., "Work", "Personal", "Shopping").
- [ ] **Implement tags for tasks** (with color coding in UI).
- [ ] **Add `start_datetime` field** to tasks (in addition to due date).
- [ ] **Add reminders/notifications** for upcoming tasks (backend and Kivy notification).
- [ ] **Allow recurring tasks** (e.g., daily, weekly).
- [ ] **Support task priorities** (e.g., low, medium, high).
- [ ] **Add task completion and archiving.**

### 4. Smart Date Parsing & Highlighting
- [ ] **Automatically parse dates/times from the task title** (e.g., "Call mom tomorrow at 5pm").
- [ ] **Highlight parsed dates/times in the UI** (both in Kivy and API response).
- [ ] **Use a natural language date parser** (e.g., `dateparser` or `parsedatetime`).

### 5. API & Backend Enhancements
- [ ] **Add filtering and searching** (by list, tag, date, completion).
- [ ] **Add pagination to `/tasks` endpoint.**
- [ ] **Add user authentication (optional, for multi-user support).**
- [ ] **Improve error messages and validation.**
- [ ] **Add OpenAPI documentation for new endpoints and fields.**

### 6. DevOps & Documentation
- [ ] **Document setup for Codespaces and local development.**
- [ ] **Add scripts for database migration and seeding.**
- [ ] **Update `environment.yml` and dependencies as features are added.**
- [ ] **Add CI workflow for tests and linting.**

---

**Feel free to add, check off, or clarify tasks as you work!**
