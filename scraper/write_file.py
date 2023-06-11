def write_into_file(filename, data):
    file = open(filename, "w")
    file.write(str(data))
    file.close()
