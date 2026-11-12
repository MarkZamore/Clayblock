# Clayblock

Подготовка сборки 1.3.2 для LANMinecraft. [Авторский клиентский выпуск](https://www.curseforge.com/minecraft/modpacks/clayblock/files/7932186)

`tools/upstream-client-lock.json` фиксирует SHA256 и размер оригинального ZIP, ссылки на официальный источник, записи зависимостей и SHA256 файлов внутри авторских overrides. Minecraft и загрузчик взяты из оригинального манифеста. Java в `portable-pack.json` соответствует выбору текущего лаунчера для этой версии Minecraft и проверяется при запуске.

## Восстановление авторского клиента

Из корня LANMinecraft используйте `tools/PackData/CurseForge/prepare.py` с `--project-id 1481123` и `--file-id 7932186`. Укажите этот lock через `--expect` и новый каталог внутри своего стенда через `--output`. Полная подготовка проверяет все заявленные зависимости. Отдельный lock поставки и метаданные карточки готовятся после запуска и проверки фактического состава.

## Публикация

У сборки MIT. В манифесте закреплён Collective, CF 342584/7148969. Условия мода требуют загрузку с CurseForge или Modrinth. [Условия](https://www.curseforge.com/minecraft/mc-mods/collective)
