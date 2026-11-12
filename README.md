# Clayblock

Подготовка сборки 1.3.2 для LANMinecraft. [Авторский клиентский выпуск](https://www.curseforge.com/minecraft/modpacks/clayblock/files/7932186)

`tools/upstream-client-lock.json` фиксирует SHA256 и размер оригинального ZIP, ссылки на официальный источник, записи зависимостей и SHA256 файлов внутри авторских overrides. Minecraft и загрузчик взяты из оригинального манифеста. Java в `portable-pack.json` соответствует выбору текущего лаунчера для этой версии Minecraft и проверяется при запуске.

## Восстановление авторского клиента

Закреплённый авторский клиент CurseForge использует project ID 1481123 и file ID 7932186.
Для подготовки текущего кандидата из корня LANMinecraft запустите:

```powershell
python -B tools/PackData/CurseForge/release_overlay.py stage --pack-source LocalSources/Clayblock --output $stage
```

`tools/overlay.json` сохраняет политику открытия мира через Steam. Для нового авторского выпуска снимите отдельную квитанцию через `prepare.py --client-only` и проверьте её командой `release_overlay.py review-update`. При изменении защищённого входа пересмотрите рецепт и закрепите новые точные байты. После нативной проверки сохраните полный `tools/upstream-lock.json` и выполните `release_overlay.py verify` по готовому манифесту.

`tools/curseforge-fallbacks.json` закрепляет Schematicannon `1350154/7034473`, для которого CurseForge вернул пустую запись метаданных. Полный JAR с официального CDN имеет размер 2 544 608 байт и SHA1 `8d73e80d83088f36be9953f1e27612bf142529c1`. Оба ID, имя файла и SHA1 совпадают с авторским lock выпуска 1.3.2. Подготовка сверяет полный SHA256. [Авторский lock Schematicannon](https://github.com/TrashboxBobylev/Clayblock/blob/2aae4f7850669321b3df4ee678104e21ba68fe70/mods/.index/schematicannon.pw.toml)

## Публикация

У сборки MIT. В манифесте закреплён Collective, CF 342584/7148969. Условия мода требуют загрузку с CurseForge или Modrinth. [Условия](https://www.curseforge.com/minecraft/mc-mods/collective)

Пользователь подтвердил наличие разрешения на перезалив. Публикация следует после проверки полного состава и нативной приёмки.
