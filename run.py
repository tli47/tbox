import subprocess
import sys
import os
from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 防止路径问题
        ui_path = os.path.join(os.path.dirname(__file__), "tbox.ui")
        uic.loadUi(ui_path, self)

        # =========================
        # 左侧导航切换页面
        # =========================
        self.pushButton.clicked.connect(self.goto_network_test)
        self.pushButton_2.clicked.connect(self.goto_audio_test)

        # =========================
        # Ping功能
        # =========================
        self.pushButton_4.clicked.connect(self.do_ping)
        self.pushButton_3.clicked.connect(self.show_local_ip)

    # =========================
    # 页面切换
    # =========================
    def goto_network_test(self):
        # page index = 0
        self.stackedWidget.setCurrentIndex(0)

    def goto_audio_test(self):
        # 你目前只有一个page，可以先占位
        self.textBrowser.append("声音测试页面（未实现）")

    # =========================
    # Ping逻辑（模拟版）
    # =========================
    def do_ping(self):
        ip = self.lineEdit.text().strip()

        if not ip:
            self.textBrowser.append("[ERROR] IP不能为空")
            return

        self.textBrowser.append(f"[INFO] Pinging {ip} ...")

        # 简化模拟结果（你后面可以换 QProcess 真ping）
        self.textBrowser.append(f"[OK] Reply from {ip}: time=12ms")
        self.textBrowser.append(f"[OK] Reply from {ip}: time=11ms")
        self.textBrowser.append("")

    # =========================
    # 获取本地IP（简化版）
    # =========================
    def show_local_ip(self):
        #import socket
        #hostname = socket.gethostname()
        #ip = socket.gethostbyname(hostname)

        result = subprocess.run(
            ["ipconfig"],
            capture_output=True,
            text=True,
            encoding="gbk"  # Windows 中文必须注意编码
        )

        self.textBrowser.append(result.stdout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())