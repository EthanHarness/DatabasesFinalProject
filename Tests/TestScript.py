from JsonParser.ParsedJson import loadJson

def main():
    path = "./Tests/JsonParserPackageTestFile.txt"
    data = loadJson(path)

    for key,value in data.items():
        print(key, value, isinstance(value, dict), isinstance(value, list))

if __name__ == "__main__":
    main()