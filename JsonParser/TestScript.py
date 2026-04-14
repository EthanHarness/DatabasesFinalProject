from JsonParser.JsonParser import loadJson

def main():
    path = "./JsonParser/testText.txt"
    data = loadJson(path)

    for key,value in data.items():
        print(key, value, isinstance(value, dict), isinstance(value, list))

if __name__ == "__main__":
    main()