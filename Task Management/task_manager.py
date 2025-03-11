#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTableView, QPushButton, QLabel, QDateEdit, 
                            QTimeEdit, QLineEdit, QComboBox, QMessageBox,
                            QFileDialog, QMenu, QAction, QHeaderView, QDialog,
                            QFormLayout, QDialogButtonBox, QCalendarWidget)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSortFilterProxyModel, QDate
from PyQt5.QtGui import QIcon, QColor, QBrush, QFont

from task_model import TaskTableModel
from reminder_system import ReminderSystem
from calendar_integration import CalendarDialog

class TaskManagerApp(QMainWindow):
    """Main window for the Task Manager application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.resize(1000, 600)
        
        # Initialize the task model and reminder system
        self.task_model = TaskTableModel()
        self.reminder_system = ReminderSystem(self)
        
        # Setup the UI
        self.setup_ui()
        
        # Setup the reminder timer
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # Check every minute
        
        # Load tasks if file exists
        self.task_file = "tasks.json"
        if os.path.exists(self.task_file):
            self.load_tasks()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Task table
        self.proxy_model = QSortFilterProxyModel()
        self.proxy_model.setSourceModel(self.task_model)
        
        self.task_table = QTableView()
        self.task_table.setModel(self.proxy_model)
        self.task_table.setSortingEnabled(True)
        self.task_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.task_table.setSelectionBehavior(QTableView.SelectRows)
        self.task_table.setAlternatingRowColors(True)
        self.task_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.task_table.customContextMenuRequested.connect(self.show_context_menu)
        
        main_layout.addWidget(self.task_table)
        
        # Control panel
        control_panel = QWidget()
        control_layout = QHBoxLayout(control_panel)
        
        # Add task button
        add_button = QPushButton("Add Task")
        add_button.clicked.connect(self.add_task)
        control_layout.addWidget(add_button)
        
        # Edit task button
        edit_button = QPushButton("Edit Task")
        edit_button.clicked.connect(self.edit_task)
        control_layout.addWidget(edit_button)
        
        # Delete task button
        delete_button = QPushButton("Delete Task")
        delete_button.clicked.connect(self.delete_task)
        control_layout.addWidget(delete_button)
        
        # Filter controls
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Active", "Completed", "Overdue"])
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        control_layout.addWidget(QLabel("Filter:"))
        control_layout.addWidget(self.filter_combo)
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tasks...")
        self.search_box.textChanged.connect(self.search_tasks)
        control_layout.addWidget(self.search_box)
        
        # Calendar button
        calendar_button = QPushButton("Calendar")
        calendar_button.clicked.connect(self.show_calendar)
        control_layout.addWidget(calendar_button)
        
        main_layout.addWidget(control_panel)
        
        # Setup menu bar
        self.setup_menu()
    
    def setup_menu(self):
        """Setup the menu bar"""
        # File menu
        file_menu = self.menuBar().addMenu("File")
        
        # Save action
        save_action = QAction("Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_tasks)
        file_menu.addAction(save_action)
        
        # Load action
        load_action = QAction("Load", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_tasks)
        file_menu.addAction(load_action)
        
        # Export action
        export_action = QAction("Export to CSV", self)
        export_action.triggered.connect(self.export_to_csv)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("Edit")
        
        # Add task action
        add_action = QAction("Add Task", self)
        add_action.triggered.connect(self.add_task)
        edit_menu.addAction(add_action)
        
        # Edit task action
        edit_action = QAction("Edit Task", self)
        edit_action.triggered.connect(self.edit_task)
        edit_menu.addAction(edit_action)
        
        # Delete task action
        delete_action = QAction("Delete Task", self)
        delete_action.triggered.connect(self.delete_task)
        edit_menu.addAction(delete_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("View")
        
        # Calendar action
        calendar_action = QAction("Calendar", self)
        calendar_action.triggered.connect(self.show_calendar)
        view_menu.addAction(calendar_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("Help")
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def add_task(self):
        """Add a new task"""
        dialog = TaskDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            task_data = dialog.get_task_data()
            self.task_model.add_task(task_data)
            self.save_tasks()
    
    def edit_task(self):
        """Edit the selected task"""
        indexes = self.task_table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "No Selection", "Please select a task to edit.")
            return
        
        # Get the source model index
        proxy_index = indexes[0]
        source_index = self.proxy_model.mapToSource(proxy_index)
        row = source_index.row()
        
        task_data = self.task_model.get_task(row)
        dialog = TaskDialog(self, task_data)
        
        if dialog.exec_() == QDialog.Accepted:
            updated_task = dialog.get_task_data()
            self.task_model.update_task(row, updated_task)
            self.save_tasks()
    
    def delete_task(self):
        """Delete the selected task"""
        indexes = self.task_table.selectionModel().selectedRows()
        if not indexes:
            QMessageBox.warning(self, "No Selection", "Please select a task to delete.")
            return
        
        # Confirm deletion
        reply = QMessageBox.question(
            self, "Confirm Deletion",
            "Are you sure you want to delete the selected task?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Delete the task
            proxy_index = indexes[0]
            source_index = self.proxy_model.mapToSource(proxy_index)
            row = source_index.row()
            self.task_model.remove_task(row)
            self.save_tasks()
    
    def show_context_menu(self, position):
        """Show context menu for the task table"""
        indexes = self.task_table.selectionModel().selectedRows()
        if not indexes:
            return
        
        menu = QMenu()
        
        # Add actions
        edit_action = menu.addAction("Edit Task")
        delete_action = menu.addAction("Delete Task")
        mark_completed_action = menu.addAction("Mark as Completed")
        
        # Show the menu and get the selected action
        action = menu.exec_(self.task_table.viewport().mapToGlobal(position))
        
        if action == edit_action:
            self.edit_task()
        elif action == delete_action:
            self.delete_task()
        elif action == mark_completed_action:
            # Mark the task as completed
            proxy_index = indexes[0]
            source_index = self.proxy_model.mapToSource(proxy_index)
            row = source_index.row()
            self.task_model.mark_completed(row)
            self.save_tasks()
    
    def apply_filter(self, filter_text):
        """Apply filter to the task table"""
        self.proxy_model.setFilterRole(Qt.UserRole)
        
        if filter_text == "All":
            self.proxy_model.setFilterFixedString("")
        elif filter_text == "Active":
            self.proxy_model.setFilterFixedString("active")
        elif filter_text == "Completed":
            self.proxy_model.setFilterFixedString("completed")
        elif filter_text == "Overdue":
            self.proxy_model.setFilterFixedString("overdue")
    
    def search_tasks(self, search_text):
        """Search tasks by title or description"""
        self.proxy_model.setFilterRole(Qt.DisplayRole)
        self.proxy_model.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.proxy_model.setFilterFixedString(search_text)
    
    def show_calendar(self):
        """Show the calendar dialog"""
        dialog = CalendarDialog(self.task_model.tasks, self)
        dialog.exec_()
    
    def check_reminders(self):
        """Check for tasks that need reminders"""
        self.reminder_system.check_reminders(self.task_model.tasks)
    
    def save_tasks(self):
        """Save tasks to a JSON file"""
        try:
            with open(self.task_file, 'w') as f:
                json.dump(self.task_model.tasks, f, default=self._serialize_datetime)
            self.statusBar().showMessage("Tasks saved successfully", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save tasks: {str(e)}")
    
    def load_tasks(self):
        """Load tasks from a JSON file"""
        try:
            with open(self.task_file, 'r') as f:
                tasks = json.load(f)
                # Convert string dates back to datetime objects
                for task in tasks:
                    if 'deadline' in task and task['deadline']:
                        task['deadline'] = datetime.fromisoformat(task['deadline'])
                    if 'reminder_time' in task and task['reminder_time']:
                        task['reminder_time'] = datetime.fromisoformat(task['reminder_time'])
                
                self.task_model.set_tasks(tasks)
            self.statusBar().showMessage("Tasks loaded successfully", 3000)
        except FileNotFoundError:
            self.statusBar().showMessage("No saved tasks found", 3000)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load tasks: {str(e)}")
    
    def export_to_csv(self):
        """Export tasks to a CSV file"""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Export Tasks", "", "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_name:
            try:
                self.task_model.export_to_csv(file_name)
                self.statusBar().showMessage(f"Tasks exported to {file_name}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export tasks: {str(e)}")
    
    def show_about(self):
        """Show the about dialog"""
        QMessageBox.about(
            self, "About Task Manager",
            "Task Manager v1.0\n\n"
            "A spreadsheet-like task management application with calendar "
            "integration and reminder system.\n\n"
            "© 2023 Task Manager Team"
        )
    
    def _serialize_datetime(self, obj):
        """Helper method to serialize datetime objects to JSON"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")


