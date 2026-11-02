import random
import sys
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtGui import QBrush, QPalette, QDoubleValidator
from PyQt5.QtWidgets import QFrame, QScrollArea
from PyQt5.QtCore import Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve, QSize
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox, QCheckBox,
    QProgressDialog, QFileDialog, QMessageBox, QInputDialog,
    QGraphicsBlurEffect, QGraphicsPixmapItem, QGraphicsScene,
    QGraphicsOpacityEffect, QMainWindow, QScrollArea
)
from PyQt5.QtGui import QIntValidator
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QFont, QColor, QImage
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal, QTimer, QRectF, QPropertyAnimation, QEasingCurve, QUrl
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from geneticalgorithm2 import geneticalgorithm2 as ga
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl

import re
import os
import base64
import fitz  # PyMuPDF
import shutil
import datetime

# Helper to access bundled resources both in dev and PyInstaller onefile
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.abspath('.'))
    return os.path.join(base_path, relative_path)

# ======================
# PDF Viewer Window
# ======================
class PDFViewerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SmartArc Program Help")
        self.setGeometry(100, 100, 1280, 1280)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        try:
            # Get the absolute path of the current script
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Try multiple possible locations for the PDF file
            possible_paths = [
                resource_path("help.pdf"),
                resource_path("help2.pdf"),
                os.path.join(current_dir, "help.pdf"),
                os.path.join(current_dir, "help2.pdf"),
                os.path.join(current_dir, "dist", "help.pdf"),
                os.path.join(current_dir, "dist", "help2.pdf"),
                os.path.join(current_dir, "Datas", "help.pdf"),
                os.path.join(current_dir, "Datas", "help2.pdf"),
                "help.pdf",
                "help2.pdf",
                "dist/help.pdf",
                "dist/help2.pdf",
                "Datas/help.pdf",
                "Datas/help2.pdf"
            ]
            
            pdf_path = None
            for path in possible_paths:
                if os.path.exists(path):
                    pdf_path = path
                    break
            
            if pdf_path is not None: 
                # Create scroll area
                scroll_area = QScrollArea()
                scroll_area.setWidgetResizable(True)
                layout.addWidget(scroll_area)
                
                # Create container widget for PDF pages
                container = QWidget()
                container_layout = QVBoxLayout(container)
                scroll_area.setWidget(container) 
                
                # Load and display PDF pages
                doc = fitz.Document(pdf_path)  # به جای fitz.open
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
                    img = QPixmap.fromImage(QImage(pix.samples, pix.width, pix.height, pix.stride, QImage.Format_RGB888))
 
                    # Create label for the page
                    page_label = QLabel()
                    page_label.setPixmap(img)
                    page_label.setAlignment(Qt.AlignCenter)
                    container_layout.addWidget(page_label)
                
                doc.close()
                
                # Add a close button
                close_button = QPushButton("Close Window")
                close_button.setStyleSheet(glass_button_style)
                close_button.clicked.connect(self.close)
                layout.addWidget(close_button, alignment=Qt.AlignCenter)
                
            else:
                # Show more detailed error message with searched paths
                searched_paths = "\n".join([f"- {path}" for path in possible_paths])
                self.show_error(f"PDF file 'help.pdf' or 'help2.pdf' not found!\n\nSearched in the following locations:\n{searched_paths}\n\nPlease make sure the file exists in one of these locations.")
        except Exception as e:
            self.show_error(f"Error loading PDF: {str(e)}")
        
        # Set window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: rgba(15, 23, 42, 0.8);
            }
            QScrollArea {
                background-color: white;
                border: none;
            }
            QLabel {
                background-color: white;
            }
        """)

    def show_error(self, message):
        error_label = QLabel(message)
        error_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 16px;
                background-color: rgba(15, 23, 42, 0.8);
                padding: 20px;
                border-radius: 10px;
            }
        """)
        error_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(error_label)

# ======================
# سبک‌ها
# ======================
main_style = """
    color: white;
    font-family: Montserrat; font-size: 18px;
    border-radius: 26px;
"""
glass_button_style = """
QPushButton, QCheckBox {
    background-color: rgba(15, 23, 42,  0.8);
    color: white;
    border:3px solid rgba(255,255,255,0.5);
    border-radius:16px;
    padding:8px; margin:5px; font-size:18px;
}
QPushButton:hover, QCheckBox:hover {
    background-color: rgba(255,255,255,0.2);
}
"""
glass_groupbox_style = """
QGroupBox {
    margin-right: 20px;
    margin-left: 20px;
    background-color: rgba(238, 78, 0, 0.2);
    border:3px solid rgba(255,255,255,0.5);
    border-radius:30px; padding:15px; margin-top:20px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    color: white;
    font-size: 45px;         /* اندازه‌ی دلخواه */
    padding: 5px 20px;       /* فضای داخل عنوان */
}
"""
glass_input_style = """
QLineEdit {
    background-color: rgba(15, 23, 42,  0.6);
    color: white;
    margin-right: 20px;
    margin-left: 20px;
    border:1px solid rgba(255,255,255,0.6);
    padding:6px; border-radius:16px;
}


QLabel {
    background-color: rgba(20, 23, 42,  0.4);
    color: white;
    font-size: 12px;
    margin-right: 5px;
    margin-left: 5px;
    border:1px solid rgba(255,255,255,0.6);
    padding:6px; border-radius:16px;
}
"""

# پارامترهای GA


