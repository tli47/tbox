import sys
import os

from PySide6.QtGui import Qt, QIcon, QPixmap
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import QProcess,QFile, QIODevice, Qt

import numpy as np
import sounddevice as sd


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # =========================
        # 1. 修改窗口标题为 TBOX
        # =========================
        self.setWindowTitle("TBOX")

        # =========================
        # 2. 设置窗口左上角图标
        # =========================
        icon_path = os.path.join(os.path.dirname(__file__), "tbox.png")
        self.setWindowIcon(QIcon(icon_path))

        # 防止路径问题
        ui_path = os.path.join(os.path.dirname(__file__), "tbox.ui")
        # 加载 .ui 文件
        ui_file = QFile(ui_path)
        # 修复：增加打开失败判断
        if not ui_file.open(QIODevice.OpenModeFlag.ReadOnly):
            print(f"无法打开UI文件：{ui_path}")
            return

        #ui_file.open(QIODevice.OpenModeFlag.ReadOnly)

        # 加载界面
        loader = QUiLoader()
        self.ui = loader.load(ui_file)
        ui_file.close()
        self.setCentralWidget(self.ui)

        if not self.ui:
            print("UI 文件加载失败！")
            return


        # =========================
        # 3. （可选）把左侧 TBOX 文字换成图标
        # =========================
        # 先把原来的 textBrowser_2 换成 QLabel（在Qt Designer里改）
        # 然后用代码加载图标：
        logo_pix = QPixmap(icon_path).scaled(180, 60, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.ui.label_2.setPixmap(logo_pix)

        # =========================
        # 左侧导航切换页面
        # =========================
        self.ui.pushButton.clicked.connect(self.goto_network_test)
        self.ui.pushButton_2.clicked.connect(self.goto_audio_test)

        # =========================
        # Ping功能
        # =========================
        self.ui.pushButton_4.clicked.connect(self.do_ping)
        self.ui.pushButton_3.clicked.connect(self.show_local_ip)

        # =========================
        # 声音测试功能（核心！）
        # =========================
        self.refresh_audio_devices()  # 开机自动刷新喇叭列表
        self.ui.pushButton_5.clicked.connect(self.test_speaker)  # 测试按钮

        # =========================
        # 关于按钮
        # =========================
        self.ui.pushButton_6.clicked.connect(self.show_about_dialog)

        # ========== 去掉所有TextBrowser底部横杠 ==========
        self.remove_textbrowser_bars(self.ui.textBrowser)
        self.remove_textbrowser_bars(self.ui.textBrowser_3)

        self.process=None

    def remove_textbrowser_bars(self, text_browser):
        # 1. 永久隐藏水平/垂直滚动条
        text_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 底部横杠
        text_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # 右边滚动条（可选）
        # 去掉底部边框（真正去掉横杠）
        #text_browser.setStyleSheet("""
        #        QTextBrowser {
        #            border: 1px solid #ccc;
        #            border-bottom: 1px solid #ccc;
        #            background-color: white;
        #        }
        #    """)

    # =========================
    # 页面切换
    # =========================
    def goto_network_test(self):
        # page index = 0
        self.ui.stackedWidget.setCurrentIndex(0)

    def goto_audio_test(self):
        # 你目前只有一个page，可以先占位
        self.ui.stackedWidget.setCurrentIndex(1)

    # =========================
    # Ping逻辑（模拟版）
    # =========================
    def do_ping(self):
        ip = self.ui.lineEdit.text().strip()
        if not ip:
            self.ui.textBrowser.append("[ERROR] IP不能为空\n")
            return
        self.ui.textBrowser.append(f"[INFO] Pinging {ip} ...\n")
        # 如果已有进程，先结束
        if self.process:
            self.process.kill()
        self.process = QProcess(self)
        # 绑定信号
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        # Windows ping
        self.process.start("ping", [ip, "-n", "4"])

    # ===== 输出处理 =====
    def handle_stdout(self):
        data = self.process.readAllStandardOutput()
        text = bytes(data).decode("gbk", errors="ignore")
        self.ui.textBrowser.append(text)
    def handle_stderr(self):
        data = self.process.readAllStandardError()
        text = bytes(data).decode("gbk", errors="ignore")
        self.ui.textBrowser.append(f"[ERROR] {text}")
    def handle_finished(self):
        self.ui.textBrowser.append("\n[INFO] Ping finished\n")

    # =========================
    # 获取本地IP（简化版）
    # =========================
    def show_local_ip(self):
        #import socket
        #hostname = socket.gethostname()
        #ip = socket.gethostbyname(hostname)

        # 如果已有进程，先结束
        if self.process:
            self.process.kill()
        self.process = QProcess(self)
        # 绑定信号
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        # Windows show local ip
        self.process.start("ipconfig")

    # =========================
    # 【声音核心】获取所有喇叭设备
    # =========================
    def refresh_audio_devices(self):
        self.ui.comboBox.clear()
        devices = sd.query_devices()

        for i, dev in enumerate(devices):
            if dev['max_output_channels'] > 0:  # 只显示有喇叭的设备
                name = dev['name']
                self.ui.comboBox.addItem(f"{i}: {name}", i)

        self.ui.textBrowser_3.append(f"[INFO] 已加载 {self.ui.comboBox.count()} 个播放设备")

    # =========================
    # 【声音核心】播放测试音
    # =========================
    def test_speaker(self):
        try:
            # 获取选中的设备
            idx = self.ui.comboBox.currentData()
            name = self.ui.comboBox.currentText()
            self.ui.textBrowser_3.append(f"\n[测试] 正在播放：{name}")

            # 生成 800Hz 测试音（清晰好听）
            fs = 44100
            t = np.linspace(0, 1, fs * 1, False)
            tone = np.sin(2 * np.pi * 800 * t) * 0.3

            # 播放
            sd.play(tone, samplerate=fs, device=idx)
            sd.wait()

            self.ui.textBrowser_3.append("[结果] ✅ 播放成功！")

        except Exception as e:
            self.ui.textBrowser_3.append(f"[错误] ❌ 播放失败：{str(e)}")

    # =========================
    # 关于对话框
    # =========================
    def show_about_dialog(self):
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtGui import QPixmap

        # 1. 创建消息框
        msg = QMessageBox(self)
        msg.setWindowTitle("关于 TBOX 工具")

        # 2. 设置你的文字（原样不动）
        msg.setText("""
TBOX 多功能测试工具

版本：V1.0

功能：
• 网络测试（Ping / 本地IP）
• 声音测试（扬声器检测）

作者：Terry""")

        # ✅ 3. 关键：隐藏左侧大图标（这一句就够）
        msg.setIcon(QMessageBox.NoIcon)

        # 4. 显示
        msg.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
