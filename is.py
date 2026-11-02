import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QHBoxLayout, QGridLayout, QGroupBox
)
from PyQt5.QtGui import QFontDatabase, QFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import pickle
from geneticalgorithm2 import geneticalgorithm2 as ga


class DataAnaltics():
    def __init__(self):
        pass

class EnergyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Energy Prediction & Optimization')
        self.setStyleSheet("background-color: #0F172A; color: white;font-family: Montserrat; font-size: 18px;border-radius: 26px;")
        self.load_fonts()

        # Styles
        self.setFont(QFont('Montserrat', 10))

        glass_button_style = """
            QPushButton {
                background-color: rgba(255, 255, 255, 0.08);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 26px;
                padding: 20px;
                margin-top: 10px;
                font-size: 18px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
        """

        glass_groupbox_style = """
            QGroupBox {
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid rgba(255, 255, 255, 0.2);
                border-radius: 25px;
                padding: 10px;
                margin-top: 20px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                color: white;
                font-family: Montserrat;
                font-weight: bold;
                font-size: 28px;
                padding: 0 3px;
            }
        """

        glass_input_style = """
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.08);
                
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 6px;
                border-radius: 16px;
            }
        """

        # Layouts
        main_layout = QHBoxLayout()

        # Left Panel (Prediction)
        prediction_box = QGroupBox("Energy Prediction")
        prediction_box.setStyleSheet(glass_groupbox_style)
        prediction_layout = QVBoxLayout()

        form_layout = QGridLayout()
        labels = ['O2 (ppm) (%)', 'Anthracite (kg)', 'Graphite (%)', 'CLOCK (s)',
                  'Lime (%)', 'Dolomite LIME (%)', 'DRI F (%)', 'DIFF_TAP TO-START',
                  'WB_Tapping (%)', 'COKE EAF (g)', 'OZ_SML/X0 (Vm³/t)', 'DIFF_TME_TT END (s)']
        self.inputs = {}

        for i, label in enumerate(labels):
            lbl = QLabel(label)
            inp = QLineEdit()
            inp.setStyleSheet(glass_input_style)
            form_layout.addWidget(lbl, i, 0)
            form_layout.addWidget(inp, i, 1)
            self.inputs[label] = inp

        self.predict_button = QPushButton('Run Prediction')
        self.predict_button.setStyleSheet(glass_button_style)

        prediction_layout.addLayout(form_layout)
        prediction_layout.addWidget(self.predict_button)

        prediction_box.setLayout(prediction_layout)

        # Right Panel (Optimization)
        optimization_box = QGroupBox("Energy Optimization")
        optimization_box.setStyleSheet(glass_groupbox_style)
        optimization_layout = QVBoxLayout()

        self.figure, self.ax = plt.subplots(figsize=(5, 3))
        self.figure.set_facecolor((1, 1, 0, 1))
        self.canvas = FigureCanvas(self.figure)

        self.optimize_button = QPushButton('Run Optimization')
        self.optimize_button.setStyleSheet(glass_button_style)

        optimization_layout.addWidget(self.canvas)
        optimization_layout.addWidget(self.optimize_button)
        optimization_box.setLayout(optimization_layout)

        # Main Layout
        main_layout.addWidget(prediction_box)
        main_layout.addWidget(optimization_box)

        # Bottom Buttons Row
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(self.predict_button)
        buttons_layout.addWidget(self.optimize_button)

        main_vertical_layout = QVBoxLayout()
        main_vertical_layout.addLayout(main_layout)
        main_vertical_layout.addLayout(buttons_layout)

        self.setLayout(main_vertical_layout)

        # Connections
        self.optimize_button.clicked.connect(self.plot_graph)

    def load_fonts(self):
        # Load external font (Montserrat)
        font_id = QFontDatabase.addApplicationFont(r"C:\Users\office\Desktop\projects\Montserrat.ttf")
        if font_id == -1:
            print("Failed to load font.")

    def plot_graph(self):
        self.ax.clear()
        data = np.random.normal(90000, 10000, 1000)
        self.ax.hist(data, bins=30, color='#3B82F6')
        self.ax.axvline(np.mean(data), color='cyan', linestyle='--', label=f'Mean = {int(np.mean(data))}')
        self.ax.axvline(np.min(data), color='red', linestyle='--', label=f'Optimized = {int(np.min(data))}')
        self.ax.legend()
        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EnergyApp()
    ex.resize(1280, 720)
    ex.show()
    sys.exit(app.exec_())