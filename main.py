import os
import hashlib
import csv
import sys

KEEP_STATUS = "To keep"
REMOVE_STATUS = "To remove"

KEEP_STATUS_ACTION = "Kept"
REMOVE_STATUS_ACTION = "Removed"

blacklist = ["Thumbs.db", ".DS_Store"]

photo_list = []
photo_map = dict()

def enumerateInPath(path, computeHash=True, verbose=False):
    # Enumerate all the files in path
    files = ["{}/{}".format(path, f) for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
    dirs = ["{}/{}".format(path, f) for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

    # Manage all the files
    for file in files:
        if verbose:
            print("Managing ", file)

        manageFile(file, computeHash)

    # Recall function on all the subdirectories
    for dir in dirs:
        enumerateInPath(dir, computeHash=computeHash, verbose=verbose)

def manageFile(filename, computeHash):
    if computeHash:
        hash = hashlib.sha512(open(filename,'rb').read()).hexdigest()
    else:
        hash = ""

    # Add in photo map
    if hash in photo_map:
        status = REMOVE_STATUS
    else:
        photo_map[hash] = filename
        status = KEEP_STATUS

    # Check filename in blacklist
    for elem in blacklist:
        if elem in filename:
            status = REMOVE_STATUS
    
    photo_list.append([filename, hash, status])

def usage():
    print("USAGE: python3 main.py <dir_path> <out_file> [options]")
    print("  --help|-h    : Print help guide")
    print("  --verbose|-v : Verbose output")
    print("  --remove|-r  : Remove automatically duplicates")
    print()
    print("Note: <out_file> will be in .cvs format")

def readInlineParams():

    remove = False
    verbose = False
    dirPath = None
    outFile = None

    if len(sys.argv) < 3:
        usage()
        sys.exit(1)

    dirPath = sys.argv[1]
    outFile = sys.argv[2]

    for i in range(3, len(sys.argv)):
        arg = sys.argv[i]

        if arg == "--verbose" or arg == "-v":
            verbose = True
        elif arg == "--remove" or arg == "-r":
            remove = True
        elif arg == "--help" or arg == "-h":
            usage()
            sys.exit(1)

    return dirPath, outFile, remove, verbose

def removeDuplicates():
    count = 0

    for elem in photo_list:
        if elem[2] == REMOVE_STATUS:
            os.remove(elem[0])
            count += 1

    return count

def main():
    dirPath, outFile, remove, verbose = readInlineParams()

    # Enumerate elements
    print("Enumerating all the elements")
    enumerateInPath(dirPath, computeHash=True, verbose=verbose)
    print(len(photo_list), "files enumerated")

    # Remove duplicates if indicated
    if remove:
        count = removeDuplicates()
        print(count, "files removed")

    # Write out file
    print("Writing output file")
    fOut = open(outFile, 'w', encoding='UTF8')
    writer = csv.writer(fOut)
    writer.writerow(["Filename", "SHA-512", "Status"])

    for elem in photo_list:
        if remove and elem[2] == KEEP_STATUS:
            elem[2] = KEEP_STATUS_ACTION
        elif remove and elem[2] == REMOVE_STATUS:
            elem[2] = REMOVE_STATUS_ACTION

        writer.writerow(elem)

    fOut.close

    # Final enumeration only is removal performed
    if remove:
        photo_list.clear()
        enumerateInPath(dirPath, computeHash=False, verbose=verbose)
        print(len(photo_list), "files enumerated")

main()