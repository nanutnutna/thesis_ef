import re


LOG_FILE = "download_images.log"
OUTPUT_FILE = "filtered"


def filter_download(log_file, output_file,word):
    try:
        with open(log_file, 'r') as file:
            lines = file.readlines()
        f_lines = [line for line in lines if word in line]

        if f_lines:
            with open(f'{output_file}_{word}.log', 'w') as file:
                file.writelines(f_lines)
            print(f"Found {len(f_lines)} error(s). Saved to '{output_file}'")
        else:
            print("No matching error logs found.")

    except FileNotFoundError:
        print(f"Log file '{log_file}' not found.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")

if __name__ == "__main__":
    filter_download(LOG_FILE, OUTPUT_FILE,word="SUCCESS")
    filter_download(LOG_FILE, OUTPUT_FILE,word="ERROR")
