@echo off
echo ========================================
echo CORRIGINDO ASSOCIACAO DE ARQUIVOS .PY
echo ========================================
echo.

echo Verificando associacao atual...
assoc .py
ftype Python.File
echo.

echo Corrigindo associacao...
assoc .py=Python.File
ftype Python.File="C:\Python313\python.exe" "%%1" %%*

echo.
echo ========================================
echo CORRECAO CONCLUIDA!
echo ========================================
echo.
echo Testando...
python --version
echo.
echo Se a versao do Python apareceu acima, a correcao funcionou!
echo.
pause
