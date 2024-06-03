import re

# File path
file_path = 'publicids'

try:
    # Read the content of the file
    with open(file_path, 'r') as file:
        content = file.read()

    # Retrieve the value of cacheversions using regular expressions
    matches = re.search(r"cacheversions\s*=\s*'([^']+)'", content)

    if matches:
        # Get the value of cacheversions
        version_value = matches.group(1)

        # Change the value of cacheversions to something else
        new_version_value = "new_version_value_here"

        # Replace the value of cacheversions with the new version value
        modified_content = re.sub(r"cacheversions\s*=\s*'([^']+)'", f"cacheversions = '{new_version_value}'", content)

        print("Original cacheversions:", version_value)
        print("Modified content:", modified_content)

        # Write the modified content back to the file
        with open(file_path, 'w') as file:
            file.write(modified_content)
    else:
        print("No cacheversions found in the file.")

except FileNotFoundError:
    print(f"File '{file_path}' not found. Please make sure the file exists and the path is correct.")
except Exception as e:
    print("An error occurred:", e)
