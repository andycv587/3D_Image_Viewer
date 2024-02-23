# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 20:05:19 2024

@author: andys
"""
import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QFileDialog, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image
from scipy.optimize import curve_fit

class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.left = 10
        self.top = 10
        self.title = '3D Image Viewer'
        self.width = 960  # Adjusted for layout
        self.height = 480
        self.image_array = None
        self.mask = None
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        
        # Main widget and layout
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)
        layout = QVBoxLayout(self.widget)
        
        # Button layout
        buttonLayout = QHBoxLayout()
        layout.addLayout(buttonLayout)
        
        # Button Definitions
        self.buttonOpen = QPushButton('Open Image', self)
        self.buttonZoomIn = QPushButton('Zoom In', self)
        self.buttonZoomOut = QPushButton('Zoom Out', self)
        self.buttonFitCurve = QPushButton('Curve Fit', self)
        self.buttonSaveMask = QPushButton('Save Mask', self)
        
        # Button Connections
        self.buttonOpen.clicked.connect(self.openFileNameDialog)
        self.buttonZoomIn.clicked.connect(lambda: self.adjustZoom(True))
        self.buttonZoomOut.clicked.connect(lambda: self.adjustZoom(False))
        self.buttonFitCurve.clicked.connect(self.fitSurface)
        self.buttonSaveMask.clicked.connect(self.saveMaskDialog)
        
        # Add buttons to layout
        buttonLayout.addWidget(self.buttonOpen)
        buttonLayout.addWidget(self.buttonZoomIn)
        buttonLayout.addWidget(self.buttonZoomOut)
        buttonLayout.addWidget(self.buttonFitCurve)
        buttonLayout.addWidget(self.buttonSaveMask)
        
        # Initially disable buttons until an image is loaded
        self.setButtonsEnabled(False)
        
        # Matplotlib canvas
        self.canvas = FigureCanvas(Figure(figsize=(10, 3)))
        layout.addWidget(self.canvas)
    
    def setButtonsEnabled(self, enabled):
        # Enable buttons after execute 'Open Image'
        self.buttonZoomIn.setEnabled(enabled)
        self.buttonZoomOut.setEnabled(enabled)
        self.buttonFitCurve.setEnabled(enabled)
        self.buttonSaveMask.setEnabled(enabled and self.mask is not None)
    
    def saveMaskDialog(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getSaveFileName(self, "Save Mask", "", "PNG Files (*.png);;All Files (*)", options=options)
        if filePath:
            self.saveMask(filePath)
    
    def saveMask(self, filePath):
        if self.mask is not None:
            # Normalize and save the mask as suggested in previous examples
            mask_normalized = ((self.mask - np.min(self.mask)) / (np.max(self.mask) - np.min(self.mask)) * 255).astype(np.uint8)
            Image.fromarray(mask_normalized).save(filePath)
    
    def displayImage(self, imagePath):
        # Updated to enable buttons after an image is loaded
        image = Image.open(imagePath).convert('L')
        self.image_array = np.array(image)
        self.mask = None  # Reset mask
        self.canvas.figure.clf()
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')
        x = np.arange(0, self.image_array.shape[1])
        y = np.arange(0, self.image_array.shape[0])
        X, Y = np.meshgrid(x, y)
        Z = -self.image_array
        self.ax.plot_surface(X, Y, Z, cmap='gray', alpha=0.5)
        self.canvas.draw()
        self.setButtonsEnabled(True)

    # Other parts of the App class as previously defined...

    def openFileNameDialog(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Image", "", "All Files (*);;JPEG Files (*.jpg);;PNG Files (*.png)", options=options)
        if fileName:
            self.displayImage(fileName)

    def adjustZoom(self, zoom_in):
        if self.ax:
            xlim = self.ax.get_xlim()
            ylim = self.ax.get_ylim()
            zlim = self.ax.get_zlim()

            # Adjust limits by a factor to zoom in or out
            factor = 0.9 if zoom_in else 1.1
            
            self.ax.set_xlim([x*factor for x in xlim])
            self.ax.set_ylim([y*factor for y in ylim])
            self.ax.set_zlim([z*factor for z in zlim])
            
            self.canvas.draw()

    def fitSurface(self):
        if self.image_array is None:
            return
        
        # Define the curved surface model as before
        def model(xy, a, b, c, d, e, f):
            x, y = xy
            return a * x**2 + b * y**2 + c * x * y + d * x + e * y + f
        
        # Prepare data for curve_fit
        x = np.arange(0, self.image_array.shape[1])
        y = np.arange(0, self.image_array.shape[0])
        X, Y = np.meshgrid(x, y)
        Z = -self.image_array  # Ensure Z is the original 2D array of image data
        xy = np.vstack((X.flatten(), Y.flatten()))
        Z_flat = Z.flatten()  # Flatten Z for curve fitting
        
        # Fit the model to the data
        popt, _ = curve_fit(model, xy, Z_flat)
        
        # Calculate the fitted surface
        Z_fit = model(xy, *popt).reshape(X.shape)
        
        # Recalculate the mask if needed for visualization or processing
        self.mask = Z + Z_fit  # This operation is conceptual; ensure it aligns with your actual intent
        
        # Clear the current axes and plot both the original data and the fitted surface
        self.canvas.figure.clf()
        self.ax = self.canvas.figure.add_subplot(111, projection='3d')
        self.ax.plot_surface(X, Y, Z, cmap='gray', alpha=0.5)  # Original data plot
        self.ax.plot_surface(X, Y, Z_fit, cmap='viridis', alpha=0.5)  # Fitted surface plot
        
        self.canvas.draw()
        self.buttonSaveMask.setEnabled(True)


# Ensure the rest of the App class definition and the main execution block are included as before


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
