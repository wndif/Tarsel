@echo off
set a=5
:loop
type nul>collectCoverage%a%s.do
set /a a+=10
if %a% == 255 (goto end set a=5)
goto loop
:end