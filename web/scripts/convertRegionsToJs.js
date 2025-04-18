const fs = require("fs");
const path = require("path");

// Функция для конвертации GeoJSON файлов из папки в JS объект
const convertFolderToJs = (folderPath, outputPath, exportName) => {
    const regions = {};

    // Читаем все .geojson файлы из папки
    fs.readdirSync(folderPath)
        .filter((file) => file.endsWith(".geojson"))
        .forEach((file) => {
            const name = path.basename(file, ".geojson");
            const content = fs.readFileSync(
                path.join(folderPath, file),
                "utf8"
            );
            regions[name] = JSON.parse(content);
        });

    // Формируем содержимое JS файла
    const fileContent = `// Автоматически сгенерировано из GeoJSON файлов
export const ${exportName} = ${JSON.stringify(regions, null, 2)};
`;

    // Записываем результат
    fs.writeFileSync(outputPath, fileContent);
    console.log(`${outputPath} успешно создан`);
};

// Пути к папкам и файлам
const baseDir = path.join(__dirname, "..", "src", "data");
const skfoDir = path.join(baseDir, "skfo");
const yufoDir = path.join(baseDir, "yufo");

// Создаем JS файлы для каждого округа
convertFolderToJs(
    skfoDir,
    path.join(baseDir, "skfo", "regions.js"),
    "skfoRegions"
);

convertFolderToJs(
    yufoDir,
    path.join(baseDir, "yufo", "regions.js"),
    "yufoRegions"
);
