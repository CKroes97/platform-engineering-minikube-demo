import os

WEBSERVICES_DIR = "webservices"
OUTPUT_DIR = "generated_dockerfiles"


def generate_dockerfile(service_name):
    """Generate a Dockerfile for the given service."""
    service_dir = os.path.join(OUTPUT_DIR, service_name)
    dockerfile_path = os.path.join(service_dir, "Dockerfile")

    if os.path.exists(dockerfile_path):
        print(f"Skipping {service_name}, Dockerfile already exists.")
        return

    os.makedirs(service_dir, exist_ok=True)

    dockerfile_content = (
        f"# Auto-generated Dockerfile for {service_name}\n"
        "FROM python:3.11-slim\n"
        "WORKDIR /app\n"
        f"COPY {WEBSERVICES_DIR}/{service_name}.py /app/{service_name}.py\n"
        'CMD ["python", "/app/{service_name}.py"]\n'
    )

    with open(dockerfile_path, "w", encoding="utf-8") as dockerfile:
        dockerfile.write(dockerfile_content)

    print(f"Generated {dockerfile_path}")


def main():
    """Scan for Python services and generate Dockerfiles."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename in os.listdir(WEBSERVICES_DIR):
        if filename.endswith(".py"):
            service_name = filename[:-3]  # Remove ".py" extension
            generate_dockerfile(service_name)


if __name__ == "__main__":
    main()