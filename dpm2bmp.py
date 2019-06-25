import sys
from functools import partial

BITMAP_HEADER = "424d"
DPM_HEADER = "44504D"

def getFileName(stream):
    terminator = "ffffffff"
    chunk = b""
    rawfilename = b""
    while chunk.hex() != terminator:
        chunk = stream.read(4)
        if chunk.hex() == terminator:
            continue
        rawfilename += chunk
    
    return bytes.fromhex(rawfilename.hex()).decode().replace("\x00", "")

def getHeader(stream):
    padding = stream.read(8)
    header = stream.read(4)
    return padding, header


if __name__ == "__main__":
    binf = open(sys.argv[1], 'rb')
    bitmaps = []

    # Header Validation
    
    file_header = binf.read(16)
    if not file_header.hex().startswith(DPM_HEADER):
        print("This is not a valid DPM File")

    bitmap_count = int(file_header[8])
    print(f"DPM contains {bitmap_count} files")


    # Bitmap header parsing
    for i in range(bitmap_count):
        filename = getFileName(binf)
        padding, header = getHeader(binf)
        print(filename, padding.hex(), header.hex())
        bitmaps.append([filename, header])
    
    buffer = bytearray(b"")
    current = -1
    iteration = 0
    first = True
    headerlist = [x[1].hex() for x in bitmaps]

    for chunk in iter(partial(binf.read, 1), b''):
        hexrepr = (chunk+binf.peek(1)[:1]).hex()
        buffer += chunk
        if hexrepr == BITMAP_HEADER:
            header = binf.peek(5)[1:5]
            if header.hex() in bitmaps[current + 1][1].hex():
                current += 1
                print(f"Found header pos: {hex(iteration)} for {bitmaps[current][0]}")
            else:
                continue

            if len(buffer) <= 1:
                continue

            print(f"Writing to {bitmaps[current - 1][0]}")
            with open(bitmaps[current - 1][0], "wb") as f:
                if buffer[-1] != 0x00:
                    buffer = buffer[:-1]
                f.write(buffer)
                
            buffer = bytearray(chunk)
        
        iteration += 1
        if iteration % 10000 == 0:
            print(f"position: {hex(iteration)}", end="\r")
    
    print(f"Writing to {bitmaps[current][0]}")
    with open(bitmaps[current][0], "wb") as f:
        f.write(buffer)
