import argparse
from pathlib import Path
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


def build_and_push_image(client, dockerfile_path, docker_registry):
    try:
        # Build the Docker image
        print(f"Building image from {dockerfile_path}...")
        dockerfile_path = Path(dockerfile_path)
        image, build_logs = client.images.build(
            path=str(Path.cwd()), dockerfile=str(dockerfile_path)
        )

        # Extract the image SHA
        image_name = f"{docker_registry}/{dockerfile_path.parent.name.lower()}:{str(image.id).split(':')[1]}"

        # Tag the image with the SHA
        image.tag(image_name)

        # Push the Docker image to the registry
        print(f"Pushing image {image_name} to registry...")
        for line in client.images.push(image_name, stream=True, decode=True):
            print(line)
        print(f"Successfully pushed {image_name} to {docker_registry}")
    except docker.errors.BuildError as e:
        print(f"Build error for {dockerfile_path}: {e}")
        sys.exit(1)
    except docker.errors.APIError as e:
        print(f"API error for {dockerfile_path}: {e}")
        sys.exit(2)


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
