@echo off
set a=1
:loop
type nul>collectCoverage%a%s.do
set /a a+=2
if %a% == 53 (goto end set a=1)
goto loop
:end