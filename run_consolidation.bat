@echo off
setlocal
cd /d %~dp0


echo Starting Consolidation...
title Consolidation
uv run src\miyori\utils\run_consolidation.py %*

pause
