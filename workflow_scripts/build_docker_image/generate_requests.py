import os
import argparse
import json
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from jinja2.exceptions import UndefinedError


def parse_args():
    parser = argparse.ArgumentParser(
        description="Render Kratix Runtime yml from Jinja2 templates for each Docker image."
    )
    parser.add_argument("--namespace", help="Kubernetes namespace", default="default")
    parser.add_argument("--env", help="Optional environment name to inject as 'env'")
    parser.add_argument(
        "--template-path",
        "-t",
        default="templates/runtime_requests.yml",
        help="Path of the Jinja2 template file",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        default="generated_python_webservices_requests",
        help="Directory to write rendered yml files",
    )
    parser.add_argument(
        "--image-tags-json",
        default="generated_dockerfiles/image_tags.json",
        help="Path to JSON file with image tags (generated during build)",
    )
    parser.add_argument("--docker-registry", default="localhost:30080")
    return parser.parse_args()


def render_template(template_path, output_dir, image_name, values):
    template_dir = str(Path(template_path).parent)
    template_file = str(Path(template_path).name)

    env = Environment(
        loader=FileSystemLoader(template_dir),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    try:
        template = env.get_template(template_file)
        rendered = template.render(values)
    except UndefinedError as e:
        print(f"❌ Error rendering {image_name}: {e}")
        return

    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, f"{image_name}.yml")

    with open(output_file, "w", encoding="utf-8") as out_file:
        out_file.write(rendered)

    print(f"✅ Rendered: {output_file}")


def main():
    args = parse_args()

    # Load image tag mapping
    with open(args.image_tags_json, "r", encoding="utf-8") as f:
        image_tags = json.load(f)

    for image_name, image_tag in image_tags.items():
        values = {
            "runtimeRequestName": image_name.replace("_", "-"),
            "namespace": args.namespace,
            "image": f"{args.docker_registry}/{image_name}:{image_tag}",
        }
        if args.env:
            values["env"] = args.env

        render_template(args.template_path, args.output_dir, image_name, values)


if __name__ == "__main__":
    main()
