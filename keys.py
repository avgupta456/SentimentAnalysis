#interface with private keys.txt file
#create a file named keys.txt and add the four keys each on a new line

def get_keys():
    f = open("keys.txt", "r")
    keys = []
    for key in f.readlines():
        keys.append(key.split("\n")[0])
    f.close()
    return keys
