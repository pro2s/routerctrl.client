# Router Control Client

settings.ini - настройки клиента
router.py - клиент сбора информации

test_online.sh - cron скрипт запуска проверки наличия наблюдателя

```
*/1* * * * /root/test_online.sh > /tmp/router.log 2>&1
```
Проверяет заходил ли пользователь на страницу и если заходил то обновляет информацию каждые 5 минут пока пользователь проявляет активность на сайте. Через 10 минут бездействия перестает посылать статистику.

