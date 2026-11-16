# Clayblock

Подготовка сборки 1.3.2 для LANMinecraft. [Авторский клиентский выпуск](https://www.curseforge.com/minecraft/modpacks/clayblock/files/7932186)

`tools/upstream-client-lock.json` фиксирует SHA256 и размер оригинального ZIP, ссылки на официальный источник, записи зависимостей и SHA256 файлов внутри авторских overrides. Minecraft и загрузчик взяты из оригинального манифеста. Java в `portable-pack.json` соответствует выбору текущего лаунчера для этой версии Minecraft и проверяется при запуске.

## Восстановление авторского клиента

Закреплённый авторский клиент CurseForge использует project ID 1481123 и file ID 7932186.
Для подготовки текущего кандидата из корня LANMinecraft запустите:

```powershell
python -B tools/PackData/CurseForge/release_overlay.py stage --pack-source LocalSources/Clayblock --output $stage
```

`tools/overlay.json` сохраняет политику открытия мира через Steam. Для нового авторского выпуска используйте описанную ниже проверку Clayblock. При изменении защищённого входа пересмотрите рецепт и закрепите новые точные байты. После нативной проверки сохраните полный `tools/upstream-lock.json`. Сценарий публикации проверяет базовый манифест по этому lock перед добавлением пресета.

Рецепт удаляет одну строку `version:3955` из авторского `kubejs/config/defaultoptions.txt`. KubeJS сам добавляет заголовок с версией при первом создании `options.txt`. NeoForge 21.1.219 останавливал следующий запуск, когда в файле оказывались два одинаковых ключа `version`. Остальные параметры шаблона сохраняются побайтно.

Для авторских обновлений Minecraft 1.21.1 и NeoForge сначала подготовьте новый `upstream-client-lock.json` обычной командой `prepare.py --client-only`. Затем пересчитайте точный слой Clayblock из этого lock и проверенного авторского ZIP:

```powershell
python -B LocalSources/Clayblock/tools/multiplayer_warning.py --launcher-source . --candidate-lock $newIntake --client-archive $authorZip
```

Команда выдаёт предложенные `overlay` и `packOwnedTxt`. Проверьте изменения и закрепите предложения в `tools/overlay.json` и `launcher/pack-owned.txt` вместе с новыми lock. Сценарий сохраняет `skipMultiplayerWarning:true`, добавляет строку при её отсутствии и убирает заголовок версии, который пишет KubeJS. Другие строки шаблона сохраняются побайтно. Если автор убрал весь шаблон или изменил платформу, подготовка останавливается до проверки нового штатного механизма. KubeJS читает шаблон только при создании `options.txt`.

`tools/curseforge-fallbacks.json` закрепляет Schematicannon `1350154/7034473`, для которого CurseForge вернул пустую запись метаданных. Полный JAR с официального CDN имеет размер 2 544 608 байт и SHA1 `8d73e80d83088f36be9953f1e27612bf142529c1`. Оба ID, имя файла и SHA1 совпадают с авторским lock выпуска 1.3.2. Подготовка сверяет полный SHA256. [Авторский lock Schematicannon](https://github.com/TrashboxBobylev/Clayblock/blob/2aae4f7850669321b3df4ee678104e21ba68fe70/mods/.index/schematicannon.pw.toml)

## Публикация

Раскладка для кнопки «Пресет управления» описана в [инструкции по раскладке](tools/keybinds/design.md). После коммита и обычной подготовки с полным lock запустите из корня LANMinecraft:

```powershell
python -B LocalSources/Clayblock/tools/stage_controls_release.py --launcher-source . --stage $stage --output $release --revision $revision
```

Сценарий использует штатную сборку архива библиотеки и игровых файлов. Пресет добавляется отдельным архивом. Загружайте новые архивы до замены манифеста `pack-latest`.
Сценарий проверяет `skipMultiplayerWarning:true` в подготовленном шаблоне и ещё раз читает шаблон из готового архива. Отсутствие строки, значение `false` и дубликаты блокируют выпуск.

У сборки MIT. В манифесте закреплён Collective, CF 342584/7148969. Условия мода требуют загрузку с CurseForge или Modrinth. [Условия](https://www.curseforge.com/minecraft/mc-mods/collective)

Пользователь подтвердил наличие разрешения на перезалив. Публикация следует после проверки полного состава и нативной приёмки.