# ======================
# کلاس DataAnalytics
# ======================
class DataAnalytics:
    def __init__(self,
                 model_path='random_forest_model_final_newRange.pkl',
                 data_path='app_data.bak'):
        with open(resource_path(model_path), 'rb') as f:
            self.model = pickle.load(f)
        self.ga_params = {
            'max_num_iteration': 100,
            'population_size': 100,
            'mutation_probability': 0.2,
            'elit_ratio': 0.01,
            'crossover_type': 'uniform',
            'parents_portion': 0.3,
            'max_iteration_without_improv': None
        }
        
        self.feature_map = {
            'HEEL_NO': 'HEEL NO',
            'GRAPHIT_LANCE_EAF': 'GRAPHIT LANCE (KG)',
            'TAP_TO_TAP_SS': 'TAP TO TAP START (S)',
            'TAP_WEI_TON': 'TAP WEI (TON)',
            'TAP_TEMP_EAF': 'TAP TEMP (C)',
            'FIRST_TEMP_EAF': 'FIRST TEMP (C)',
            'SCRAP_WEI_EAF': 'SCRAPE (KG)',
            'DRI_EAF': 'DRI (TON)',
            'POWER_ON_TAP': 'POWER ON TAP (S)',
            'OXCYGEN_EAF': 'OXCYGEN (NM^3)',
            'LIME_EAF': 'LIME (KG)',
            'DOLOMIT_LIME_EAF': 'LIME DOLOMIT (KG)',
            'COFE_COKE_EAF': 'COFE COKE (KG)',
            'GAS_MEATN_EAF': 'GAS MEATN (NM^3)',
        }
        # Use actual data ranges as shown in UI labels
        self.input_ranges = {
            "HEEL NO": (0, 1),
            "GRAPHIT LANCE (KG)": (0.0, 1500.0),
            "TAP TO TAP START (S)": (3601.0, 6598.0),
            "TAP WEI (TON)": (180.0, 200.0),
            "TAP TEMP (C)": (1577.0, 1660.0),
            "FIRST TEMP (C)": (1560.0, 1670.0),
            "SCRAPE (KG)": (0.0, 60000.0),
            "DRI (TON)": (180.0, 250.0),
            "POWER ON TAP (S)": (3000.0, 4500.0),
            "OXCYGEN (NM^3)": (4531.0, 7960.0),
            "LIME (KG)": (6010.0, 11794.4),
            "LIME DOLOMIT (KG)": (5000.0, 9000.0),
            "COFE COKE (KG)": (0.0, 1000.0),
            "GAS MEATN (NM^3)": (400.0, 800.0),
        }

        # Align features with model and dataset
        self.expected_features = list(self.model.feature_names_in_)
        self.feature_importances_ = pd.Series(
            self.model.feature_importances_,
            index=self.expected_features
        ).sort_values()

        df_raw = pd.read_excel(resource_path(data_path))
        if 'ENERGY_TOT_EAF' in df_raw.columns:
            self.Tot_e = df_raw['ENERGY_TOT_EAF'].dropna().values
        else:
            self.Tot_e = np.array([])

        drop_cols = ['HEAT', 'DAT_EN', 'ENERGY_TOT_EAF', 'ENERGY_TOT_EAF_PER_TON', 'GRD_CLAS_EAF']
        drop_existing = [c for c in drop_cols if c in df_raw.columns]
        df_vars = df_raw.drop(columns=drop_existing)

        # Order/select columns to match model feature order (robust)
        if hasattr(self.model, 'feature_names_in_'):
            features_in_both = [f for f in self.model.feature_names_in_ if f in df_vars.columns]
            self.df_vars = df_vars[features_in_both].copy()
            self.expected_features = features_in_both
        else:
            self.df_vars = df_vars.copy()
            self.expected_features = list(self.df_vars.columns)

        # Keep input ranges as predefined - no override from dataset
        # This ensures consistency between UI validation and optimization bounds

        # Skip loading optional external fixed inputs (removed per user request)
        self.external_fixed = {}


    def predict_row_from_dataset(self, row_index):
        # Predict a specific row from the original dataset using GA final logic
        df_all = pd.read_excel(resource_path('app_data.bak'))
        actual_value = None
        if 'ENERGY_TOT_EAF' in df_all.columns and row_index < len(df_all):
            try:
                actual_value = float(df_all['ENERGY_TOT_EAF'].iloc[row_index])
            except Exception:
                actual_value = None
        drop_cols = ['HEAT', 'DAT_EN', 'ENERGY_TOT_EAF', 'ENERGY_TOT_EAF_PER_TON', 'GRD_CLAS_EAF']
        drop_existing = [c for c in drop_cols if c in df_all.columns]
        df_vars = df_all.drop(columns=drop_existing)
        if row_index >= len(df_vars):
            raise IndexError('Row index out of range for dataset')
        row = df_vars.iloc[row_index].copy()
        # Apply external fixed overrides
        for col, val in getattr(self, 'external_fixed', {}).items():
            if col in row.index:
                row[col] = val
        # Align to model features
        features = self.expected_features
        x = pd.DataFrame([row[features]], columns=features)
        pred = float(self.model.predict(x)[0])
        return pred, actual_value, row
 
    def predict(self, inputs, use_constraints=False):
        vals, self.last_input_values = [], {}
        for feat in self.expected_features:
            label = self.feature_map.get(feat)
            v = 0.0
            if label in inputs and inputs[label] is not None:
                try:
                    v = float(inputs[label].text())
                except:
                    v = 0.0
            if use_constraints:
                # Apply external fixed constraints (override user entry)
                if feat in getattr(self, 'external_fixed', {}):
                    v = self.external_fixed[feat]
            vals.append(v)
            self.last_input_values[feat] = v

        df_pred = pd.DataFrame([vals], columns=self.expected_features)
        self.last_prediction = float(self.model.predict(df_pred)[0])
        return self.last_prediction

    def optimize_energy(self):
        # Follow GA_RF_Energy_Final.py logic exactly
        print("DEBUG: Starting optimize_energy")
        def log_and_alert(message):
            try:
                # write to a simple log file next to executable (or cwd)
                with open(os.path.join(os.getcwd(), 'smartarc_log.txt'), 'a', encoding='utf-8') as f:
                    f.write(message + "\n")
            except Exception:
                pass
            try:
                QMessageBox.critical(None, "Optimization Error", message)
            except Exception:
                pass
        
        # Optional fixed inputs file removed; use empty DataFrame
        fixed_inputs_df = pd.DataFrame()
        
        # Add UI fixed values from static mode to fixed_inputs_df
        ui_fixed = getattr(self, 'ui_fixed', {})
        print(f"DEBUG: UI fixed values: {ui_fixed}")
        if ui_fixed:
            # If no file-based fixed inputs, create DataFrame from UI values
            if fixed_inputs_df.empty:
                fixed_inputs_df = pd.DataFrame([ui_fixed])
                print(f"DEBUG: Created fixed_inputs_df from UI: {fixed_inputs_df}")
            else:
                # Combine with file-based fixed inputs (UI takes precedence)
                for col, val in ui_fixed.items():
                    fixed_inputs_df[col] = val
                print(f"DEBUG: Combined fixed_inputs_df: {fixed_inputs_df}")
        
        # Create variable bounds exactly like GA_RF_Energy_Final.py
        if self.df_vars is None or self.df_vars.shape[1] == 0:
            raise ValueError("No variables available for optimization. Check model features vs dataset columns.")

        varbound = np.array([[self.df_vars[col].min(), self.df_vars[col].max()] 
                            for col in self.df_vars.columns], dtype=float)
        # Validate bounds: replace invalid/NaN/inverted bounds
        for i in range(varbound.shape[0]):
            lo, hi = varbound[i]
            if not np.isfinite(lo) or not np.isfinite(hi) or hi < lo or lo == hi:
                varbound[i] = [0.0, 1.0]
        
        # Update bounds for fixed inputs (exactly like GA_RF_Energy_Final.py)
        for var in fixed_inputs_df.columns:
            if var in self.df_vars.columns:
                idx = self.df_vars.columns.get_loc(var)
                val = fixed_inputs_df[var].iloc[-1]
                varbound[idx] = [val, val]
        
        # Define objective function exactly like GA_RF_Energy_Final.py
        def objective_function(individual):
            inputs = pd.DataFrame([individual], columns=self.df_vars.columns)
            
            # Apply fixed inputs (exactly like GA_RF_Energy_Final.py)
            for var in fixed_inputs_df.columns:
                if var in inputs.columns:
                    inputs[var] = fixed_inputs_df[var].iloc[-1]
            
            # Predict using the Random Forest model
            return float(self.model.predict(inputs)[0])
        
        # Run GA with exact same parameters as GA_RF_Energy_Final.py
        try:
            print(f"DEBUG: Running GA with dimension={len(self.df_vars.columns)}, varbound shape={varbound.shape}")
            model = ga(
                function=objective_function,
                dimension=len(self.df_vars.columns),
                variable_type='real',
                variable_boundaries=varbound,
                algorithm_parameters=self.ga_params
            )
            # Disable internal GA progress output and guard against None stdout/stderr in GUI builds
            class _DummyStream:
                def write(self, *args, **kwargs):
                    return 0
                def flush(self):
                    return None
            old_stdout, old_stderr = getattr(sys, 'stdout', None), getattr(sys, 'stderr', None)
            try:
                if old_stdout is None:
                    sys.stdout = _DummyStream()
                if old_stderr is None:
                    sys.stderr = _DummyStream()
                model.run(no_plot=True, progress_bar_stream=None)
            finally:
                # Restore original streams if they existed
                try:
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr
                except Exception:
                    pass
            print(f"DEBUG: GA completed successfully")
            return float(model.result['score']), list(model.result['variable'])
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            msg = f"ERROR in GA optimization: {e}\n\n{tb}"
            print(msg)
            log_and_alert(msg)
            # Return a fallback result
            return 0.0, [0.0] * len(self.df_vars.columns)


# ======================
# Worker برای بهینه‌سازی GA
# ======================
class OptimizeWorker(QObject):
    finished = pyqtSignal(object)

    def __init__(self, analytics):
        super().__init__()
        self.analytics = analytics

    def run(self):
        try:
            result = self.analytics.optimize_energy()
        except Exception as e:
            print("Error in OptimizeWorker: ", e)
            import traceback
            traceback.print_exc()  
            result = ("Error", [])
        self.finished.emit(result)


