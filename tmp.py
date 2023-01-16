import subprocess

# Use subprocess to call Docker pull
res = subprocess.run(
    ["docker", "save", "aas-backend:1.0.3"],
    shell=False,
    check=True,
    capture_output=True,
)
with open("test.tgz", "wb") as f:
    subprocess.run(["gzip"], input=res.stdout, stdout=f, check=True)
