@echo off
set a=10
:loop
type nul>collectCoverage%a%s.do
set /a a+=10
if %a% == 530 (goto end set a=10)
goto loop
:end