# ======================
# Worker برای پیش‌بینی فایل
# ======================
class PredictFileWorker(QObject):
    finished = pyqtSignal(pd.DataFrame)
    def __init__(self, analytics, df, feature_map):
        super().__init__()
        self.analytics = analytics
        self.df = df.copy()
        self.feature_map = feature_map

    def run(self):
        results = []
        for _, row in self.df.iterrows():
            # شبیه‌سازی ورودی‌های QLineEdit
            class Dummy:
                def __init__(self, v): self.v = v
                def text(self): return str(self.v)
            inputs = {}
            for feat, label in self.feature_map.items():
                inputs[label] = Dummy(row[feat]) if feat in row else None
            results.append(self.analytics.predict(inputs))

        self.df['Predicted_Energy'] = results
        self.finished.emit(self.df)


# ======================
# کلاس اصلی اپ
# ======================
class EnergyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.data_analytics = DataAnalytics()
        self.loaded_df = None
        self.static_checkboxes = {}  
        self.initUI()
        

    def style_units(self, text):
        # به جای پیدا کردن تمامی عبارات داخل پرانتز، مثال زیر همه موارد را تغییر می‌دهد.
        # عبارت داخل پرانتز (به صورت غیر حریص) را پیدا و آن را در یک span با رنگ قرمز قرار می‌دهد.
        styled_text = re.sub(r'(\(.*?\))', r'<span style="color: red; font-size: 12px;">\1</span>', text)
        return styled_text
    
    def format_range_text(self, label, min_val, max_val):
        # Only format LIME (KG) range to one decimal place
        if label == "LIME (KG)":
            return f"[{min_val:.1f}, {max_val:.1f}]"
        return f"[{min_val}, {max_val}]"
    
    def initUI(self):
        self.setWindowTitle('SmartArc - Energy Prediction & Optimization')
        self.setStyleSheet(main_style)
        pixmap = QPixmap(resource_path("core.png"))   # مسیر تصویرت
        palette = QPalette()
        # تصویر را به‌عنوان برس برای حالت Window (کل پنجره) قرار بده
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)
        self.setAutoFillBackground(True)     # حتماً فعال باشد
        main_layout = QHBoxLayout()

        # ---- Prediction Box ----
        self.pred_box = QGroupBox("Inputs")
        self.pred_box.setStyleSheet(glass_groupbox_style)
        self.pred_box.setFixedSize(720, 1500)

        p_layout = QVBoxLayout()
        self.pre_grid = QGridLayout()
        self.inputs = {}
        self.input_rows = {}

        for i, label in enumerate(self.data_analytics.feature_map.values()):

            lbl = QLabel(label)
            lbl.setTextFormat(Qt.RichText) 
            lbl.setStyleSheet("""
background-color: rgba(15, 23, 42,  0.3);
    font-size: 15px;
    color: white;
    margin-right: 20px;
    margin-left: 20px;
    border:2px solid rgba(255,255,255,0.4);
    border-color: black;
    padding:6px; 
     border-radius:15px;
""")
            min_val, max_val = self.data_analytics.input_ranges[label]
            if label in self.data_analytics.input_ranges:
                

                styled_label_text = self.style_units(label)
                range_str = self.format_range_text(label, min_val, max_val)
                lbl.setText(f"{styled_label_text} <span style='color: grey; '>{range_str}</span>")
                # ایجاد و ست کردن QIntValidator برای ورودی
                if label == "HEEL NO":
                    validator = QIntValidator(int(min_val), int(max_val))
                else:
                    validator = QDoubleValidator(float(min_val), float(max_val),  20)
                
            else:
                validator = None
            static_check = QCheckBox()
            static_check.setVisible(False)  # ابتدا مخفی باشد
            static_check.stateChanged.connect(lambda state, l=label: self.update_static_label(l, state))
            self.static_checkboxes[label] = static_check


            le = QLineEdit()
            # No default value - user must enter their own values
            le.setStyleSheet(glass_input_style)
            if validator is not None:
                le.setValidator(validator)
            
            # Add special handling for HEEL NO to auto-convert float to int
            if label == "HEEL NO":
                le.textChanged.connect(lambda text, l=label: self.on_heel_no_changed(l, text))
            else:
                le.textChanged.connect(lambda text, l=label: self.on_input_changed(l, text))
            lbl.setAlignment(Qt.AlignCenter)

            self.pre_grid.addWidget(lbl, i, 0)
            self.pre_grid.addWidget(static_check, i, 4)
            self.pre_grid.addWidget(le, i, 1)
            self.inputs[label] = le
            self.input_rows[label] = i

        self.file_box = QGroupBox("")
        self.file_box.setStyleSheet(glass_groupbox_style)
        self.file_box.setFixedSize(500, 300)  # Increased height to accommodate larger buttons
        f_layout = QVBoxLayout()
        self.file_status_label = QLabel("No file loaded.")
        self.file_status_label.setAlignment(Qt.AlignCenter)
        self.file_status_label.setStyleSheet(
            'margin:10px 0; font-size:22px; '
            'background-color: rgba(15, 23, 42, 0.4); '
            'border-radius: 10px; padding:8px;'
        )
        btn_load = QPushButton("Load Excel Data")
        btn_load.setStyleSheet(glass_button_style)
        btn_load.setFixedSize(400, 50)  # Set fixed size for buttons
        btn_load.clicked.connect(self.load_input_file)
        
        btn_open_excel = QPushButton("*** [HELP] Data Example (Excel)")
        btn_open_excel.setStyleSheet(glass_button_style)
        btn_open_excel.setFixedSize(400, 50)  # Set fixed size for buttons
        btn_open_excel.clicked.connect(self.open_fixed_excel)

        btn_program_help = QPushButton("Program Help")

        btn_program_help.setStyleSheet(glass_button_style)
        btn_program_help.setFixedSize(400, 50)  # Set fixed size for buttons
        btn_program_help.clicked.connect(self.open_program_help)

        copyright = QLabel("")
        copyright.setStyleSheet("color: white; font-size: 13px; margin-top: 20px;")
        
        f_layout.addWidget(btn_load, alignment=Qt.AlignCenter)
        f_layout.addWidget(self.file_status_label, alignment=Qt.AlignCenter)
        f_layout.addWidget(btn_open_excel, alignment=Qt.AlignCenter)
        f_layout.addWidget(btn_program_help, alignment=Qt.AlignCenter)
        f_layout.addWidget(copyright, alignment=Qt.AlignCenter)
        self.file_box.setLayout(f_layout)

        
        # Canvas for GA histogram is created later in the Optimization Box section

        cb_layout = QHBoxLayout()
        
        #self.imp_cb = QCheckBox('Feature Importances')
        self.te_cb  = QCheckBox('Estimated Total Energy')
        #self.tr_cb  = QCheckBox('True Total Energy')

        self.te_cb.setStyleSheet("""
QPushButton, QCheckBox {
    background-color: rgba(15, 23, 42,  0.6);
    color: white;
    border:2px solid rgba(255,255,255,0.8);
    border-radius:14px;
    padding:5px; margin:2px; font-size:14px;
}
QPushButton:hover, QCheckBox:hover {
    background-color: rgba(255,255,255,0.2);
}
""")
        cb_layout.addWidget(self.te_cb)

        # btn_pred = QPushButton("Run Prediction")
        # btn_pred.setStyleSheet(glass_button_style)
        # btn_pred.clicked.connect(self.run_prediction)

        # self.result_label = QLabel("Predicted:")
        # self.result_label.setAlignment(Qt.AlignCenter)
        # self.result_label.setStyleSheet(
        #     'margin:10px; font-size:21px; '
        #     'background-color: rgba(15, 23, 42, 0.4); '
        #     'border-radius: 15px; padding:10px;'
        # )

        p_layout.addLayout(self.pre_grid)
        #p_layout.addLayout(cb_layout)
        #p_layout.addWidget(btn_pred, alignment=Qt.AlignCenter)
        p_layout.addWidget(self.file_box, alignment=Qt.AlignCenter)
        #p_layout.addWidget(self.result_label)
        self.pred_box.setLayout(p_layout)

        # ---- Optimization Box ----
        opts_box = QGroupBox("Prediction")
        opts_box.setStyleSheet(glass_groupbox_style)
        self.file_box.setFixedSize(600, 300)
        o_layout = QVBoxLayout()
        self.figure2, self.ax2 = plt.subplots(figsize=(10,8), dpi=100)
        self.canvas2 = FigureCanvas(self.figure2)
        self.canvas2.setMinimumSize(500, 400)

        from PyQt5.QtWidgets import QSizePolicy
        self.canvas2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        semi_green = (0.2, 0.7, 0.0, 0)
        semi_orange = (1, 1, 1, 0.3)
        self.figure2.patch.set_facecolor(semi_green)
        self.ax2.patch.set_facecolor(semi_orange)
        # اگر لازم بود برای FigureCanvas هم قابل شفاف شدن


        self.canvas2.setStyleSheet("background:transparent; border-radius: 25px;")
        self.canvas2.setAttribute(Qt.WA_TranslucentBackground)
        # Past Data Checker


        btn_download_pdf_pred = QPushButton("Download PDF")
        btn_download_pdf_pred.setStyleSheet(glass_button_style)
        btn_download_pdf_pred.clicked.connect(self.download_pdf_pred)


        btn_download_png_pred = QPushButton("Download PNG")
        btn_download_png_pred.setStyleSheet(glass_button_style)
        btn_download_png_pred.clicked.connect(self.download_png_pred)


        btn_pre = QPushButton("Run Prediction")

        btn_pre.setStyleSheet(glass_button_style)
        btn_pre.clicked.connect(self.run_prediction)

        self.result_label = QLabel("Predicted: Not Cullected Yet!")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(
            'margin:10px; font-size:21px; '
            'background-color: rgba(15, 23, 42, 0.4); '
            'border-radius: 15px; padding:10px;'
        )

        frame1 = QFrame()
        frame1.setStyleSheet("""
            QFrame {
                background-color: rgba(238, 78, 0, 0.3);
                border-radius: 26px;
                border:2px solid rgba(255,255,255,0.8);
                            color: white;
            }
        """)

        frame1.setLayout(QVBoxLayout())
        frame1.layout().setContentsMargins(0,0,0,0)
        frame1.layout().setAlignment(Qt.AlignCenter)
        frame1.layout().addWidget(self.canvas2)
        frame1.layout().addWidget(btn_download_pdf_pred)
        frame1.layout().addWidget(self.result_label)
        frame1.layout().addWidget(btn_pre, alignment=Qt.AlignCenter)

        opt_box = QGroupBox("Energy Optimization")
        opt_box.setStyleSheet(glass_groupbox_style)
        o_layout = QVBoxLayout()
        self.figure1, self.ax1 = plt.subplots(figsize=(10,8), dpi=100)
        self.canvas1 = FigureCanvas(self.figure1)

        self.canvas1.setMinimumSize(500, 400)

        from PyQt5.QtWidgets import QSizePolicy
        self.canvas1.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        semi_green = (0.2, 0.7, 0.0, 0)
        semi_orange = (1, 1, 1, 0.3)
        self.figure1.patch.set_facecolor(semi_green)
        self.ax1.patch.set_facecolor(semi_orange)
        # اگر لازم بود برای FigureCanvas هم قابل شفاف شدن
        
        self.canvas1.setStyleSheet("background:transparent; border-radius: 25px;")
        self.canvas1.setAttribute(Qt.WA_TranslucentBackground)
        # Past Data Checker
        btn_download_pdf_opt = QPushButton("Download PDF")
        btn_download_pdf_opt.setStyleSheet(glass_button_style)
        btn_download_pdf_opt.clicked.connect(self.download_pdf_opt)


        btn_download_png_opt = QPushButton("Download PNG")
        btn_download_png_opt.setStyleSheet(glass_button_style)

        btn_download_png_opt.clicked.connect(self.download_png_opt)

        btn_export_excel = QPushButton("Export Excel (Optimized)")
        btn_export_excel.setStyleSheet(glass_button_style)
        btn_export_excel.clicked.connect(self.export_optimized_data)

        ga_label = QLabel("GA AI NUM. (Max Num Iteration) [20, 100]")
        ga_label.setStyleSheet("color: white; font-size: 16px;")
        # استفاده از QLineEdit به همراه QIntValidator برای دریافت مقادیر عددی صحیح
        self.ga_iterations_input = QLineEdit()
        self.ga_iterations_input.setText("20")
        
        self.ga_iterations_input.setValidator(QIntValidator(20, 100))
        self.ga_iterations_input.setStyleSheet(glass_input_style)
        self.static_checkbox = QCheckBox("Static Mode")
        self.static_checkbox.setStyleSheet("color: white; font-size: 16px;")
        self.static_checkbox.stateChanged.connect(self.toggle_static_mode)
        
        # Add Select All and Deselect All buttons under Static Mode
        self.select_all_static_btn = QPushButton("Select All Static")
        self.select_all_static_btn.setStyleSheet(glass_button_style)
        self.select_all_static_btn.clicked.connect(self.select_all_static)
        self.select_all_static_btn.setVisible(False)  # Initially hidden
        
        self.deselect_all_static_btn = QPushButton("Deselect All Static")
        self.deselect_all_static_btn.setStyleSheet(glass_button_style)
        self.deselect_all_static_btn.clicked.connect(self.deselect_all_static)
        self.deselect_all_static_btn.setVisible(False)  # Initially hidden
    
        btn_opt = QPushButton("Run Optimization")

        btn_opt.setStyleSheet(glass_button_style)
        btn_opt.clicked.connect(self.run_optimization)

        self.opt_result_label = QLabel("Optimized Energy: Not Calculated Yet!")
        self.opt_result_label.setAlignment(Qt.AlignCenter)
        self.opt_result_label.setStyleSheet(
            
            'background-color: rgba(15, 23, 42, 0.5); '+
            'margin:5px; font-size:21px;'+
            'border-radius: 15px; padding:2px;'

        )

        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: rgba(238, 78, 0, 0.3);
                border-radius: 26px;
                border:2px solid rgba(255,255,255,0.8);
                            color: white;
            }
        """)
        frame.setLayout(QVBoxLayout())

        frame.layout().setContentsMargins(0,0,0,0)
        frame.layout().setAlignment(Qt.AlignCenter)
        frame.layout().addWidget(self.canvas1)
        frame.layout().addWidget(btn_download_pdf_opt)
        frame.layout().addWidget(btn_export_excel)
        frame.layout().addWidget(ga_label)
        frame.layout().addWidget(self.ga_iterations_input)
        frame.layout().addWidget(self.opt_result_label)
        frame.layout().addWidget(self.static_checkbox, alignment=Qt.AlignCenter)
        frame.layout().addWidget(self.select_all_static_btn, alignment=Qt.AlignCenter)
        frame.layout().addWidget(self.deselect_all_static_btn, alignment=Qt.AlignCenter)
        frame.layout().addWidget(btn_opt, alignment=Qt.AlignCenter)

        # سپس به جای اضافه‌کردن مستقیم self.canvas،
        # همین frame را به layout مربوط به Optimization Box اضافه کن:
#         self.help = QLabel("""
# Program Help:

