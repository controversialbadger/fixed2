#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QCalendarWidget,
                           QListWidget, QListWidgetItem, QLabel, QPushButton,
                           QFrame, QSplitter)
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtGui import QColor, QBrush, QFont, QTextCharFormat

class CalendarDialog(QDialog):
    """Dialog for calendar integration with tasks"""
    
    def __init__(self, tasks, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Task Calendar")
        self.resize(900, 700)
        
        self.tasks = tasks
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QCalendarWidget {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QCalendarWidget QToolButton {
                color: #333;
                background-color: transparent;
                border: none;
                border-radius: 4px;
                padding: 4px;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #e0e0e0;
            }
            QCalendarWidget QMenu {
                background-color: white;
                border: 1px solid #d0d0d0;
            }
            QCalendarWidget QSpinBox {
                border: 1px solid #d0d0d0;
                border-radius: 2px;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel {
                font-weight: bold;
                color: #333;
            }
            QPushButton {
                background-color: #4a86e8;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #3a76d8;
            }
            QPushButton:pressed {
                background-color: #2a66c8;
            }
        """)
        
        self.setup_ui()
        self.populate_task_list()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Header with title
        header_label = QLabel("Task Calendar")
        header_label.setStyleSheet("font-size: 18px; margin-bottom: 10px;")
        main_layout.addWidget(header_label)
        
        # Create a splitter for resizable sections
        splitter = QSplitter(Qt.Horizontal)
        
        # Calendar widget
        calendar_frame = QFrame()
        calendar_layout = QVBoxLayout(calendar_frame)
        calendar_layout.setContentsMargins(0, 0, 0, 0)
        
        calendar_header = QLabel("Calendar")
        calendar_header.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
        calendar_layout.addWidget(calendar_header)
        
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.setSelectionMode(QCalendarWidget.SingleSelection)
        self.calendar.clicked.connect(self.date_selected)
        
        # Make the calendar cells larger
        self.calendar.setMinimumDate(QDate.currentDate().addMonths(-6))
        self.calendar.setMaximumDate(QDate.currentDate().addMonths(12))
        
        calendar_layout.addWidget(self.calendar)
        
        # Task list widget
        task_frame = QFrame()
        task_layout = QVBoxLayout(task_frame)
        task_layout.setContentsMargins(0, 0, 0, 0)
        
        task_header = QLabel("Tasks for Selected Date")
        task_header.setStyleSheet("font-size: 14px; margin-bottom: 5px;")
        task_layout.addWidget(task_header)
        
        self.task_list = QListWidget()
        self.task_list.setAlternatingRowColors(True)
        self.task_list.setSelectionMode(QListWidget.SingleSelection)
        self.task_list.setStyleSheet("""
            QListWidget::item {
                padding: 6px;
                border-bottom: 1px solid #e0e0e0;
            }
            QListWidget::item:selected {
                background-color: #e0e0ff;
                color: #333;
            }
            QListWidget::item:alternate {
                background-color: #f9f9f9;
            }
        """)
        
        task_layout.addWidget(self.task_list)
        
        # Add frames to splitter
        splitter.addWidget(calendar_frame)
        splitter.addWidget(task_frame)
        
        # Set initial sizes
        splitter.setSizes([450, 450])
        
        main_layout.addWidget(splitter)
        
        # Legend for task priorities
        legend_frame = QFrame()
        legend_frame.setStyleSheet("background-color: white; border: 1px solid #d0d0d0; border-radius: 4px; padding: 8px;")
        legend_layout = QHBoxLayout(legend_frame)
        
        legend_label = QLabel("Priority Legend:")
        legend_layout.addWidget(legend_label)
        
        # High priority
        high_color = QFrame()
        high_color.setStyleSheet("background-color: #ffc8c8; min-width: 20px; min-height: 20px; border-radius: 3px;")
        high_color.setFixedSize(20, 20)
        legend_layout.addWidget(high_color)
        legend_layout.addWidget(QLabel("High"))
        
        # Medium priority
        medium_color = QFrame()
        medium_color.setStyleSheet("background-color: #ffffc8; min-width: 20px; min-height: 20px; border-radius: 3px;")
        medium_color.setFixedSize(20, 20)
        legend_layout.addWidget(medium_color)
        legend_layout.addWidget(QLabel("Medium"))
        
        # Low priority
        low_color = QFrame()
        low_color.setStyleSheet("background-color: #c8ffc8; min-width: 20px; min-height: 20px; border-radius: 3px;")
        low_color.setFixedSize(20, 20)
        legend_layout.addWidget(low_color)
        legend_layout.addWidget(QLabel("Low"))
        
        # Calendar highlight
        calendar_color = QFrame()
        calendar_color.setStyleSheet("background-color: #c8e6ff; min-width: 20px; min-height: 20px; border-radius: 3px;")
        calendar_color.setFixedSize(20, 20)
        legend_layout.addWidget(calendar_color)
        legend_layout.addWidget(QLabel("Task Date"))
        
        legend_layout.addStretch()
        
        main_layout.addWidget(legend_frame)
        
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
        task_format = QTextCharFormat()
        task_format.setBackground(QBrush(QColor(200, 230, 255)))  # Light blue
        
        # Clear existing highlights by resetting all dates to default format
        # Instead of using clone() which doesn't exist, we use a new QTextCharFormat
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
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
        
        # Show a message if no tasks for the selected date
        if self.task_list.count() == 0:
            empty_item = QListWidgetItem("No tasks for this date")
            empty_item.setTextAlignment(Qt.AlignCenter)
            font = empty_item.font()
            font.setItalic(True)
            empty_item.setFont(font)
            empty_item.setForeground(QBrush(QColor(150, 150, 150)))
            self.task_list.addItem(empty_item)
    
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