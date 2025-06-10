@echo off
::有3w的账号
start "" "./v7.exe" "账号1" "密码" --is3w --num100 20 --num200 10 --num500 16 --num1000 16 --num2000 1
start "" "./v7.exe" "账号2" "密码" --is3w --num100 20 --num200 10 --num500 16 --num1000 16 --num2000 1
::没有3w的账号
start "" "./v7.exe" "账号2" "密码" --num100 0 --num200 0 --num500 0 --num1000 0 --num2000 10
echo 所有程序已启动
