import argparse
import subprocess

from typing import List
from itertools import product


def build_images(
    repo: str,
    username: str,
    password: str,
    python_version: List[str],
    gradio_version: List[str],
    cuda_version: List[str],
    cudnn_version: List[str],
    skip_push: bool,
):
    """Build base images for inference services

    # TODO: Check if cuDNN version and CUDA version are compatible

    Args:
        repo (str): Repository to push images to
        username (str): Docker registry username
        password (str): Docker registry password
        python_version (List[str]): List of Python versions to target
        gradio_version (List[str]): List of Gradio versions to target
        cuda_version (List[str]): List of CUDA versions to target
        cudnn_version (List[str]): CUDNN versions to target
        skip_push (bool): If should skip push to registry
    """
    build_args = [python_version, cuda_version, cudnn_version, gradio_version]
    combinations = list(product(*build_args))

    login_command = (
        f"docker login -u {username} -p '{password}'"
    )
    try:
        subprocess.run(login_command, check=True, shell=True)
    except subprocess.CalledProcessError as err:
        print(f"Error logging in: {err}")

    for args in combinations:
        # Format build command
        python_version, cuda_version, cudnn_version, gradio_version = args
        command = "docker build "
        command += f"--build-arg PYTHON_VERSION={python_version} "
        command += f"--build-arg CUDA_VERSION={cuda_version} "
        command += f"--build-arg CUDA_VERSION={cudnn_version} "
        command += f"--build-arg GRADIO_VERSION={gradio_version} "

        tag = f"inference-engine:1.0.0-py{python_version}-gr{gradio_version}"
        cpu_tag = tag + "-cpu"
        gpu_tag = tag + f"-cuda{cuda_version}-cudnn{cudnn_version}"

        cpu_command = command + "-f dockerfiles/cpu.Dockerfile "
        gpu_command = command + "-f dockerfiles/gpu.Dockerfile "

        cpu_command += f"-t {cpu_tag} "
        gpu_command += f"-t {gpu_tag} "

        cpu_command += "."
        gpu_command += "."

        # Run build command
        for build_command in (gpu_command, cpu_command):
            try:
                subprocess.run(build_command, check=True, shell=True)
            except subprocess.CalledProcessError as err:
                print(f"Error building image for {build_command}: {err}")
                continue

        # Tag image and push to repository
        for tag in (cpu_tag, gpu_tag):
            tag_command = (
                f"docker tag {tag} {repo}/{tag}"
            )
            push_command = (
                f"docker login -u {username} -p '{password}' && docker push {repo}/{tag}"
            )

            try:

                subprocess.run(tag_command, check=True, shell=True)
                if not skip_push:
                    subprocess.run(push_command, check=True, shell=True)
            except subprocess.CalledProcessError as err:
                print(f"Error pushing image for {args} to {repo}: {err}")


if __name__ == "__main__":
    # Define the command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo", required=True, help="Docker repository to push the images to"
    )
    parser.add_argument(
        "--username", required=True, help="Username for the Docker repository"
    )
    parser.add_argument(
        "--password", required=True, help="Password for the Docker repository"
    )
    parser.add_argument(
        "--python_version",
        nargs="+",
        help="List of possible Python versions",
        default=["3.8", "3.9"]
    )
    parser.add_argument(
        "--gradio_version",
        nargs="+",
        help="List of possible Gradio versions",
        default=["2.9.4", "3.16.1"]
    )
    parser.add_argument(
        "--cuda_version",
        nargs="+",
        help="List of possible CUDA versions",
        default=["11.8"]
    )
    parser.add_argument(
        "--cudnn_version",
        nargs="+",
        help="List of possible CUDNN versions",
        default=["8.6"]
    )
    parser.add_argument(
        "--skip_push",
        action='store_true',
        default=False
    )
    args = parser.parse_args()
    # Call the build_and_push function with the command line arguments
    build_images(
        args.repo,
        args.username,
        args.password,
        args.python_version,
        args.gradio_version,
        args.cuda_version,
        args.cudnn_version,
        args.skip_push
    )
