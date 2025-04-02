@echo off
chcp 65001

echo 清理旧的打包文件...
if exist "dist" rmdir /s /q dist
if exist "build" rmdir /s /q build

echo 正在打包程序...
pyinstaller 2fa_tool.spec --noconfirm

if errorlevel 1 (
    echo 打包失败！请检查错误信息。
    pause
    exit /b 1
)

echo 打包完成！
set "EXEPATH=%~dp0dist\2fa_tool.exe"
echo 程序位于：%EXEPATH%
if exist "%EXEPATH%" (
    echo 文件已成功生成！
) else (
    echo 警告：未找到生成的文件！
)
pause