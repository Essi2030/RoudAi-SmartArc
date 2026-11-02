import random
import sys
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtGui import QBrush, QPalette, QPixmap, QPainter, QPainterPath, QFont, QColor
from PyQt5.QtWidgets import (QFrame, QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
                             QHBoxLayout, QGridLayout, QGroupBox, QCheckBox, QProgressDialog, QFileDialog,
                             QMessageBox, QInputDialog, QGraphicsBlurEffect, QGraphicsPixmapItem,
                             QGraphicsScene, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPropertyAnimation, QEasingCurve, QSize, QObject, QThread, pyqtSignal

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from geneticalgorithm2 import geneticalgorithm2 as ga

# --------------------------
# سبک‌ها
# --------------------------
main_style = """
    color: white;
    font-family: Montserrat; 
    font-size: 18px;
    border-radius: 26px;
"""
glass_button_style = """
QPushButton, QCheckBox {
    background-color: rgba(15, 23, 42, 0.6);
    color: white;
    border: 2px solid rgba(255,255,255,0.8);
    border-radius: 16px;
    padding: 8px; margin: 5px;
    font-size: 16px;
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
    border: 3px solid rgba(255,255,255,0.5);
    border-radius: 30px;
    padding: 15px;
    margin-top: 20px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    color: white;
    font-size: 45px;
    padding: 5px 20px;
}
"""
glass_input_style = """
QLineEdit {
    background-color: rgba(15, 23, 42, 0.6);
    color: white;
    margin-right: 20px;
    margin-left: 20px;
    border: 1px solid rgba(255,255,255,0.6);
    padding: 6px;
    border-radius: 16px;
}
"""

# --------------------------
# پارامترهای GA
# --------------------------
ga_params = {
    'max_num_iteration': 100,
    'population_size': 100,
    'mutation_probability': 0.2,
    'elit_ratio': 0.01,
    'crossover_type': 'uniform',
    'parents_portion': 0.3,
    'max_iteration_without_improv': None
}

# ======================
# کلاس DataAnalytics
# ======================
class DataAnalytics:
    def __init__(self,
                 model_path='random_forest_model_final.pkl',
                 data_path='Merged_excells_Engy_Ct_K2_Sf_Nf_Tf.xlsx'):
        with open(model_path, 'rb') as f:
            self.model = pickle.load(f)

        # نگاشت نام فیچر به لیبل
        self.feature_map = {
            'ARIV_O2_PPM': 'O2 (ppm) ',
            'GRAPHIT_LANCE_EAF': 'Lance EAF ',
            'C_CLOX_EAF': 'CLOX ',
            'ANTHRACITE_EAF': 'ANTHRACITE EAF',
            'TAP_TO_TAP_SS': 'Tap to Start',
            'TAP_WEI_TON': 'TAP WEI',
            'SCRAP_WEI_EAF': 'SCRAPE EAF',
            'DRI_EAF': 'DRI EAF',
            'PDWR_LIME': 'LIME POWDER',
            'DOLOMIT_LIME_EAF': 'LIME DOLOMIT',
            'LIME_EAF': 'LIME EAF',
            'CARBON_EAF': 'CARBON EAF',
            'GRAPHIT_EAF': 'GRAPHIT EAF',
            'COKE_EAF': 'COKE EAF (0-9999)',
            'POWER_OFF_TAP': 'POWER OFF TAP',
            'POWER_ON_TAP': 'POWER ON TAP',
            'OXCYGEN_EAF': 'OXCYGEN_EAF',
        }
        self.expected_features = list(self.model.feature_names_in_)
        self.feature_importances_ = pd.Series(
            self.model.feature_importances_,
            index=self.expected_features
        ).sort_values()

        df = pd.read_excel(data_path)
        self.df_vars = df.drop(columns=['HEAT', 'DAT_EN', 'ENERGY_TOT_EAF'])
        self.Tot_e = df['ENERGY_TOT_EAF'].values
        _, _, _, y_test = train_test_split(
            self.df_vars, df['ENERGY_TOT_EAF'],
            test_size=0.2, random_state=40
        )
        self.y_test = y_test

    def predict(self, inputs):
        vals, self.last_input_values = [], {}
        for feat in self.expected_features:
            label = self.feature_map.get(feat)
            v = 0.0
            if label in inputs and inputs[label] is not None:
                try:
                    v = float(inputs[label].text())
                except:
                    v = 0.0
            vals.append(v)
            self.last_input_values[feat] = v

        df_pred = pd.DataFrame([vals], columns=self.expected_features)
        self.last_prediction = self.model.predict(df_pred)[0]
        return self.last_prediction

    def optimize_energy(self):
        manual_fixed = {}
        for feat, label in self.feature_map.items():
            if hasattr(self, 'inputs') and label in self.inputs:
                widget = self.inputs[label]
                if not widget.isEnabled():  # یعنی از فایل آمده
                    try:
                        manual_fixed[feat] = float(widget.text())
                    except:
                        continue

        varbound = np.array([
            [self.df_vars[c].min(), self.df_vars[c].max()]
            for c in self.df_vars.columns
        ])

        for var in manual_fixed:
            if var in self.df_vars.columns:
                idx = self.df_vars.columns.get_loc(var)
                val = manual_fixed[var]
                varbound[idx] = [val, val]  # قفل می‌شود

        def objective(x):
            ind = pd.DataFrame([x], columns=self.df_vars.columns)
            for var in manual_fixed:
                if var in ind.columns:
                    ind[var] = manual_fixed[var]
            return self.model.predict(ind)[0]

        # اجرای GA
        model = ga(
            function=objective,
            dimension=len(self.df_vars.columns),
            variable_type='real',
            variable_boundaries=varbound,
            algorithm_parameters=ga_params
        )
        model.run(no_plot=True, progress_bar_stream=None)

        return float(model.result['score']), list(model.result['variable'])


# ======================
# Worker برای بهینه‌سازی GA
# ======================
class OptimizeWorker(QObject):
    finished = pyqtSignal(object)
    def __init__(self, analytics):
        super().__init__()
        self.analytics = analytics

    def run(self):
        result = self.analytics.optimize_energy()
        self.finished.emit(result)  # ارسال نتیجه (tuple: امتیاز و متغیرها)


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
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Energy Prediction & Optimization')
        self.setStyleSheet(main_style)
        pixmap = QPixmap("core.png")   # مسیر تصویر
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(pixmap))
        self.setPalette(palette)
        self.setAutoFillBackground(True)
        main_layout = QHBoxLayout()

        # ---- Prediction Box ----
        self.pred_box = QGroupBox("Energy Prediction")
        self.pred_box.setStyleSheet(glass_groupbox_style)
        self.pred_box.setFixedSize(720, 1280)
        p_layout = QVBoxLayout()
        self.pre_grid = QGridLayout()
        self.inputs = {}
        self.input_rows = {}

        for i, label in enumerate(self.data_analytics.feature_map.values()):
            lbl = QLabel(label)
            lbl.setStyleSheet("""
                background-color: rgba(15, 23, 42, 0.3);
                color: white;
                margin-right: 20px;
                margin-left: 20px;
                border: 3px solid rgba(255,255,255,0.5);
                padding: 6px; 
                border-radius:15px;
            """)
            lbl.setAlignment(Qt.AlignCenter)
            le = QLineEdit()
            le.setText("0")
            le.setStyleSheet(glass_input_style)
            self.pre_grid.addWidget(lbl, i, 0)
            self.pre_grid.addWidget(le, i, 1)
            self.inputs[label] = le
            self.input_rows[label] = i

        cb_layout = QHBoxLayout()        
        self.imp_cb = QCheckBox('Feature Importances')
        self.te_cb  = QCheckBox('Estimated Total Energy')
        self.tr_cb  = QCheckBox('True Total Energy')
        for cb in (self.imp_cb, self.te_cb, self.tr_cb):
            cb.setStyleSheet("""
                QPushButton, QCheckBox {
                    background-color: rgba(15, 23, 42, 0.6);
                    color: white;
                    border:2px solid rgba(255,255,255,0.8);
                    border-radius:14px;
                    padding:5px; margin:2px;
                    font-size:14px;
                }
                QPushButton:hover, QCheckBox:hover {
                    background-color: rgba(255,255,255,0.2);
                }
            """)
            cb_layout.addWidget(cb)

        btn_pred = QPushButton("Run Prediction")
        btn_pred.setStyleSheet(glass_button_style)
        btn_pred.clicked.connect(self.run_prediction)

        self.result_label = QLabel("Predicted:")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setStyleSheet(
            'margin:10px; font-size:21px; background-color: rgba(15, 23, 42, 0.4); border-radius: 15px; padding:10px;'
        )

        p_layout.addLayout(self.pre_grid)
        p_layout.addLayout(cb_layout)
        p_layout.addWidget(btn_pred, alignment=Qt.AlignCenter)
        p_layout.addWidget(self.result_label)
        self.pred_box.setLayout(p_layout)

        # ---- Optimization Box ----
        opt_box = QGroupBox("Energy Optimization")
        opt_box.setStyleSheet(glass_groupbox_style)
        o_layout = QVBoxLayout()

        # Past Data Checker
        self.file_box = QGroupBox("Past Data Checker")
        self.file_box.setStyleSheet(glass_groupbox_style)
        self.file_box.setFixedSize(700, 200)
        f_layout = QVBoxLayout()
        self.file_status_label = QLabel("No past file loaded.")
        self.file_status_label.setAlignment(Qt.AlignCenter)
        self.file_status_label.setStyleSheet(
            'margin:10px 0; font-size:22px; background-color: rgba(15, 23, 42, 0.4); border-radius: 10px; padding:8px;'
        )
        btn_load = QPushButton("Load Excel/CSV Data")
        btn_load.setStyleSheet(glass_button_style)
        btn_load.clicked.connect(self.load_input_file)
        f_layout.addWidget(btn_load, alignment=Qt.AlignCenter)
        f_layout.addWidget(self.file_status_label, alignment=Qt.AlignCenter)
        self.file_box.setLayout(f_layout)

        # Canvas برای نمایش هیستوگرام GA
        self.figure1, self.ax1 = plt.subplots(figsize=(8,8), dpi=100)
        self.canvas1 = FigureCanvas(self.figure1)
        semi_green = (0.2, 0.7, 0.0, 0)
        semi_orange = (1, 1, 1, 0.3)
        self.figure1.patch.set_facecolor(semi_green)
        self.ax1.patch.set_facecolor(semi_orange)
        self.canvas1.setStyleSheet("background:transparent; border-radius: 25px;")
        self.canvas1.setAttribute(Qt.WA_TranslucentBackground)
        btn_opt = QPushButton("Run Optimization")
        btn_opt.setStyleSheet(glass_button_style)
        btn_opt.clicked.connect(self.run_optimization)

        self.opt_result_label = QLabel("Optimized Energy: Not Calculated Yet!")
        self.opt_result_label.setAlignment(Qt.AlignCenter)
        self.opt_result_label.setStyleSheet(
            'background-color: rgba(15, 23, 42, 0.5); margin:5px; font-size:21px; border-radius: 15px; padding:2px;'
        )
        self.help = QLabel("""
Program Help:

>> Real-Time Section <<
--------------------------------
In this section, the user can manually input values 
and instantly receive results or analysis.  
It is useful for quick and on-the-spot evaluations.

>> Past-Time Section <<
--------------------------------
This section allows the user to upload an output file 
(e.g., a data log). The program processes the file 
and provides results based on historical data.
""")
        self.help.setAlignment(Qt.AlignLeft)
        self.help.setStyleSheet(
            'background-color: rgba(15, 23, 42, 0.6); margin:5px; font-size:18px; border-radius: 15px; padding:5px;'
        )
        self.help.setFixedSize(opt_box.size())
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
        frame.layout().addWidget(self.opt_result_label)
        frame.layout().addWidget(btn_opt, alignment=Qt.AlignCenter)

        o_layout.addWidget(frame)
        o_layout.addWidget(self.file_box, alignment=Qt.AlignCenter)
        o_layout.addWidget(self.help, alignment=Qt.AlignCenter)
        opt_box.setLayout(o_layout)

        main_layout.addWidget(self.pred_box)
        main_layout.addWidget(opt_box)
        self.setLayout(main_layout)

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

        if len(df) > 1:
            dlg = QInputDialog(self)
            dlg.setStyleSheet("background-color: rgba(15, 23, 42, 0.6)")
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

        self.file_status_label.setText(f"Loaded: ({len(valid_keys)} valid cols)")
        row = df.iloc[rownum]
        for key in valid_keys:
            label = self.data_analytics.feature_map[key]
            if label in self.inputs:
                self.inputs[label].setText(str(row[key]))

    # --------------------------
    def run_prediction(self):
        if self.loaded_df is not None:
            inputs_from_file = {}
            for feat, label in self.data_analytics.feature_map.items():
                class Dummy:
                    def __init__(self, v): self.v = v
                    def text(self): return str(self.v)
                if feat in self.loaded_df.columns:
                    inputs_from_file[label] = Dummy(self.loaded_df.iloc[0][feat])
                else:
                    inputs_from_file[label] = None
            pred = self.data_analytics.predict(inputs_from_file)
            self.result_label.setText(f"Predicted: {pred:.2f} KWh")
            if self.imp_cb.isChecked():
                self.show_feature_importance_chart()
            if self.te_cb.isChecked():
                self.show_total_energy_chart()
            if self.tr_cb.isChecked():
                self.progress = QProgressDialog("True Total Energy in progress...", None, 0, 0, self)
                self.progress.setStyleSheet("background-color: rgba(15, 23, 42, 1)")
                self.progress.resize(600, 300)
                self.progress.setWindowTitle("Please wait ... (1min)")
                self.progress.setWindowModality(Qt.WindowModal)
                self.progress.setCancelButton(None)
                self.progress.show()
                self.show_true_energy_chart()
                self.progress.close()
            return

        pred = self.data_analytics.predict(self.inputs)
        if self.imp_cb.isChecked():
            self.show_feature_importance_chart()
        if self.te_cb.isChecked():
            self.show_total_energy_chart()
        if self.tr_cb.isChecked():
            self.progress = QProgressDialog("True Total Energy in progress...", None, 0, 0, self)
            self.progress.setStyleSheet("background-color: rgba(15, 23, 42, 1)")
            self.progress.resize(600, 300)
            self.progress.setWindowTitle("Please wait ... (1min)")
            self.progress.setWindowModality(Qt.WindowModal)
            self.progress.setCancelButton(None)
            self.progress.show()
            self.show_true_energy_chart()
            self.progress.close()
        self.result_label.setText(f"Predicted: {pred:.2f} KWh")

    # --------------------------
    def run_optimization(self):
        if self.loaded_df is not None:
            self.progress = QProgressDialog("optimize from file...", None, 0, 0, self)
            self.progress.setWindowTitle("Optimization ...")
            self.progress.setWindowModality(Qt.WindowModal)
            self.progress.setCancelButton(None)
            self.progress.show()

            self.predict_thread = QThread()
            self.predict_worker = PredictFileWorker(
                analytics=self.data_analytics,
                df=self.loaded_df,
                feature_map=self.data_analytics.feature_map
            )
            self.predict_worker.moveToThread(self.predict_thread)

            self.predict_thread.started.connect(self.predict_worker.run)
            self.predict_worker.finished.connect(self.on_optimization_done)
            self.predict_worker.finished.connect(self.predict_thread.quit)
            self.predict_worker.finished.connect(self.predict_worker.deleteLater)
            self.predict_thread.finished.connect(self.predict_thread.deleteLater)

            self.predict_thread.start()
            return

        self.progress = QProgressDialog("Optimization in progress...", None, 0, 0, self)
        self.progress.setStyleSheet("background-color: rgba(15, 23, 42, 0.6)")
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

    # --------------------------
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
        self.opt_result_label.setText(f"Optimized Energy: {float(best)} KWh")

        for feat_key, val in zip(self.data_analytics.model.feature_names_in_, variables):
            label = self.data_analytics.feature_map.get(feat_key)
            if label in self.inputs:
                row = self.input_rows[label]
                opt_label = QLabel(f"Opt: {val:.2f}")
                opt_label.setStyleSheet(glass_input_style)
                self.pre_grid.addWidget(opt_label, row, 2)

        self.ax1.clear()
        self.ax1.hist(self.data_analytics.Tot_e, bins=30, edgecolor='black')
        self.ax1.axvline(
            np.mean(self.data_analytics.Tot_e),
            linestyle='--',
            label=f"Mean: {int(np.mean(self.data_analytics.Tot_e))}"
        )
        self.ax1.axvline(best, linestyle='-.', label=f"Opt: {int(best)}")
        self.ax1.set_xlabel("Total Energy (KWh)")
        self.ax1.set_ylabel("Frequency")
        self.ax1.legend()
        self.figure1.tight_layout()
        semi_green = (0.2, 0.7, 0.0, 0)
        semi_orange = (1, 1, 1, 0.3)
        self.figure1.patch.set_facecolor(semi_green)
        self.ax1.patch.set_facecolor(semi_orange)
        self.canvas1.setStyleSheet("background:transparent; border-radius: 25px;")
        self.canvas1.setAttribute(Qt.WA_TranslucentBackground)
        self.canvas1.draw()

    # --------------------------
    def show_feature_importance_chart(self):
        fig, ax = plt.subplots()
        mdi = self.data_analytics.feature_importances_
        mdi.plot.barh(ax=ax)
        ax.set_title("Random Forest Feature Importances")
        ax.set_xlabel("Importance")
        for i, feat in enumerate(mdi.index):
            ax.text(
                mdi[feat] + 0.001, i,
                f"{self.data_analytics.last_input_values.get(feat,0):.2f}",
                va='center', fontsize=9
            )
        fig.tight_layout()
        fig.show()

    def show_total_energy_chart(self):
        fig, ax = plt.subplots()
        ax.hist(self.data_analytics.y_test, bins=30, edgecolor='black')
        ax.axvline(
            self.data_analytics.last_prediction,
            color='red', linestyle='--',
            label=f"User Prediction: {int(self.data_analytics.last_prediction)}"
        )
        ax.legend()
        ax.set_title("Total Energy Distribution")
        ax.set_xlabel("Total Energy (KWh)")
        ax.set_ylabel("Frequency")
        fig.tight_layout()
        fig.show()

    def show_true_energy_chart(self, filepath: str = "Merged_excells_Engy_Ct_K2_Sf_Nf_Tf.xlsx"):
        """
        رسم نمودار True vs Predicted برای 20% داده‌ی تست،
        طبق اسکریپت اصلی شما.
        اگر filepath داده شود، از آن خوانده می‌شود،
        در غیر این صورت از self.loaded_df.
        """
        if isinstance(filepath, str):
            df = pd.read_excel(filepath) if filepath.endswith('.xlsx') else pd.read_csv(filepath)
        elif self.loaded_df is not None:
            df = self.loaded_df.copy()
        else:
            QMessageBox.warning(self, "Data Missing", "No data available. Load via UI or pass filepath.")
            return

        drop_cols = [c for c in ['GAS_MEATN_EAF', 'HEEL_NO'] if c in df.columns]
        df = df.drop(columns=drop_cols, errors='ignore')

        X = df.iloc[:, :-1]
        y = df.iloc[:, -1].values

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=40
        )

        if 'HEAT' not in X_test.columns:
            QMessageBox.warning(self, "Missing Column", "Column 'HEAT' is required for plotting.")
            return
        heat_test = X_test['HEAT'].values
        X_test_proc  = X_test.drop(columns=['HEAT', 'DAT_EN'], errors='ignore')
        X_train_proc = X_train.drop(columns=['HEAT', 'DAT_EN'], errors='ignore')

        rf = RandomForestRegressor(n_estimators=100, random_state=42)
        rf.fit(X_train_proc, y_train)
        y_test_pred = rf.predict(X_test_proc)

        plt.figure(figsize=(6,6))
        plt.plot(y_test, y_test_pred, '.', alpha=0.6)
        m, M = np.min(y_test), np.max(y_test)
        plt.plot([m, M], [m, M], '--k')
        r2 = r2_score(y_test, y_test_pred)
        plt.text(0.4*(M+m), 0.6*(M+m), f'$R^2$ = {r2:.2f}')
        plt.xlabel('True Total Energy (KWh)')
        plt.ylabel('Predicted Total Energy (KWh)')
        plt.tight_layout()
        plt.show()

        df_y = pd.DataFrame({
            "HEAT": heat_test,
            "True": y_test,
            "Pred": y_test_pred
        }).sort_values(by='HEAT')

        plt.figure(figsize=(10,5))
        plt.plot(df_y['HEAT'], df_y['True'], '-o', label='True')
        plt.plot(df_y['HEAT'], df_y['Pred'], '-o', label='Predicted')
        plt.xlim(321050, 321450)
        plt.ylim(80000, 130000)
        plt.xlabel('Heat number (furnace: 2, year: 1403)')
        plt.ylabel('Total Energy (KWh)')
        plt.legend()
        plt.tight_layout()
        plt.show()
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
        pixmap = QPixmap("core.png").scaled(width, height,
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

        # ۳) اعمال ماسک پنجره براساس rounded
        self.setMask(rounded.mask())
        self.pixmap_rounded = rounded

        # لیبل‌های متن
        self.ai = QLabel("AI", self)
        self.ai.setAlignment(Qt.AlignCenter)
        self.ai.setStyleSheet("color: white;")
        font = QFont("Montserrat", 45, QFont.Bold)
        self.ai.setFont(font)
        size = QSize(900, 420)
        self.ai.resize(size)
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("color: white;")
        font = QFont("Montserrat", 30, QFont.Bold)
        self.label.setFont(font)
        self.label.resize(self.size())

        # افکت شفافیت
        self.opacity = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity)
        # تایمر افزایش فونت
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
        # زمان‌بندی fade-out پس از مدت زمان مشخص
        QTimer.singleShot(self.duration - 800, self.anim_out.start)

    def paintEvent(self, event):
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
        self.ai.setStyleSheet(f"color: {random.choice(['white', 'black', 'orange', 'darkred', 'white'])}; opacity: {random.choice([0.9, 1, 0.4, 0.1])};")
        f.setPointSize(f.pointSize() + random.choice([+1, +2, -1]))
        self.ai.setFont(f)
        self.elapsed += 40
        if self.elapsed + 1000 >= self.duration:
            self.font_timer.stop()


# ======================
# Main
# ======================
def start_main_app():
    global energy_win
    energy_win = EnergyApp()
    energy_win.resize(1280, 720)
    energy_win.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    splash = AnimatedSplash(duration=3000)
    splash.show()
    splash.anim_out.finished.connect(start_main_app)
    sys.exit(app.exec_())
