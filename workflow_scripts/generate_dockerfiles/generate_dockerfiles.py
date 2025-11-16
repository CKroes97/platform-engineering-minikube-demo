import os

WEBSERVICES_DIR = "webservices"
REQUIREMENTS_DIR = "webservices_requirements"
MOUNT_DIR = "webservices_mountpaths"
OUTPUT_DIR = "generated_dockerfiles"


def generate_dockerfile(service_name, requirements_exists=False, mount_exists=False):
    """Generate a Dockerfile for the given service."""
    service_dir = os.path.join(OUTPUT_DIR, service_name)
    dockerfile_path = os.path.join(service_dir, "Dockerfile")

    os.makedirs(service_dir, exist_ok=True)

    dockerfile_lines = [
        f"# Auto-generated Dockerfile for {service_name}",
        "FROM python:3.13.9-slim",
        "WORKDIR /app",
        f"COPY {WEBSERVICES_DIR}/{service_name}.py /app/{service_name}.py",
    ]

    if requirements_exists:
        # Use forward slashes in the Dockerfile COPY path
        dockerfile_lines.append(
            f"COPY {REQUIREMENTS_DIR}/{service_name}.txt /app/requirements.txt"
        )
        dockerfile_lines.append(
            "RUN pip install --no-cache-dir -r /app/requirements.txt"
        )

    if mount_exists:
        mount_paths_file = os.path.join(MOUNT_DIR, f"{service_name}.txt")
        with open(mount_paths_file, "r", encoding="utf-8") as f:
            for line in f:
                mount_path = line.strip()
                if mount_path:
                    dockerfile_lines.append(f"COPY {mount_path}/ /app/{mount_path}/")

    dockerfile_lines.append(f'CMD ["python", "/app/{service_name}.py"]')
    dockerfile_content = "\n".join(dockerfile_lines) + "\n"

    with open(dockerfile_path, "w", encoding="utf-8") as dockerfile:
        dockerfile.write(dockerfile_content)

    print(f"Generated {dockerfile_path}")


def main():
    """Scan for Python services and generate Dockerfiles."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(WEBSERVICES_DIR):
        if filename.endswith(".py"):
            service_name = filename[:-3]  # Remove ".py" extension
            req_path = os.path.join(REQUIREMENTS_DIR, f"{service_name}.txt")
            requirements_exists = os.path.exists(req_path)
            mount_path = os.path.join(MOUNT_DIR, f"{service_name}.txt")
            mount_exists = os.path.exists(mount_path)
            generate_dockerfile(
                service_name,
                requirements_exists=requirements_exists,
                mount_exists=mount_exists,
            )


if __name__ == "__main__":
    main()
