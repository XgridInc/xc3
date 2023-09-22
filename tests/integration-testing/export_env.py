# export_env.py
import re

with open("../../infrastructure/terraform.auto.tfvars", "r") as f:
    content = f.read()

match = re.search(r'env\s+=\s+"(\w+)"', content)
if match:
    env_value = match.group(1)
    with open("config.py", "r+") as config_file:
        lines = config_file.readlines()
        for line in lines:
            if "env" in line:
                break
        else:  # This part is executed only if the loop completes without a break
            config_file.write(f'env = "{env_value}"\n')
            print("env appended successfully!")
else:
    print("env variable not found in terraform.auto.tfvars")