@echo off
setlocal
cd /d %~dp0


echo Starting Consolidation...
title Consolidation
uv run src\utils\run_consolidation.py %*

pause
