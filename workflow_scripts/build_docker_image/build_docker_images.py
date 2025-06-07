import argparse
from pathlib import Path
import json
import docker
import os
import sys


def parse_arguments():
    parser = argparse.ArgumentParser(description="Build and push Docker images.")
    parser.add_argument(
        "--dockerfiles-dir",
        type=str,
        required=True,
        help="Directory containing the Dockerfiles.",
    )
    parser.add_argument(
        "--docker-registry",
        type=str,
        required=True,
        help="Docker registry to push the images to.",
    )
    return parser.parse_args()


def find_dockerfiles(dockerfiles_dir):
    dockerfiles_dir = Path(dockerfiles_dir)
    dockerfile_paths = [
        str(path.resolve() / "Dockerfile")
        for path in dockerfiles_dir.iterdir()
        if path.is_dir() and (path / "Dockerfile").exists()
    ]
    return dockerfile_paths


def set_github_env_var(name, value):
    github_env = os.getenv("GITHUB_ENV")
    if not github_env:
        raise RuntimeError("GITHUB_ENV not set")
    with open(github_env, "a") as f:
        f.write(f"{name}={value}\n")


def build_and_push_image(client, dockerfile_path, docker_registry):
    try:
        # Build the Docker image
        print(f"Building image from {dockerfile_path}...")
        dockerfile_path = Path(dockerfile_path)
        image, build_logs = client.images.build(
            path=str(Path.cwd()), dockerfile=str(dockerfile_path)
        )

        # Extract the image SHA
        image_name = dockerfile_path.parent.name.lower()
        image_tag = str(image.id).split(":")[1]
        image_name_tagged = f"{docker_registry}/{image_name}:{image_tag}"

        # Tag the image with the SHA
        image.tag(image_name_tagged)

        set_github_env_var("DOCKER_IMAGE", image_name_tagged)

        # Push the Docker image to the registry
        print(f"Pushing image {image_name_tagged} to registry...")
        for line in client.images.push(image_name_tagged, stream=True, decode=True):
            print(line)
        print(f"Successfully pushed {image_name_tagged} to {docker_registry}")
    except docker.errors.BuildError as e:
        print(f"Build error for {dockerfile_path}: {e}")
        sys.exit(1)
    except docker.errors.APIError as e:
        print(f"API error for {dockerfile_path}: {e}")
        sys.exit(2)

    update_image_tag(image_name, image_tag)


def update_image_tag(
    service_name, new_tag, json_path="generated_dockerfiles/image_tags.json"
):
    json_path = Path(json_path)

    if json_path.exists():
        with json_path.open("r") as f:
            existing_tags = json.load(f)
    else:
        existing_tags = {}

    existing_tags[service_name] = new_tag

    with json_path.open("w") as f:
        json.dump(existing_tags, f, indent=2)


def main():
    args = parse_arguments()
    dockerfiles_dir_name = args.dockerfiles_dir
    docker_registry = args.docker_registry
    dockerfiles_dir = Path(dockerfiles_dir_name)
    if not dockerfiles_dir.exists():
        print(f"Directory '{dockerfiles_dir}' does not exist.")
        return

    client = docker.from_env()

    client.login(
        username=os.getenv("DOCKER_REGISTRY_USERNAME"),
        password=os.getenv("DOCKER_REGISTRY_PASSWORD"),
        registry=docker_registry,
    )

    try:
        dockerfile_paths = find_dockerfiles(dockerfiles_dir)
        for dockerfile_path in dockerfile_paths:
            build_and_push_image(client, dockerfile_path, docker_registry)
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
