
def init_file(name):
    try:
        file = open(name, 'x')
        #include calibrated reading
        #file.write("time in ms,temp 1,temp 2,temp 3,temp 4,temp 5,temp 6,temp 7,temp 8,raw 1,raw 2,raw 3,raw 4,raw 5,raw 6,raw 7,raw 8")
        #only raw reading
        file.write("time in ms,raw 1,raw 2,raw 3,raw 4,raw 5,raw 6,raw 7,raw 8")
    except OSError:
        file = open(name, 'a')
        file.write("\n")
    file.close()
    return

def write_line(name, line):
    length = len(line)
    file = open(name, 'a')
    file.write("\n" + str(line[0]))  
    for i in range(1, length):
        file.write("," + str(line[i]))
    file.close()