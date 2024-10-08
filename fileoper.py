import errno
import io
import os

def write_text_file(filename, content):
    try:
        #print(f"Writing to file: {filename}...")
        file_handle = io.open(filename, "w")
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise
    else:
        with open(filename, encoding='utf-8', mode='w+') as file_obj:
            file_obj.write(content)
