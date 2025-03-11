#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                           QListWidget, QListWidgetItem, QLabel, QPushButton,
                           QFrame, QSplitter)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QColor, QBrush, QFont

class CalendarDialog(QDialog):
    """Dialog for calendar integration with tasks"""
    
    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Calendar")
        self.resize(800, 600)
        
        self.tasks = tasks
        
        self.setup_ui()
        self.populate_task_list()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create a splitter for resizable sections
        splitter = QSplitter(Qt.Horizontal)
        
        # Calendar widget
        calendar_frame = QFrame()
        calendar_layout = QVBoxLayout(calendar_frame)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setSelectionMode(QCalendarWidget.SingleSelection)
        self.calendar.clicked.connect(self.date_selected)
        
        calendar_layout.addWidget(QLabel("Calendar"))
        calendar_layout.addWidget(self.calendar)
        
        # Task list widget
        task_frame = QFrame()
        task_layout = QVBoxLayout(task_frame)
        
        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        self.task_list.setSelectionMode(QListWidget.SingleSelection)
        
        task_layout.addWidget(QLabel("Tasks for Selected Date"))
        task_layout.addWidget(self.task_list)
        
        # Add frames to splitter
        splitter.addWidget(calendar_frame)
        splitter.addWidget(task_frame)
        
        # Set initial sizes
        splitter.setSizes([400, 400])
        
        main_layout.addWidget(splitter)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
        
        # Highlight dates with tasks
        self.highlight_task_dates()
    
    def highlight_task_dates(self):
        """Highlight dates that have tasks"""
        # Get the first day of the month
        current_date = self.calendar.selectedDate()
        year = current_date.year()
        month = current_date.month()
        
        # Create a format for dates with tasks
        task_format = self.calendar.dateTextFormat(QDate())
        task_format.setBackground(QBrush(QColor(200, 230, 255)))  # Light blue
        
        # Clear existing highlights
        self.calendar.setDateTextFormat(QDate(), task_format.clone())
        
        # Set the format for dates with tasks
        for task in self.tasks:
            deadline = task.get('deadline')
            if deadline:
                task_date = QDate(deadline.year, deadline.month, deadline.day)
                self.calendar.setDateTextFormat(task_date, task_format)
    
    def date_selected(self, date):
        """Handle date selection"""
        self.populate_task_list(date)
    
    def populate_task_list(self, selected_date=None):
        """Populate the task list with tasks for the selected date"""
        self.task_list.clear()
        
        if selected_date is None:
            selected_date = self.calendar.selectedDate()
        
        # Convert QDate to Python date for comparison
        py_date = datetime(selected_date.year(), selected_date.month(), selected_date.day()).date()
        
        # Add tasks for the selected date
        for task in self.tasks:
            deadline = task.get('deadline')
            if deadline and deadline.date() == py_date:
                self._add_task_to_list(task)
    
    def _add_task_to_list(self, task):
        """Add a task to the list widget"""
        item = QListWidgetItem()
        
        # Set the item text
        title = task.get('title', 'Untitled Task')
        status = task.get('status', 'Not Started')
        priority = task.get('priority', 'Medium')
        deadline = task.get('deadline')
        time_str = deadline.strftime('%H:%M') if deadline else 'No time'
        
        item.setText(f"{title} ({time_str}) - {priority} priority - {status}")
        
        # Set the item tooltip
        description = task.get('description', 'No description')
        item.setToolTip(f"{title}\n\n{description}\n\nDeadline: {deadline}\nPriority: {priority}\nStatus: {status}")
        
        # Set the item background color based on priority
        if priority == 'High':
            item.setBackground(QBrush(QColor(255, 200, 200)))  # Light red
        elif priority == 'Medium':
            item.setBackground(QBrush(QColor(255, 255, 200)))  # Light yellow
        elif priority == 'Low':
            item.setBackground(QBrush(QColor(200, 255, 200)))  # Light green
        
        # Set the item text color for overdue tasks
        if deadline and deadline < datetime.now() and status != 'Completed':
            item.setForeground(QBrush(QColor(255, 0, 0)))  # Red for overdue
        
        # Set the item font for completed tasks
        if status == 'Completed':
            font = item.font()
            font.setStrikeOut(True)
            item.setFont(font)
        
        # Add the item to the list
        self.task_list.addItem(item)