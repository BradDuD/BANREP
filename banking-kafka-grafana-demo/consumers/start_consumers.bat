@echo off

start "Consumer A - PostgreSQL" cmd /k "python consumers\consumer_a_persistencia.py"

start "Consumer B - Fraude" cmd /k "python consumers\consumer_b_fraude.py"

start "Consumer C - Metricas" cmd /k "python consumers\consumer_c_metricas.py"

start "Consumer Alertas" cmd /k "python consumers\consumer_alertas.py"

echo.
echo Todos los consumers fueron iniciados.
pause