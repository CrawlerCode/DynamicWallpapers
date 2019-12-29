python -m pip install --upgrade pip
pip install crawlercodepythontools
pip install Pillow
pip install PySimpleGUIQt
pip install PySimpleGUI
pip install psutil
pip install pywin32
pip install pyinstaller
pyinstaller Dynamic-Wallpapers.py --onefile --noconsole --icon=icon.ico
move %cd%\dist\Dynamic-Wallpapers.exe %cd%
@RD /S /Q %cd%\dist
@RD /S /Q %cd%\build
echo 'Dynamic-Wallpapers successfully created!'
pause