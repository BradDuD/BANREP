@echo off

start "🗄 Consumer A - PostgreSQL" cmd /k "color 1F && python consumers\consumer_a_persistencia.py"

start "🚨 Consumer B - Fraude" cmd /k "color 4F && python consumers\consumer_b_fraude.py"

start "📊 Consumer C - Metricas" cmd /k "color 5F && python consumers\consumer_c_metricas.py"

start "🔔 Consumer Alertas" cmd /k "color 6F && python consumers\consumer_alertas.py"