class TaskDialog(QDialog):
    """Dialog for adding or editing tasks"""
    
    def __init__(self, parent=None, task_data=None):
        super().__init__(parent)
        self.setWindowTitle("Task" if task_data else "New Task")
        self.resize(400, 300)
        
        self.task_data = task_data or {}
        
        self.setup_ui()
        
        # Fill the form if editing an existing task
        if task_data:
            self.fill_form()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QFormLayout(self)
        
        # Task title
        self.title_edit = QLineEdit()
        layout.addRow("Title:", self.title_edit)
        
        # Task description
        self.description_edit = QLineEdit()
        layout.addRow("Description:", self.description_edit)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        layout.addRow("Priority:", self.priority_combo)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Not Started", "In Progress", "Completed"])
        layout.addRow("Status:", self.status_combo)
        
        # Deadline date
        self.deadline_date = QDateEdit()
        self.deadline_date.setCalendarPopup(True)
        self.deadline_date.setDate(QDate.currentDate())
        layout.addRow("Deadline Date:", self.deadline_date)
        
        # Deadline time
        self.deadline_time = QTimeEdit()
        self.deadline_time.setTime(QDateTime.currentDateTime().time())
        layout.addRow("Deadline Time:", self.deadline_time)
        
        # Reminder checkbox
        self.reminder_checkbox = QComboBox()
        self.reminder_checkbox.addItems(["No Reminder", "5 minutes before", "15 minutes before", 
                                         "30 minutes before", "1 hour before", "1 day before"])
        layout.addRow("Reminder:", self.reminder_checkbox)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)
    
    def fill_form(self):
        """Fill the form with existing task data"""
        self.title_edit.setText(self.task_data.get('title', ''))
        self.description_edit.setText(self.task_data.get('description', ''))
        
        # Set priority
        priority = self.task_data.get('priority', 'Medium')
        index = self.priority_combo.findText(priority)
        if index >= 0:
            self.priority_combo.setCurrentIndex(index)
        
        # Set status
        status = self.task_data.get('status', 'Not Started')
        index = self.status_combo.findText(status)
        if index >= 0:
            self.status_combo.setCurrentIndex(index)
        
        # Set deadline
        deadline = self.task_data.get('deadline')
        if deadline:
            self.deadline_date.setDate(QDate(deadline.year, deadline.month, deadline.day))
            self.deadline_time.setTime(deadline.time())
        
        # Set reminder
        reminder_offset = self.task_data.get('reminder_offset', 'No Reminder')
        index = self.reminder_checkbox.findText(reminder_offset)
        if index >= 0:
            self.reminder_checkbox.setCurrentIndex(index)
    
    def get_task_data(self):
        """Get the task data from the form"""
        # Get the deadline datetime
        date = self.deadline_date.date()
        time = self.deadline_time.time()
        deadline = datetime(date.year(), date.month(), date.day(), 
                           time.hour(), time.minute(), time.second())
        
        # Calculate reminder time based on offset
        reminder_offset = self.reminder_checkbox.currentText()
        reminder_time = None
        
        if reminder_offset != "No Reminder":
            if reminder_offset == "5 minutes before":
                reminder_time = deadline - timedelta(minutes=5)
            elif reminder_offset == "15 minutes before":
                reminder_time = deadline - timedelta(minutes=15)
            elif reminder_offset == "30 minutes before":
                reminder_time = deadline - timedelta(minutes=30)
            elif reminder_offset == "1 hour before":
                reminder_time = deadline - timedelta(hours=1)
            elif reminder_offset == "1 day before":
                reminder_time = deadline - timedelta(days=1)
        
        # Create the task data dictionary
        task_data = {
            'title': self.title_edit.text(),
            'description': self.description_edit.text(),
            'priority': self.priority_combo.currentText(),
            'status': self.status_combo.currentText(),
            'deadline': deadline,
            'reminder_offset': reminder_offset,
            'reminder_time': reminder_time,
            'completed': self.status_combo.currentText() == "Completed"
        }
        
        return task_data