# >> Real-Time Section <<
# --------------------------------
# In this section, the user can manually input values 
# and instantly receive results or analysis.  
# It is useful for quick and on-the-spot evaluations.

# >> Past-Time Section <<
# --------------------------------
# This section allows the user to upload an output file 
# (e.g., a data log). The program processes the file 
# and provides results based on historical data.

# """)
#         self.help.setAlignment(Qt.AlignLeft)
#         self.help.setStyleSheet(
            
#             'background-color: rgba(15, 23, 42, 0.6); '+
#             'margin:5px; font-size:18px;'+
#             'border-radius: 15px; padding:5px;'

#         )
#         self.help.setFixedSize(opt_box.size())
        
        o_layout.addWidget(frame1)
        o_layout.addWidget(frame)
        #o_layout.addWidget(self.help, alignment=Qt.AlignCenter)
        opt_box.setLayout(o_layout)

        main_layout.addWidget(self.pred_box)
        main_layout.addWidget(opt_box)
        
        self.setLayout(main_layout)

    def download_pdf_pred(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
            if filename:
                from matplotlib.backends.backend_pdf import PdfPages
                with PdfPages(filename) as pdf:
                    # ایجاد یک figure جدید برای همه محتوا
                    fig = plt.figure(figsize=(12, 16))
                    
                    # اضافه کردن مقادیر ورودی
                    input_text = "Input Values:\n\n"
                    for label in self.data_analytics.feature_map.values():
                        if label in self.inputs:
                            value = self.inputs[label].text()
                            input_text += f"{label}: {value}\n"
                    
                    plt.figtext(0.1, 0.95, input_text, fontsize=10, va='top')
                    
                    # اضافه کردن نمودار پیش‌بینی
                    plt.subplot(2, 1, 1)
                    plt.hist(self.data_analytics.Tot_e, bins=30, edgecolor='black')
                    plt.axvline(
                        self.data_analytics.last_prediction,
                        color='red', linestyle='--',
                        label=f"User Prediction: {int(self.data_analytics.last_prediction)} KWh"
                    )
                    plt.legend()
                    plt.title("Total Energy Distribution (Prediction)")
                    plt.xlabel("Total Energy (KWh)")
                    plt.ylabel("Frequency")
                    
                    # اضافه کردن نمودار بهینه‌سازی اگر وجود دارد
                    if hasattr(self, 'optimized_result') and self.optimized_result is not None:
                        best, _ = self.optimized_result
                        plt.subplot(2, 1, 2)
                        plt.hist(self.data_analytics.Tot_e, bins=30, edgecolor='black')
                        plt.axvline(
                            self.data_analytics.last_prediction,
                            color='red', linestyle='--',
                            label=f"User Prediction: {int(self.data_analytics.last_prediction)} KWh"
                        )
                        plt.axvline(best, color='green', linestyle='-.', 
                                  label=f"Optimized: {int(best)} KWh")
                        plt.legend()
                        plt.title("Total Energy Distribution (Optimization)")
                        plt.xlabel("Total Energy (KWh)")
                        plt.ylabel("Frequency")
                    
                    plt.tight_layout()
                    pdf.savefig(fig)
                    plt.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF: {str(e)}")

    def download_png_pred(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save PNG", "", "PNG Files (*.png)")
            if filename:
                # ذخیره نمودار پیش‌بینی به صورت PNG
                self.figure2.savefig(filename, format="png")
        except:
            pass

    def download_pdf_opt(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save PDF", "", "PDF Files (*.pdf)")
            if filename:
                from matplotlib.backends.backend_pdf import PdfPages
                with PdfPages(filename) as pdf:
                    # ایجاد یک figure جدید برای همه محتوا
                    fig = plt.figure(figsize=(12, 16))
                    
                    # اضافه کردن مقادیر ورودی
                    input_text = "Input Values:\n\n"
                    for label in self.data_analytics.feature_map.values():
                        if label in self.inputs:
                            value = self.inputs[label].text()
                            input_text += f"{label}: {value}\n"
                    
                    plt.figtext(0.1, 0.95, input_text, fontsize=10, va='top')
                    
                    # اضافه کردن نمودار پیش‌بینی
                    plt.subplot(2, 1, 1)
                    plt.hist(self.data_analytics.Tot_e, bins=30, edgecolor='black')
                    plt.axvline(
                        self.data_analytics.last_prediction,
                        color='red', linestyle='--',
                        label=f"User Prediction: {int(self.data_analytics.last_prediction)} KWh"
                    )
                    plt.legend()
                    plt.title("Total Energy Distribution (Prediction)")
                    plt.xlabel("Total Energy (KWh)")
                    plt.ylabel("Frequency")
                    
                    # اضافه کردن نمودار بهینه‌سازی
                    if hasattr(self, 'optimized_result') and self.optimized_result is not None:
                        best, variables = self.optimized_result
                        plt.subplot(2, 1, 2)
                        plt.hist(self.data_analytics.Tot_e, bins=30, edgecolor='black')
                        plt.axvline(
                            self.data_analytics.last_prediction,
                            color='red', linestyle='--',
                            label=f"User Prediction: {int(self.data_analytics.last_prediction)} KWh"
                        )
                        plt.axvline(best, color='green', linestyle='-.', 
                                  label=f"Optimized: {int(best)} KWh")
                        
                        # اضافه کردن مقادیر بهینه‌سازی به نمودار
                        opt_text = "Optimized Values:\n\n"
                        for feat_key, val in zip(self.data_analytics.model.feature_names_in_, variables):
                            label = self.data_analytics.feature_map.get(feat_key)
                            if self.static_checkboxes[label].isChecked():
                                val = float(self.inputs[label].text())
                            elif label == "HEEL NO":
                                val = round(val)
                            opt_text += f"{label}: {val:.2f}\n"
                        
                        plt.text(0.1, 0.95, opt_text,
                                transform=plt.gca().transAxes,
                                verticalalignment='top',
                                fontsize=10,
                                color='black')
                        
                        plt.legend()
                        plt.title("Total Energy Distribution (Optimization)")
                        plt.xlabel("Total Energy (KWh)")
                        plt.ylabel("Frequency")
                    
                    plt.tight_layout()
                    pdf.savefig(fig)
                    plt.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save PDF: {str(e)}")
    def download_png_opt(self):
        try:
            filename, _ = QFileDialog.getSaveFileName(self, "Save PNG", "", "PNG Files (*.png)")
            if filename:
                # ذخیره نمودار بهینه‌سازی به صورت PNG
                self.figure1.savefig(filename, format="png")
        except:
            pass

    def toggle_static_mode(self):
        is_checked = self.static_checkbox.isChecked()
        
        # Show/hide individual static checkboxes
        for label, checkbox in self.static_checkboxes.items():
            checkbox.setVisible(is_checked)
        
        # Show/hide Select All and Deselect All Static buttons
        self.select_all_static_btn.setVisible(is_checked)
        self.deselect_all_static_btn.setVisible(is_checked)
        
        # If static mode is being disabled, uncheck all static checkboxes first
        if not is_checked:
            for label, checkbox in self.static_checkboxes.items():
                checkbox.setChecked(False)
        
        # Update all labels to ensure they always show original ranges
        for label, checkbox in self.static_checkboxes.items():
            if label in self.inputs:
                # همیشه بازه اصلی را نمایش بده
                min_val, max_val = self.data_analytics.input_ranges[label]
                styled_label_text = self.style_units(label)
                item_at_position = self.pre_grid.itemAtPosition(self.input_rows[label], 0)
                if item_at_position is not None:
                    lbl = item_at_position.widget()
                    if lbl is not None:
                        range_str = self.format_range_text(label, min_val, max_val)
                        lbl.setText(f"{styled_label_text} <span style='color: grey; '>{range_str}</span>")
                
                # به‌روزرسانی ستون سوم بر اساس وضعیت
                item_at_position = self.pre_grid.itemAtPosition(self.input_rows[label], 3)
                if item_at_position is not None:
                    opt_label = item_at_position.widget()
                    if opt_label is not None:
                        if is_checked and checkbox.isChecked():
                            # نمایش مقدار استاتیک
                            current_value = self.inputs[label].text()
                            opt_label.setText(f"Static: {current_value}")
                        else:
                            # اگر مقدار بهینه‌سازی وجود دارد، آن را نمایش بده
                            if hasattr(self, 'optimized_result') and self.optimized_result is not None:
                                try:
                                    _, variables = self.optimized_result
                                    if variables:  # بررسی وجود متغیرها
                                        for feat_key, val in zip(self.data_analytics.model.feature_names_in_, variables):
                                            if self.data_analytics.feature_map.get(feat_key) == label:
                                                if label == "HEEL NO":
                                                    val = round(val)
                                                opt_label.setText(f"OPT.: {val:.2f}")
                                                break
                                except:
                                    pass  # اگر مشکلی در دسترسی به مقادیر بهینه‌سازی وجود داشت، نادیده بگیر

    def select_all_static(self):
        """Select all static checkboxes"""
        for label, checkbox in self.static_checkboxes.items():
            if checkbox.isVisible():  # Only check visible checkboxes
                checkbox.setChecked(True)

    def deselect_all_static(self):
        """Deselect all static checkboxes"""
        for label, checkbox in self.static_checkboxes.items():
            if checkbox.isVisible():  # Only uncheck visible checkboxes
                checkbox.setChecked(False)

    def on_optimization_done(self, best):
        self.progress.close()

        try:
            best, variables = best
        except:
            best, variables = best, []
        try:
            best = best.iloc[0, 0]
        except:
            pass
        self.optimized_result = (float(best), variables)
        self.opt_result_label.setText(f"Optimized Energy: {float(best):.2f} KWh")
        self.clear_optimization_labels()
        
        # افزودن Opt در کنار ورودی‌ها
        for feat_key, val in zip(self.data_analytics.model.feature_names_in_, variables):
            label = self.data_analytics.feature_map.get(feat_key)
            if label in self.inputs:
                txt = "OPT. "
                # بررسی وضعیت چک‌باکس برای مقدار ورودی دستی
                if self.static_checkboxes[label].isChecked():
                    txt = "Static"
                    val = float(self.inputs[label].text())  # مقدار ورودی دستی
                elif label == "HEEL NO":
                    val = round(val)  # گرد کردن به 0 یا 1

                row = self.input_rows[label]
                opt_label = QLabel(f"{txt}: {val:.2f}")
                opt_label.setStyleSheet(glass_input_style)
                self.pre_grid.addWidget(opt_label, row, 3)

        # تعیین مقدار خط قرمز: اگر پیش‌بینی قبلاً انجام نشده/ورودی خالی است، میانگین کل ذوب‌ها
        any_filled = any(le.text().strip() != "" for le in self.inputs.values())
        if any_filled:
            red_value = self.data_analytics.predict(self.inputs, use_constraints=False)
            red_label = f"User Prediction: {int(red_value)} KWh"
        else:
            try:
                red_value = float(np.mean(self.data_analytics.Tot_e))
            except Exception:
                red_value = 0.0
            red_label = f"Average: {int(red_value)} KWh"

        self.ax1.clear()
        self.ax1.hist(self.data_analytics.Tot_e, bins=30, edgecolor='black')
        self.ax1.axvline(
            red_value,
            color='red',
            linestyle='--',
            label=red_label
        )
        
        self.ax1.axvline(best, color='green', linestyle='-.', label=f"Opt: {int(best)} KWh")

        # نمایش درصد بهبود نسبت به خط قرمز (پیش‌بینی کاربر یا میانگین)
        try:
            baseline = float(red_value)
            optimized = float(best)
            if baseline > 0:
                percent_change = (baseline - optimized) / baseline * 100.0
                # رنگ‌بندی: سبز برای بهبود، قرمز برای بدتر شدن، خاکستری برای تغییر کم
                if percent_change > 0.5:
                    pct_color = 'green'
                elif percent_change < -0.5:
                    pct_color = 'red'
                else:
                    pct_color = 'orange'

                pct_text = f"Δ vs Baseline: {percent_change:+.1f}%"
                # متن زیبا در داخل نمودار گوشه بالا-راست
                self.ax1.text(
                    0.98, 0.95, pct_text,
                    transform=self.ax1.transAxes,
                    ha='right', va='top',
                    fontsize=13, color=pct_color,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.85, edgecolor=pct_color),
                    zorder=10
                )

                # فلش بین baseline و optimized برای زیبایی
                y_top = self.ax1.get_ylim()[1] * 0.85
                self.ax1.annotate(
                    '',
                    xy=(optimized, y_top), xytext=(baseline, y_top),
                    arrowprops=dict(arrowstyle='<->', color=pct_color, lw=2),
                    zorder=9
                )
            else:
                pass
        except Exception:
            pass
        self.ax1.set_xlabel("Total Energy (KWh)")
        self.ax1.set_ylabel("Frequency")
        # Dynamic legend placement to avoid overlap with green arrow and percent box
        try:
            x_min, x_max = self.ax1.get_xlim()
            x_mid = (baseline + optimized) / 2.0
            x_mid_norm = (x_mid - x_min) / (x_max - x_min + 1e-9)
            legend_loc = 'lower right' if x_mid_norm < 0.5 else 'lower left'
        except Exception:
            legend_loc = 'lower right'
        self.ax1.legend(loc=legend_loc, framealpha=0.9, facecolor='white')
        self.figure1.tight_layout()
        semi_green = (0.2, 0.7, 0.0, 0)
        semi_orange = (1, 1, 1, 0.3)
        self.figure1.patch.set_facecolor(semi_green)
        self.ax1.patch.set_facecolor(semi_orange)
        self.canvas1.setStyleSheet("background:transparent; border-radius: 25px;")
        self.canvas1.setAttribute(Qt.WA_TranslucentBackground)
        self.canvas1.draw()

    def show_total_energy_chart(self):
        self.ax2.clear()
        self.ax2.hist(self.data_analytics.Tot_e, bins=30, edgecolor='black')
        self.ax2.axvline(
            self.data_analytics.last_prediction,
            color='red', linestyle='--',
            label=f"User Prediction: {int(self.data_analytics.last_prediction)} KWh"
        )
        self.ax2.legend()
        self.ax2.set_title("Total Energy Distribution")
        self.ax2.set_xlabel("Total Energy (KWh)")
        self.ax2.set_ylabel("Frequency")
        self.figure2.tight_layout(pad=2.0)
        semi_green = (0.2, 0.7, 0.0, 0)
        semi_orange = (1, 1, 1, 0.3)

        self.figure2.patch.set_facecolor(semi_green)
        self.ax2.patch.set_facecolor(semi_orange)
        self.canvas2.setStyleSheet("background:transparent; border-radius: 25px;")
        self.canvas2.setAttribute(Qt.WA_TranslucentBackground)
        self.canvas2.draw()

    def export_optimized_data(self):
        if not hasattr(self, "optimized_result"):
            QMessageBox.warning(self, "No Data", "No optimized data available to export.")
            return

        best, variables = self.optimized_result

        # ساخت دیکشنری از داده‌های بهینه‌شده
        optimized_data = {}
        for feat_key, val in zip(self.data_analytics.model.feature_names_in_, variables):
            label = self.data_analytics.feature_map.get(feat_key, feat_key)
            # اگر فیلد استاتیک است، از مقدار ورودی استفاده کن
            if self.static_checkboxes[label].isChecked():
                val = float(self.inputs[label].text())
            # اگر HEEL NO است، گرد کن
            elif label == "HEEL NO":
                val = round(val)
            optimized_data[label] = val
        optimized_data["Optimized Energy"] = f"{best:.2f} KWh"

        import pandas as pd
        df = pd.DataFrame([optimized_data])

        # نمایش QFileDialog جهت ذخیره‌سازی فایل اکسل
        filename, _ = QFileDialog.getSaveFileName(self, "Save Optimized Data", "", "Excel Files (*.xlsx)")
        if filename:
            try:
                df.to_excel(filename, index=False)
                QMessageBox.information(self, "Export Successful", f"Optimized data exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Failed", f"Failed to export data:\n{str(e)}")
    
    def export_row100_compare(self):
        try:
            pred, actual, row = self.data_analytics.predict_row_from_dataset(99)
            out = row.to_frame().T
            out['Predicted_Energy'] = pred
            if actual is not None:
                out['Actual_Energy'] = actual
            filename, _ = QFileDialog.getSaveFileName(self, "Save Row100 Compare", "row100_prediction_compare.xlsx", "Excel Files (*.xlsx)")
            if filename:
                out.to_excel(filename, index=False)
                QMessageBox.information(self, "Export Successful", f"Saved to {filename}")
        except Exception as e:
            QMessageBox.critical(self, "Export Failed", f"Failed to export row 100 compare:\n{str(e)}")
    # --------------------------
    def load_input_file(self):
        progress = QProgressDialog("Loading file...", None, 0, 0, self)
        progress.setWindowTitle("Please wait")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()
        QApplication.processEvents()

        path, _ = QFileDialog.getOpenFileName(
            self, "Select Excel or CSV File", '',
            "Excel Files (*.xlsx);;CSV Files (*.csv)"
        )
        progress.close()
        if not path:
            return

        try:
            df = (pd.read_excel(path, sheet_name=0)
                  if path.endswith('.xlsx') else pd.read_csv(path))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file: {e}")
            return
        if 'ENERGY_TOT_EAF' in df.columns:
            df = df.dropna(subset=['ENERGY_TOT_EAF'])

        valid_keys = set(df.columns) & set(self.data_analytics.feature_map.keys())
        if len(valid_keys) < 8:
            QMessageBox.warning(
                self, "Insufficient Data",
                f"File must contain at least 8 features from model map. Found {len(valid_keys)}."
            )
            return

        # انتخاب ردیف در صورت چند ردیف بودن
        if len(df) > 1:
            dlg = QInputDialog(self)
            dlg.setStyleSheet("background-color: rgba(15, 23, 42,  0.6)")
            dlg.setWindowTitle("Select Row")
            dlg.setLabelText(f"Enter row number (1 to {len(df)}):")
            dlg.setOption(QInputDialog.UsePlainTextEditForTextInput, False)
            dlg.setIntRange(1, len(df))
            dlg.setIntValue(1)
            dlg.setFixedSize(400, 200)
            ok = dlg.exec_()
            if not ok:
                return
            rownum = dlg.intValue() - 1
        else:
            rownum = 0

        self.file_status_label.setText(
            f"Loaded: ({len(valid_keys)} valid cols)"
        )

        row = df.iloc[rownum]
        for key in valid_keys:
            label = self.data_analytics.feature_map[key]
            if label in self.inputs:
                value = row[key]
                # Automatically convert HEEL NO from float to int
                if label == "HEEL NO":
                    try:
                        value = int(round(float(value)))
                    except (ValueError, TypeError):
                        value = 0
                self.inputs[label].setText(str(value))

    # --------------------------
    def run_prediction(self):
        # Check if user has entered any values
        filled_inputs = 0
        for label, le in self.inputs.items():
            if le.text().strip() != "":
                filled_inputs += 1
                
        if filled_inputs == 0:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("No Input Values")
            msg.setText("Please enter values for the input parameters before running prediction.")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d2d;
                }
                QLabel {
                    color: white;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #555555;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
            """)
            msg.exec_()
            return
            
        # Check for invalid input values
        for label, le in self.inputs.items():
            if le.text().strip() != "" and not le.hasAcceptableInput():
                # نمایش پیام خطا برای ورودی نامعتبر
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                if label == "HEEL NO":
                    msg.setWindowTitle("Incorrect Value")
                    msg.setText(f"The input for {label} is not within the allowed range and must be an Integer (not Float).")
                else:
                    msg.setWindowTitle("Incorrect Value")
                    msg.setText(f"The input for {label} is not within the allowed range.")
                msg.setStandardButtons(QMessageBox.Ok)
                # استایل دلخواه: تغییر رنگ پس‌زمینه، رنگ متن و استایل کلیدها
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #2d2d2d;
                    }
                    QLabel {
                        color: white;
                        font-size: 16px;
                    }
                    QPushButton {
                        background-color: #555555;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 5px 15px;
                    }
                    QPushButton:hover {
                        background-color: #777777;
                    }
                """)
                msg.exec_()
                return
        # manual mode
        pred = self.data_analytics.predict(self.inputs, use_constraints=False)

        self.show_total_energy_chart()
        self.result_label.setText(f"Predicted: {pred:.2f} KWh")

    # --------------------------
    def run_optimization(self):
        # For optimization, we can proceed even with empty fields (they'll be set to 0)
        # Only check for invalid input values in filled fields
        for label, le in self.inputs.items():
            if le.text().strip() != "" and not le.hasAcceptableInput():
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Incorrect Value")
                msg.setText(f"The input for {label} is not within the allowed range.")
                msg.setStandardButtons(QMessageBox.Ok)
                # استایل دلخواه: تغییر رنگ پس‌زمینه، رنگ متن و استایل کلیدها
                msg.setStyleSheet("""
                    QMessageBox {
                        background-color: #2d2d2d;
                    }
                    QLabel {
                        color: white;
                        font-size: 16px;
                    }
                    QPushButton {
                        background-color: #555555;
                        color: white;
                        border: none;
                        border-radius: 5px;
                        padding: 5px 15px;
                    }
                    QPushButton:hover {
                        background-color: #777777;
                    }
                """)
                msg.exec_()
                return 
        try:
            if self.ga_iterations_input.hasAcceptableInput():
                max_iter = int(self.ga_iterations_input.text())
            else:
                raise ValueError
        except ValueError:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("Incorrect Value")
            msg.setText(f"Please enter a valid integer for max iterations. (GA AI NUM.)")
            msg.setStandardButtons(QMessageBox.Ok)
            # استایل دلخواه: تغییر رنگ پس‌زمینه، رنگ متن و استایل کلیدها
            msg.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d2d;
                }
                QLabel {
                    color: white;
                    font-size: 16px;
                }
                QPushButton {
                    background-color: #555555;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 5px 15px;
                }
                QPushButton:hover {
                    background-color: #777777;
                }
            """)
            msg.exec_()
            return 

        # بروزرسانی ga_params؛ فرض کنید ga_params در بالای فایل به این صورت تعریف شده:
        # ga_params = { 'max_num_iteration': 100, ... }
        self.data_analytics.ga_params['max_num_iteration'] = max_iter

        # Capture UI static fixed values mapped to model features
        # Reset ui_fixed completely each time to ensure disabled checkboxes don't persist
        try:
            ui_fixed = {}  # Start fresh each time
            for feat_key in self.data_analytics.expected_features:
                label = self.data_analytics.feature_map.get(feat_key)
                if label and label in self.inputs and label in self.static_checkboxes:
                    # Only add to ui_fixed if checkbox is currently checked
                    if self.static_checkboxes[label].isChecked():
                        try:
                            val = float(self.inputs[label].text())
                            if label == "HEEL NO":
                                val = round(val)
                            ui_fixed[feat_key] = val
                        except Exception:
                            pass
                    # If checkbox is not checked, explicitly do NOT add to ui_fixed
            # Always set ui_fixed (even if empty) to clear previous values
            self.data_analytics.ui_fixed = ui_fixed
        except Exception:
            # In case of error, ensure ui_fixed is cleared
            self.data_analytics.ui_fixed = {}

        self.progress = QProgressDialog(
            "Optimization in progress...", None, 0, 0, self
        )
        self.progress.setStyleSheet("background-color: rgba(15, 23, 42,  0.6)")
        self.progress.resize(600, 300)
        self.progress.setWindowTitle("Please wait ... (1min)")
        self.progress.setWindowModality(Qt.WindowModal)
        self.progress.setCancelButton(None)
        self.progress.show()

        self.thread = QThread()
        self.worker = OptimizeWorker(self.data_analytics)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.on_optimization_done)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def clear_optimization_labels(self):
        # از انتها به ابتدا پیمایش می‌کنیم تا در حین حذف مشکل ایندکس زدن رخ ندهد.
        for i in reversed(range(self.pre_grid.count())):
            item = self.pre_grid.itemAt(i)
            if item:
                row, col, rowSpan, colSpan = self.pre_grid.getItemPosition(i)
                if col == 3:  # اگر آیتم داخل ستون دوم باشد
                    widget = item.widget()
                    if widget is not None:
                        self.pre_grid.removeWidget(widget)
                        widget.deleteLater()
    # --------------------------

    def open_fixed_excel(self):
        try:
            # مسیر فایل اصلی
            original_file = resource_path('Help.xlsx')
            if not os.path.exists(original_file):
                original_file = 'Help.xlsx'
            
            # ایجاد نام برای فایل کپی با استفاده از تاریخ و زمان فعلی
            now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_dir = os.path.join(os.environ.get('TEMP', os.getcwd()), 'EAF_App_Temp')
            
            # ایجاد پوشه موقت اگر وجود ندارد
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir)
                
            # مسیر فایل کپی 
            copied_file = os.path.join(temp_dir, f'Help_Copy_{now}.xlsx')
            
            # کپی فایل
            if os.path.exists(original_file):
                shutil.copy2(original_file, copied_file)
                
                # باز کردن فایل کپی شده
                QDesktopServices.openUrl(QUrl.fromLocalFile(copied_file))
            else:
                QMessageBox.warning(self, "فایل یافت نشد", "فایل راهنما یافت نشد!")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن فایل: {str(e)}")

    def open_program_help(self):
        self.pdf_window = PDFViewerWindow(self)
        self.pdf_window.show()

    def update_static_label(self, label, state):
        if label in self.inputs:
            # همیشه بازه اصلی را نمایش بده، بدون توجه به وضعیت چک‌باکس
            min_val, max_val = self.data_analytics.input_ranges[label]
            styled_label_text = self.style_units(label)
            item_at_position = self.pre_grid.itemAtPosition(self.input_rows[label], 0)
            if item_at_position is not None:
                lbl = item_at_position.widget()
                if lbl is not None:
                    range_str = self.format_range_text(label, min_val, max_val)
                    lbl.setText(f"{styled_label_text} <span style='color: grey; '>{range_str}</span>")
            
            # به‌روزرسانی مقدار در ستون سوم بر اساس وضعیت چک‌باکس
            item_at_position = self.pre_grid.itemAtPosition(self.input_rows[label], 3)
            if item_at_position is not None:
                opt_label = item_at_position.widget()
                if opt_label is not None:
                    if state == Qt.Checked:
                        # نمایش مقدار استاتیک
                        current_value = self.inputs[label].text()
                        opt_label.setText(f"Static: {current_value}")
                    else:
                        # اگر مقدار بهینه‌سازی وجود دارد، آن را نمایش بده
                        if hasattr(self, 'optimized_result') and self.optimized_result is not None:
                            try:
                                _, variables = self.optimized_result
                                if variables:  # بررسی وجود متغیرها
                                    for feat_key, val in zip(self.data_analytics.model.feature_names_in_, variables):
                                        if self.data_analytics.feature_map.get(feat_key) == label:
                                            if label == "HEEL NO":
                                                val = round(val)
                                            opt_label.setText(f"OPT.: {val:.2f}")
                                            break
                            except:
                                pass  # اگر مشکلی در دسترسی به مقادیر بهینه‌سازی وجود داشت، نادیده بگیر

    def on_heel_no_changed(self, label, text):
        """Special handler for HEEL NO field to auto-convert float to int"""
        if text.strip():
            try:
                # Try to convert the input to float first, then round to int
                float_val = float(text)
                int_val = int(round(float_val))
                
                # Only update if the conversion actually changed the value
                if str(int_val) != text:
                    # Temporarily disconnect to avoid infinite loop
                    self.inputs[label].textChanged.disconnect()
                    self.inputs[label].setText(str(int_val))
                    # Reconnect the signal
                    self.inputs[label].textChanged.connect(lambda txt, l=label: self.on_heel_no_changed(l, txt))
                    
                # Update static label if needed
                self.on_input_changed(label, str(int_val))
            except (ValueError, TypeError):
                # If conversion fails, use the regular input change handler
                self.on_input_changed(label, text)
        else:
            # Empty text, use regular handler
            self.on_input_changed(label, text)

    def on_input_changed(self, label, text):
        # فقط اگر Static Mode فعال باشد و چک‌باکس استاتیک این پارامتر تیک خورده باشد، ستون سوم را به‌روز کن
        # بازه اصلی هرگز تغییر نمی‌کند
        if (self.static_checkbox.isChecked() and 
            label in self.static_checkboxes and 
            self.static_checkboxes[label].isChecked()):
            
            # به‌روزرسانی فقط ستون سوم (مقدار استاتیک)
            item_at_position = self.pre_grid.itemAtPosition(self.input_rows[label], 3)
            if item_at_position is not None:
                opt_label = item_at_position.widget()
                if opt_label is not None:
                    opt_label.setText(f"Static: {text}")

# ======================
# Splash انیمیشنی
# ======================
class AnimatedSplash(QWidget):
    def __init__(self, text="Energy Optimization", duration=4000, parent=None):
        super().__init__(parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        # ۱) پنجره رو شفاف کن
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.duration = duration
        self.elapsed = 0
        width, height = 900, 600
        self.resize(width, height)

        # ۲) پردازش تصویر با blur و rounded
        pixmap = QPixmap(resource_path("core.png")).scaled(width, height,
                                            Qt.KeepAspectRatioByExpanding,
                                            Qt.SmoothTransformation)
        scene = QGraphicsScene()
        item = QGraphicsPixmapItem(pixmap)
        blur = QGraphicsBlurEffect()
        blur.setBlurRadius(1)
        item.setGraphicsEffect(blur)
        scene.addItem(item)

        blurred = QPixmap(width, height)
        blurred.fill(Qt.transparent)
        p = QPainter(blurred)
        scene.render(p)
        p.end()

        rounded = QPixmap(width, height)
        rounded.fill(Qt.transparent)
        p = QPainter(rounded)
        p.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, width, height), 40, 40)
        p.setClipPath(path)
        p.drawPixmap(0, 0, blurred)
        p.end()

        # ۳) ماسک پنجره رو براساس rounded اعمال کن
        self.setMask(rounded.mask())
        self.pixmap_rounded = rounded

        # لیبل متن
    
        self.ai = QLabel("SmartArc", self)
        self.ai.setAlignment(Qt.AlignCenter)
        self.ai.setStyleSheet("color: white; ")
        
        font = QFont("Montserrat", 45, QFont.Bold)
        self.ai.setFont(font)
        size = QSize(900, 420)
        self.ai.resize(size)

        # افکت شفافیت
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        # تایمر افزایش فونت هر ثانیه
        self.font_timer = QTimer(self)
        self.font_timer.setInterval(40)
        self.font_timer.timeout.connect(self.increase_font)
        # انیمیشن fade-in
        self.anim_in = QPropertyAnimation(self.opacity, b"opacity")
        self.anim_in.setDuration(800)
        self.anim_in.setStartValue(0.0)
        self.anim_in.setEndValue(1.0)
        self.anim_in.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim_in.finished.connect(self.start_font_timer)

        # انیمیشن fade-out
        self.anim_out = QPropertyAnimation(self.opacity, b"opacity")
        self.anim_out.setDuration(800)
        self.anim_out.setStartValue(1.0)
        self.anim_out.setEndValue(0.0)
        self.anim_out.setEasingCurve(QEasingCurve.InOutQuad)
        self.anim_out.finished.connect(self.close)



        # زمان‌بندی fade-out بعد از کل مدت منهای fade-out
        QTimer.singleShot(self.duration - 800, self.anim_out.start)

    def paintEvent(self, event):
        # فقط rounded pixmap رو رسم کن
        p = QPainter(self)
        p.drawPixmap(0, 0, self.pixmap_rounded)
        p.end()

    def show(self):
        super().show()
        self.anim_in.start()

    def start_font_timer(self):
        self.font_timer.start()

    def increase_font(self):
        f = self.ai.font()
        self.ai.setStyleSheet(
            "color: {} ; opacity: {} ;".format(
                random.choice(["white", "black", "orange", "darkred", "white"]),
                random.choice([0.9, 1, 0.4, 0.1])
            )
        )
        f.setPointSize(f.pointSize() + random.choice([+1, +2, -1]))
        self.ai.setFont(f)
        self.elapsed += 40
        if self.elapsed + 1000 >= self.duration:
            self.font_timer.stop()


# ======================
# Main
# ======================
def start_main_app():
    global energy_win  # اطمینان از نگهداری مرجع شیء اصلی
    energy_app = EnergyApp()
    scroll_area = QScrollArea()
    scroll_area.setWidgetResizable(True)  # محتوا نسبت به اندازه پنجره تطبیق یابد
    scroll_area.setWidget(energy_app)
    scroll_area.resize(1500, 1900)
    energy_win = scroll_area  # نگهداری مرجع در متغیر جهانی
    scroll_area.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    splash = AnimatedSplash(duration=3000)
    splash.show()
    splash.anim_out.finished.connect(start_main_app)

    sys.exit(app.exec_())
