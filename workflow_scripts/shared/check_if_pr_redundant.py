import argparse
import os

from github import Github


# Parse command-line arguments using argparse
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Check for changes and manage PRs for generated Dockerfiles."
    )
    parser.add_argument(
        "--current-branch",
        required=True,
        help="The branch that contains the new changes (e.g., feature branch).",
    )
    parser.add_argument(
        "--base-branch",
        required=True,
        help="The base branch to compare against (e.g., main).",
    )
    parser.add_argument(
        "--repository",
        required=True,
        help=r"Github repository (use ${{ github.repository in github action}})",
    )
    parser.add_argument(
        "--folder",
        default="generated_dockerfiles",
        help="Comma-separated list of folders to check for diffs.",
        type=lambda s: [f.strip() for f in s.split(",") if f.strip()],
    )
    return parser.parse_args()


def delete_branch_from_github(repo, branch_name):
    """Delete the branch from GitHub."""
    ref = repo.get_git_ref(f"heads/{branch_name}")
    ref.delete()
    print(f"Branch '{branch_name}' has been deleted.")


# Function to get the repository and authenticated user
def get_repo_and_user(github, repo_name):
    """Authenticate to GitHub with a token and get the repository."""
    repo = github.get_repo(repo_name)
    return repo


# Function to check if a PR already exists with no diff in the generated_dockerfiles folder
def check_existing_prs(repo, base_branch, current_branch, folders_to_check):
    """Check if an open PR exists with diffs in any of the specified folders."""
    open_prs = repo.get_pulls(state="open", head=current_branch, base=base_branch)
    for pr in open_prs:
        for file in pr.get_files():
            if any(file.filename.startswith(folder) for folder in folders_to_check):
                print(f"Found existing PR {pr.number} with changes in {file.filename}.")
                return pr
    return None


def main():
    args = parse_arguments()
    g = Github(os.getenv("GITHUB_TOKEN"))
    current_branch = args.current_branch
    base_branch = args.base_branch
    repository = args.repository
    folder = args.folder

    repo = get_repo_and_user(g, repository)
    existing_pr = check_existing_prs(repo, base_branch, current_branch, folder)

    if existing_pr:
        print(
            f"Existing PR {existing_pr.number} found with diff. "
            f"Merging and deleting branch '{args.current_branch}'."
        )
        existing_pr.merge(
            commit_message="Merge via Github Action", merge_method="squash"
        )
        delete_branch_from_github(repo, args.current_branch)
    else:
        print(
            f"Existing PR no PR found with diff. "
            f"Deleting branch '{args.current_branch}'."
        )
        delete_branch_from_github(repo, args.current_branch)


if __name__ == "__main__":
    main()
