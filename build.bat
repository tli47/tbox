@echo off
echo ======================================
echo          TBOX 打包脚本
echo ======================================

pyinstaller ^
--onefile ^
--windowed ^
--name TBOX ^
--icon=tbox.ico ^
--add-data "tbox.ui;." ^
--add-data "tbox.png;." ^
--clean ^
--noconsole ^
run.py

echo.
echo 打包完成！输出文件在 dist 文件夹
pause