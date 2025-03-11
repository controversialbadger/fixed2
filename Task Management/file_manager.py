#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import uuid
import mimetypes
from PyQt5.QtWidgets import (QFileDialog, QMessageBox, QDialog, QVBoxLayout, 
                           QHBoxLayout, QLabel, QPushButton, QListWidget, 
                           QListWidgetItem, QDesktopWidget, QApplication)
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QIcon, QPixmap
import subprocess
import platform

class FileManager:
    """Class for managing file attachments"""
    
    def __init__(self, data_dir):
        """Initialize the file manager with the data directory"""
        self.data_dir = data_dir
        self.attachments_dir = os.path.join(data_dir, "attachments")
        
        # Create attachments directory if it doesn't exist
        if not os.path.exists(self.attachments_dir):
            try:
                os.makedirs(self.attachments_dir)
            except OSError as e:
                print(f"Error creating attachments directory: {str(e)}")
    
    def add_attachment(self, source_path):
        """
        Copy a file to the attachments directory and return the new path
        
        Args:
            source_path (str): Path to the source file
            
        Returns:
            str: Path to the copied file in the attachments directory
        """
        if not os.path.exists(source_path):
            return None
        
        # Generate a unique filename to avoid conflicts
        filename = os.path.basename(source_path)
        name, ext = os.path.splitext(filename)
        unique_name = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Create the destination path
        dest_path = os.path.join(self.attachments_dir, unique_name)
        
        try:
            # Copy the file
            shutil.copy2(source_path, dest_path)
            return dest_path
        except Exception as e:
            print(f"Error copying file: {str(e)}")
            return None
    
    def remove_attachment(self, file_path):
        """
        Remove a file from the attachments directory
        
        Args:
            file_path (str): Path to the file to remove
            
        Returns:
            bool: True if the file was removed successfully, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            os.remove(file_path)
            return True
        except Exception as e:
            print(f"Error removing file: {str(e)}")
            return False
    
    def clean_unused_attachments(self, unused_paths):
        """
        Remove unused attachment files
        
        Args:
            unused_paths (list): List of paths to unused files
            
        Returns:
            int: Number of files removed
        """
        count = 0
        for path in unused_paths:
            if self.remove_attachment(path):
                count += 1
        return count
    
    def get_file_icon(self, file_path):
        """
        Get an appropriate icon for a file based on its type
        
        Args:
            file_path (str): Path to the file
            
        Returns:
            QIcon: Icon for the file
        """
        # Get the file type
        mime_type, _ = mimetypes.guess_type(file_path)
        
        if mime_type is None:
            # Default icon for unknown file types
            return QApplication.style().standardIcon(QApplication.style().SP_FileIcon)
        
        if mime_type.startswith('image/'):
            # Use a small preview for images
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(QSize(32, 32), Qt.KeepAspectRatio, Qt.SmoothTransformation)
                return QIcon(pixmap)
        
        # Use standard icons based on mime type
        if mime_type.startswith('text/'):
            return QApplication.style().standardIcon(QApplication.style().SP_FileDialogContentsView)
        elif mime_type.startswith('audio/'):
            return QApplication.style().standardIcon(QApplication.style().SP_MediaVolume)
        elif mime_type.startswith('video/'):
            return QApplication.style().standardIcon(QApplication.style().SP_MediaPlay)
        elif mime_type == 'application/pdf':
            return QApplication.style().standardIcon(QApplication.style().SP_FileDialogDetailedView)
        elif 'spreadsheet' in mime_type or 'excel' in mime_type:
            return QApplication.style().standardIcon(QApplication.style().SP_FileDialogListView)
        elif 'word' in mime_type or 'document' in mime_type:
            return QApplication.style().standardIcon(QApplication.style().SP_FileDialogDetailedView)
        elif 'presentation' in mime_type or 'powerpoint' in mime_type:
            return QApplication.style().standardIcon(QApplication.style().SP_FileDialogDetailedView)
        
        # Default icon for other file types
        return QApplication.style().standardIcon(QApplication.style().SP_FileIcon)
    
    def open_file(self, file_path):
        """
        Open a file with the default application
        
        Args:
            file_path (str): Path to the file to open
            
        Returns:
            bool: True if the file was opened successfully, False otherwise
        """
        if not os.path.exists(file_path):
            return False
        
        try:
            # Open the file with the default application based on the OS
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', file_path])
            else:  # Linux and other Unix-like
                subprocess.call(['xdg-open', file_path])
            return True
        except Exception as e:
            print(f"Error opening file: {str(e)}")
            return False


class AttachmentDialog(QDialog):
    """Dialog for managing file attachments"""
    
    def __init__(self, parent=None, attachments=None, file_manager=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Attachments")
        self.resize(500, 400)
        
        self.attachments = attachments or []
        self.file_manager = file_manager
        
        self.setup_ui()
        self.populate_attachment_list()
    
    def setup_ui(self):
        """Setup the dialog UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Header with title
        header_label = QLabel("Manage Attachments")
        header_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(header_label)
        
        # Attachment list
        self.attachment_list = QListWidget()
        self.attachment_list.setAlternatingRowColors(True)
        self.attachment_list.setSelectionMode(QListWidget.SingleSelection)
        self.attachment_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #000;
            }
            QListWidget::item:alternate {
                background-color: #f9f9f9;
            }
        """)
        self.attachment_list.itemDoubleClicked.connect(self.open_attachment)
        main_layout.addWidget(self.attachment_list)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Add button
        add_button = QPushButton("Add File")
        add_button.setIcon(QIcon.fromTheme("document-new", 
                                         QApplication.style().standardIcon(QApplication.style().SP_FileDialogNewFolder)))
        add_button.clicked.connect(self.add_attachment)
        button_layout.addWidget(add_button)
        
        # Remove button
        remove_button = QPushButton("Remove")
        remove_button.setIcon(QIcon.fromTheme("edit-delete", 
                                            QApplication.style().standardIcon(QApplication.style().SP_TrashIcon)))
        remove_button.clicked.connect(self.remove_attachment)
        button_layout.addWidget(remove_button)
        
        # Open button
        open_button = QPushButton("Open")
        open_button.setIcon(QIcon.fromTheme("document-open", 
                                          QApplication.style().standardIcon(QApplication.style().SP_DialogOpenButton)))
        open_button.clicked.connect(self.open_selected_attachment)
        button_layout.addWidget(open_button)
        
        button_layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(button_layout)
    
    def populate_attachment_list(self):
        """Populate the attachment list with the current attachments"""
        self.attachment_list.clear()
        
        for attachment in self.attachments:
            if os.path.exists(attachment):
                item = QListWidgetItem()
                item.setText(os.path.basename(attachment))
                item.setToolTip(attachment)
                item.setIcon(self.file_manager.get_file_icon(attachment))
                self.attachment_list.addItem(item)
    
    def add_attachment(self):
        """Add a new attachment"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Select File", "", "All Files (*)"
        )
        
        if file_path:
            # Copy the file to the attachments directory
            new_path = self.file_manager.add_attachment(file_path)
            if new_path:
                self.attachments.append(new_path)
                self.populate_attachment_list()
            else:
                QMessageBox.warning(self, "Error", "Failed to add attachment.")
    
    def remove_attachment(self):
        """Remove the selected attachment"""
        selected_items = self.attachment_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an attachment to remove.")
            return
        
        item = selected_items[0]
        attachment_path = item.toolTip()
        
        # Confirm removal
        reply = QMessageBox.question(
            self, "Confirm Removal",
            f"Are you sure you want to remove '{item.text()}'?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove the attachment
            if attachment_path in self.attachments:
                self.attachments.remove(attachment_path)
                self.populate_attachment_list()
    
    def open_attachment(self, item):
        """Open the selected attachment"""
        attachment_path = item.toolTip()
        if not self.file_manager.open_file(attachment_path):
            QMessageBox.warning(self, "Error", f"Failed to open '{item.text()}'.")
    
    def open_selected_attachment(self):
        """Open the selected attachment"""
        selected_items = self.attachment_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an attachment to open.")
            return
        
        self.open_attachment(selected_items[0])
    
    def get_attachments(self):
        """Get the current list of attachments"""
        return self.attachments