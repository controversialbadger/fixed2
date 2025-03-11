#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
from datetime import datetime
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QVariant
from PyQt5.QtGui import QColor, QBrush, QFont

class TaskTableModel(QAbstractTableModel):
    """Table model for tasks"""
    
    # Column definitions
    COLUMNS = ['Title', 'Description', 'Priority', 'Status', 'Deadline', 'Reminder']
    
    # Column indices
    TITLE_COL = 0
    DESCRIPTION_COL = 1
    PRIORITY_COL = 2
    STATUS_COL = 3
    DEADLINE_COL = 4
    REMINDER_COL = 5
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tasks = []
    
    def rowCount(self, parent=QModelIndex()):
        """Return the number of rows"""
        return len(self.tasks)
    
    def columnCount(self, parent=QModelIndex()):
        """Return the number of columns"""
        return len(self.COLUMNS)
    
    def data(self, index, role=Qt.DisplayRole):
        """Return the data at the given index"""
        if not index.isValid() or not (0 <= index.row() < len(self.tasks)):
            return QVariant()
        
        task = self.tasks[index.row()]
        column = index.column()
        
        if role == Qt.DisplayRole:
            # Display data for each column
            if column == self.TITLE_COL:
                return task.get('title', '')
            elif column == self.DESCRIPTION_COL:
                return task.get('description', '')
            elif column == self.PRIORITY_COL:
                return task.get('priority', 'Medium')
            elif column == self.STATUS_COL:
                return task.get('status', 'Not Started')
            elif column == self.DEADLINE_COL:
                deadline = task.get('deadline')
                return deadline.strftime('%Y-%m-%d %H:%M') if deadline else ''
            elif column == self.REMINDER_COL:
                return task.get('reminder_offset', 'No Reminder')
        
        elif role == Qt.BackgroundRole:
            # Set background color based on priority
            priority = task.get('priority', 'Medium')
            if priority == 'High':
                return QBrush(QColor(255, 200, 200))  # Light red
            elif priority == 'Medium':
                return QBrush(QColor(255, 255, 200))  # Light yellow
            elif priority == 'Low':
                return QBrush(QColor(200, 255, 200))  # Light green
        
        elif role == Qt.ForegroundRole:
            # Set text color for overdue tasks
            deadline = task.get('deadline')
            if deadline and deadline < datetime.now() and task.get('status') != 'Completed':
                return QBrush(QColor(255, 0, 0))  # Red for overdue
        
        elif role == Qt.FontRole:
            # Set font for completed tasks
            if task.get('status') == 'Completed':
                font = QFont()
                font.setStrikeOut(True)
                return font
        
        elif role == Qt.UserRole:
            # Used for filtering
            if task.get('status') == 'Completed':
                return "completed"
            elif task.get('deadline') and task.get('deadline') < datetime.now() and task.get('status') != 'Completed':
                return "overdue"
            else:
                return "active"
        
        return QVariant()
    
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        """Return the header data"""
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.COLUMNS[section]
        return QVariant()
    
    def flags(self, index):
        """Return the item flags"""
        if not index.isValid():
            return Qt.NoItemFlags
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable
    
    def add_task(self, task_data):
        """Add a new task to the model"""
        self.beginInsertRows(QModelIndex(), len(self.tasks), len(self.tasks))
        self.tasks.append(task_data)
        self.endInsertRows()
    
    def update_task(self, row, task_data):
        """Update an existing task"""
        if 0 <= row < len(self.tasks):
            self.tasks[row] = task_data
            self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))
    
    def remove_task(self, row):
        """Remove a task from the model"""
        if 0 <= row < len(self.tasks):
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.tasks[row]
            self.endRemoveRows()
    
    def get_task(self, row):
        """Get a task by row index"""
        if 0 <= row < len(self.tasks):
            return self.tasks[row]
        return None
    
    def set_tasks(self, tasks):
        """Set the tasks list"""
        self.beginResetModel()
        self.tasks = tasks
        self.endResetModel()
    
    def mark_completed(self, row):
        """Mark a task as completed"""
        if 0 <= row < len(self.tasks):
            self.tasks[row]['status'] = 'Completed'
            self.tasks[row]['completed'] = True
            self.dataChanged.emit(self.index(row, 0), self.index(row, self.columnCount() - 1))
    
    def export_to_csv(self, filename):
        """Export tasks to a CSV file"""
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow(self.COLUMNS)
            
            # Write tasks
            for task in self.tasks:
                row = [
                    task.get('title', ''),
                    task.get('description', ''),
                    task.get('priority', 'Medium'),
                    task.get('status', 'Not Started'),
                    task.get('deadline').strftime('%Y-%m-%d %H:%M') if task.get('deadline') else '',
                    task.get('reminder_offset', 'No Reminder')
                ]
                writer.writerow(row)