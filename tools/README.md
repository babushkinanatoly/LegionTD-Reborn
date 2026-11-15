# Запуск на Windows

1. Steam → Dota 2 → Свойства → DLC → включить **Dota 2 Workshop Tools**.
2. Скачать репозиторий (Code → Download ZIP или `git clone`) в постоянную папку, например `C:\dev\LegionTD-Reborn`.
   Не переносить папку после установки — ссылки сломаются (тогда просто запустить install.bat снова).
3. Двойной клик `tools\install.bat`. Он сам найдёт Dota и создаст ссылки:
   - `dota 2 beta\game\dota_addons\legion_td` → `репо\game\dota_addons\legion_td`
   - `dota 2 beta\content\dota_addons\legion_td` → `репо\content\dota_addons\legion_td`
   Если в Dota уже была настоящая папка `legion_td` — она переименуется в `legion_td_backup_<дата>`.
4. Двойной клик `tools\launch.bat` — откроется Workshop Tools с аддоном legion_td.
   (Вручную: Steam → Dota 2 → «Launch Dota 2 - Tools» → выбрать legion_td.)
5. Открыть консоль (клавиша `` ` `` или окно VConsole) и ввести:
   ```
   dota_launch_custom_game legion_td legion_td_4v4
   ```
6. Если что-то сломалось: лог консоли лежит в `dota 2 beta\game\dota\console.log` (пишется благодаря `-condebug`). Его и присылать.

Чит-команды в чате (работают в Workshop Tools, там включены читы): `-start` / `-skip` — следующая волна сразу, `-stop` — остановить раунд.
