from JsonParser import loadJson

def main():
    path = "testText.txt"
    data = loadJson(path)

    print(data["string"])

if __name__ == "__main__":
    main()