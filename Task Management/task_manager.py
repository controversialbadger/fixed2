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
                            QFormLayout, QDialogButtonBox, QCalendarWidget, QFrame)
from recurrence_system import RecurrencePattern, RecurrenceDialog, RecurrenceSystem
from PyQt5.QtCore import Qt, QTimer, QDateTime, QSortFilterProxyModel, QDate
from PyQt5.QtGui import QIcon, QColor, QBrush, QFont

from task_model import TaskTableModel
from reminder_system import ReminderSystem
from calendar_integration import CalendarDialog
from file_manager import FileManager, AttachmentDialog

class TaskManagerApp(QMainWindow):
    """Main window for the Task Manager application"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Task Manager")
        self.resize(1000, 600)
        
        # Set application style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #fafafa;
            }
            QMenuBar {
                background-color: #f0f0f0;
                border-bottom: 1px solid #ddd;
            }
            QMenuBar::item {
                padding: 6px 10px;
                color: #333;
            }
            QMenuBar::item:selected {
                background-color: #e3f2fd;
                color: #2196F3;
            }
            QStatusBar {
                background-color: #f0f0f0;
                color: #666;
                border-top: 1px solid #ddd;
            }
            QToolTip {
                border: 1px solid #ccc;
                background-color: #f8f8f8;
                color: #333;
                padding: 5px;
            }
        """)
        
        # Initialize the task model and reminder system
        self.task_model = TaskTableModel()
        self.reminder_system = ReminderSystem(self)
        self.recurrence_system = RecurrenceSystem(self.task_model)
        
        # Setup the UI
        self.setup_ui()
        
        # Setup the reminder timer
        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.check_reminders)
        self.reminder_timer.start(60000)  # Check every minute
        
        # Create data directory in user's home directory
        self.data_dir = os.path.join(os.path.expanduser("~"), ".task_manager")
        if not os.path.exists(self.data_dir):
            try:
                os.makedirs(self.data_dir)
            except OSError as e:
                QMessageBox.warning(self, "Warning", f"Could not create data directory: {str(e)}")
        
        # Initialize file manager
        self.file_manager = FileManager(self.data_dir)
        
        # Set task file path
        self.task_file = os.path.join(self.data_dir, "tasks.json")
        
        # Load tasks if file exists
        if os.path.exists(self.task_file):
            self.load_tasks()
    
    def setup_ui(self):
        """Setup the user interface"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Header section with title and search
        header_layout = QHBoxLayout()
        
        # Title label
        title_label = QLabel("Task Manager")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin: 10px 0;")
        header_layout.addWidget(title_label)
        
        # Spacer
        header_layout.addStretch()
        
        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search tasks...")
        self.search_box.setToolTip("Search for tasks by title or description")
        self.search_box.textChanged.connect(self.search_tasks)
        self.search_box.setMinimumWidth(250)
        self.search_box.setMinimumHeight(36)
        self.search_box.setStyleSheet("""
            QLineEdit {
                border: 1px solid #ccc;
                border-radius: 18px;
                padding: 5px 15px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #2196F3;
            }
        """)
        header_layout.addWidget(self.search_box)
        
        main_layout.addLayout(header_layout)
        
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
        self.task_table.setToolTip("Double-click a task to edit it")
        self.task_table.doubleClicked.connect(self.edit_task)
        
        # Set row height
        self.task_table.verticalHeader().setDefaultSectionSize(36)
        self.task_table.verticalHeader().setVisible(False)  # Hide vertical header
        
        # Set header style
        self.task_table.horizontalHeader().setStyleSheet("""
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 10px 6px;
                border: none;
                border-bottom: 2px solid #2196F3;
                font-weight: bold;
                font-size: 14px;
                color: #333;
            }
        """)
        
        # Set table style
        self.task_table.setStyleSheet("""
            QTableView {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                gridline-color: #eee;
                selection-background-color: #e3f2fd;
                selection-color: #000;
            }
            QTableView::item {
                padding: 6px;
                border-bottom: 1px solid #eee;
            }
            QTableView::item:alternate {
                background-color: #f9f9f9;
            }
        """)
        
        main_layout.addWidget(self.task_table, 1)  # Give table a stretch factor of 1
        
        # Control panel
        control_panel = QWidget()
        control_panel.setStyleSheet("""
            background-color: #f0f0f0; 
            border-top: 1px solid #cccccc;
            border-radius: 0px; 
            padding: 10px;
        """)
        control_layout = QHBoxLayout(control_panel)
        control_layout.setContentsMargins(15, 15, 15, 15)
        control_layout.setSpacing(15)
        
        # Add task button
        add_button = QPushButton("Add Task")
        add_button.setIcon(self.style().standardIcon(self.style().SP_FileDialogNewFolder))
        add_button.setToolTip("Create a new task")
        add_button.setMinimumHeight(40)
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_button.clicked.connect(self.add_task)
        control_layout.addWidget(add_button)
        
        # Edit task button
        edit_button = QPushButton("Edit Task")
        edit_button.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))
        edit_button.setToolTip("Edit the selected task")
        edit_button.setMinimumHeight(40)
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0b7dda;
            }
        """)
        edit_button.clicked.connect(self.edit_task)
        control_layout.addWidget(edit_button)
        
        # Delete task button
        delete_button = QPushButton("Delete Task")
        delete_button.setIcon(self.style().standardIcon(self.style().SP_TrashIcon))
        delete_button.setToolTip("Delete the selected task")
        delete_button.setMinimumHeight(40)
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        delete_button.clicked.connect(self.delete_task)
        control_layout.addWidget(delete_button)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #cccccc; margin: 5px 10px;")
        control_layout.addWidget(separator)
        
        # Filter controls
        filter_label = QLabel("Filter:")
        filter_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        control_layout.addWidget(filter_label)
        
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Active", "Completed", "Overdue"])
        self.filter_combo.setToolTip("Filter tasks by status")
        self.filter_combo.setMinimumHeight(30)
        self.filter_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 4px;
                background-color: white;
                min-width: 120px;
            }
        """)
        self.filter_combo.currentTextChanged.connect(self.apply_filter)
        control_layout.addWidget(self.filter_combo)
        
        # Spacer
        control_layout.addStretch()
        
        # Calendar button
        calendar_button = QPushButton("Calendar View")
        calendar_button.setIcon(self.style().standardIcon(self.style().SP_DialogApplyButton))
        calendar_button.setToolTip("View tasks in a calendar")
        calendar_button.setMinimumHeight(40)
        calendar_button.setStyleSheet("""
            QPushButton {
                background-color: #9C27B0;
                color: white;
                font-weight: bold;
                border-radius: 4px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #7B1FA2;
            }
        """)
        calendar_button.clicked.connect(self.show_calendar)
        control_layout.addWidget(calendar_button)
        
        main_layout.addWidget(control_panel)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
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
        dialog = TaskDialog(self, file_manager=self.file_manager)
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
        dialog = TaskDialog(self, task_data, self.file_manager)
        
        if dialog.exec_() == QDialog.Accepted:
            updated_task = dialog.get_task_data()
            # Update the task and get unused attachments
            unused_attachments = self.task_model.update_task(row, updated_task)
            # Clean up unused attachments
            if unused_attachments:
                self.file_manager.clean_unused_attachments(unused_attachments)
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
            # Remove the task and get attachments for cleanup
            attachments = self.task_model.remove_task(row)
            # Clean up attachments
            if attachments:
                self.file_manager.clean_unused_attachments(attachments)
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
            task_data = self.task_model.get_task(row)
            self.task_model.mark_completed(row)
            
            # Handle recurring task
            if task_data and task_data.get('recurrence'):
                if self.recurrence_system.handle_completed_task(task_data):
                    self.statusBar().showMessage("Created next recurring task", 3000)
            
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
        except PermissionError:
            QMessageBox.critical(self, "Permission Error", 
                                f"Cannot write to {self.task_file}. Please check file permissions.")
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
    
    def __init__(self, parent=None, task_data=None, file_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Task" if task_data else "New Task")
        self.resize(500, 400)
        
        self.task_data = task_data or {}
        self.file_manager = file_manager
        
        self.setup_ui()
        
        # Fill the form if editing an existing task
        if task_data:
            self.fill_form()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        main_layout = QVBoxLayout(self)
        
        # Create a form layout for the inputs
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        
        # Task title
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Enter task title")
        self.title_edit.setToolTip("Enter a clear and concise title for your task")
        form_layout.addRow("Title:", self.title_edit)
        
        # Task description
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Enter task description")
        self.description_edit.setToolTip("Provide details about what needs to be done")
        form_layout.addRow("Description:", self.description_edit)
        
        # Priority
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Low", "Medium", "High"])
        self.priority_combo.setToolTip("Set the importance level of this task")
        
        # Add color indicators to priority dropdown
        self.priority_combo.setItemData(0, QBrush(QColor(200, 255, 200)), Qt.BackgroundRole)  # Low - Light green
        self.priority_combo.setItemData(1, QBrush(QColor(255, 255, 200)), Qt.BackgroundRole)  # Medium - Light yellow
        self.priority_combo.setItemData(2, QBrush(QColor(255, 200, 200)), Qt.BackgroundRole)  # High - Light red
        
        form_layout.addRow("Priority:", self.priority_combo)
        
        # Status
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Not Started", "In Progress", "Completed"])
        self.status_combo.setToolTip("Current status of the task")
        form_layout.addRow("Status:", self.status_combo)
        
        # Deadline date
        self.deadline_date = QDateEdit()
        self.deadline_date.setCalendarPopup(True)
        self.deadline_date.setDate(QDate.currentDate())
        self.deadline_date.setToolTip("Set the due date for this task")
        form_layout.addRow("Deadline Date:", self.deadline_date)
        
        # Deadline time
        self.deadline_time = QTimeEdit()
        self.deadline_time.setTime(QDateTime.currentDateTime().time())
        self.deadline_time.setToolTip("Set the due time for this task")
        form_layout.addRow("Deadline Time:", self.deadline_time)
        
        # Reminder checkbox
        self.reminder_combo = QComboBox()
        self.reminder_combo.addItems(["No Reminder", "5 minutes before", "15 minutes before", 
                                     "30 minutes before", "1 hour before", "1 day before"])
        self.reminder_combo.setToolTip("Set when you want to be reminded about this task")
        form_layout.addRow("Reminder:", self.reminder_combo)
        
        # Attachments
        self.attachments_label = QLabel("0 file(s) attached")
        self.attachments_button = QPushButton("Manage Attachments")
        self.attachments_button.setToolTip("Add, remove, or view file attachments")
        self.attachments_button.clicked.connect(self.manage_attachments)

        attachments_layout = QHBoxLayout()
        attachments_layout.addWidget(self.attachments_label)
        attachments_layout.addWidget(self.attachments_button)
        attachments_layout.addStretch()

        form_layout.addRow("Attachments:", attachments_layout)
        
        # Recurrence
        self.recurrence_label = QLabel("No recurrence")
        self.recurrence_button = QPushButton("Set Recurrence")
        self.recurrence_button.setToolTip("Set up recurring task")
        self.recurrence_button.clicked.connect(self.set_recurrence)

        recurrence_layout = QHBoxLayout()
        recurrence_layout.addWidget(self.recurrence_label)
        recurrence_layout.addWidget(self.recurrence_button)
        recurrence_layout.addStretch()

        form_layout.addRow("Recurrence:", recurrence_layout)
        
        main_layout.addLayout(form_layout)
        
        # Add a spacer
        main_layout.addSpacing(20)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Style the buttons
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setToolTip("Save the task")
        
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        cancel_button.setToolTip("Discard changes and close")
        
        main_layout.addWidget(button_box)
    
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
        index = self.reminder_combo.findText(reminder_offset)
        if index >= 0:
            self.reminder_combo.setCurrentIndex(index)
            
        # Update attachments label
        self.update_attachments_label()
        
        # Update recurrence label
        recurrence_data = self.task_data.get('recurrence')
        if recurrence_data:
            recurrence = RecurrencePattern.from_dict(recurrence_data)
            self.recurrence_label.setText(recurrence.get_description())
    
    def get_task_data(self):
        """Get the task data from the form"""
        # Get the deadline datetime
        date = self.deadline_date.date()
        time = self.deadline_time.time()
        deadline = datetime(date.year(), date.month(), date.day(), 
                           time.hour(), time.minute(), time.second())
        
        # Calculate reminder time based on offset
        reminder_offset = self.reminder_combo.currentText()
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
            'completed': self.status_combo.currentText() == "Completed",
            'attachments': self.task_data.get('attachments', [])
        }
        
        return task_data
        
    def manage_attachments(self):
        """Open the attachment dialog to manage attachments"""
        if not self.file_manager:
            QMessageBox.warning(self, "Error", "File manager not initialized.")
            return
        
        # Get current attachments
        attachments = self.task_data.get('attachments', [])
        
        # Open the attachment dialog
        dialog = AttachmentDialog(self, attachments, self.file_manager)
        if dialog.exec_() == QDialog.Accepted:
            # Update attachments
            self.task_data['attachments'] = dialog.get_attachments()
            # Update the label
            self.update_attachments_label()
            
    def update_attachments_label(self):
        """Update the attachments label with the current count"""
        attachments = self.task_data.get('attachments', [])
        count = len(attachments)
        self.attachments_label.setText(f"{count} file(s) attached")
        
    def set_recurrence(self):
        """Open the recurrence dialog to set up recurring tasks"""
        # Get current recurrence data if it exists
        recurrence_data = self.task_data.get('recurrence')
        recurrence = None
        if recurrence_data:
            recurrence = RecurrencePattern.from_dict(recurrence_data)
            
        # Open the recurrence dialog
        dialog = RecurrenceDialog(self, recurrence)
        if dialog.exec_() == QDialog.Accepted:
            # Update recurrence
            new_recurrence = dialog.get_recurrence()
            if new_recurrence:
                self.task_data['recurrence'] = new_recurrence.to_dict()
                self.recurrence_label.setText(new_recurrence.get_description())
            else:
                # Recurrence was removed
                if 'recurrence' in self.task_data:
                    del self.task_data['recurrence']
                self.recurrence_label.setText("No recurrence")