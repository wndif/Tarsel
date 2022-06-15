@echo off
set a=4
:loop
type nul>collectCoverage%a%s.do
set /a a+=4
if %a% == 152 (goto end set a=4)
goto loop
:end