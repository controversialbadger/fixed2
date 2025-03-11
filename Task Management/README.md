# Task Management Application

A spreadsheet-like task management application with calendar integration and reminder system.

## Features

- Spreadsheet-like interface for managing tasks
- Add, edit, and delete tasks
- Set task priorities, deadlines, and reminders
- Calendar integration for visualizing task deadlines
- Reminder system with pop-up notifications
- Filter and search tasks
- Export tasks to CSV
- Save and load tasks from JSON file
- Visual distinction for overdue tasks

## Requirements

- Python 3.6 or higher
- PyQt5

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Run the application with:

```bash
python main.py
```

### Adding Tasks

1. Click the "Add Task" button or select "Edit" > "Add Task" from the menu
2. Fill in the task details:
   - Title
   - Description
   - Priority (Low, Medium, High)
   - Status (Not Started, In Progress, Completed)
   - Deadline date and time
   - Reminder (No Reminder, 5 minutes before, 15 minutes before, etc.)
3. Click "OK" to add the task

### Editing Tasks

1. Select a task from the table
2. Click the "Edit Task" button or select "Edit" > "Edit Task" from the menu
3. Modify the task details
4. Click "OK" to save the changes

### Deleting Tasks

1. Select a task from the table
2. Click the "Delete Task" button or select "Edit" > "Delete Task" from the menu
3. Confirm the deletion

### Filtering Tasks

Use the filter dropdown to filter tasks by:
- All
- Active
- Completed
- Overdue

### Searching Tasks

Type in the search box to search for tasks by title or description.

### Calendar View

Click the "Calendar" button or select "View" > "Calendar" from the menu to open the calendar view. The calendar shows dates with tasks highlighted, and you can click on a date to see the tasks for that day.

### Saving and Loading Tasks

- Select "File" > "Save" to save tasks to a JSON file
- Select "File" > "Load" to load tasks from a JSON file

### Exporting Tasks

Select "File" > "Export to CSV" to export tasks to a CSV file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.