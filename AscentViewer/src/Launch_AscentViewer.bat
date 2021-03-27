:: AscentViewer, a Python image viewer.
:: Copyright (C) 2020-2021 DespawnedDiamond, A Crazy Town and other contributors
::
:: This file is part of AscentViewer.
::
:: AscentViewer is free software: you can redistribute it and/or modify
:: it under the terms of the GNU General Public License as published by
:: the Free Software Foundation, either version 3 of the License, or
:: (at your option) any later version.
::
:: AscentViewer is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
:: GNU General Public License for more details.
::
:: You should have received a copy of the GNU General Public License
:: along with AscentViewer.  If not, see <https://www.gnu.org/licenses/>.

@echo off

:: thanks to
:: https://stackoverflow.com/questions/2730643/how-to-execute-programs-in-the-same-directory-as-the-windows-batch-file 
:: and https://stackoverflow.com/questions/11269338/how-to-comment-out-add-comment-in-a-batch-cmd
:: and https://stackoverflow.com/questions/21772060/batch-file-try-catch (is not currently used)

:: NOTE: should probably fix the keyboardinterrupt thing

::if %ERRORLEVEL% neq 0 goto ProcessError

py "%~dp0\AscentViewer_files"

:::ProcessError
::python "%~dp0\AscentViewer_files\ascv_launcher.py"
