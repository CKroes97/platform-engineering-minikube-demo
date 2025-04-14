import argparse
from github import Github
import os


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
        help="The folder to check for diffs.",
    )
    return parser.parse_args()


def delete_branch_from_github(repo, branch_name):
    """Delete the branch from GitHub."""
    ref = repo.get_git_ref(f"heads/{branch_name}")
    ref.delete()
    print(f"Branch '{branch_name}' has been deleted.")


# Function to get the repository and authenticated user
def get_repo_and_user(github_token, repo_name):
    """Authenticate to GitHub with a token and get the repository."""
    g = Github(github_token)
    repo = g.get_repo(repo_name)
    return repo


# Function to check if a PR already exists with no diff in the generated_dockerfiles folder
def check_existing_prs(repo, base_branch, current_branch, folder_to_check):
    """Check if an open PR exists with no diff in the specified folder."""
    open_prs = repo.get_pulls(state="open", base=base_branch)

    for pr in open_prs:
        # Compare the PR branch with the current branch
        if pr.head.ref == current_branch:
            # Check the diff of the PR to see if it contains changes in the specified folder
            files = pr.get_files()
            for file in files:
                if file.filename.startswith(folder_to_check):
                    print(
                        f"Found existing PR {pr.number} with changes in {folder_to_check}."
                    )
                    return pr
    return None


def main():
    args = parse_arguments()
    print(os.getenv("GITHUB_TOKEN"))
    g = Github(os.getenv("GITHUB_TOKEN"))
    current_branch = args.current_branch
    base_branch = args.base_branch
    repository = args.repository
    folder = args.folder

    repo = get_repo_and_user(g, repository)
    existing_pr = check_existing_prs(
        repo, base_branch, current_branch, folder
    )

    if existing_pr:
        print(
            f"Existing PR {existing_pr.number} found with no diff. "
            f"Deleting branch '{args.current_branch}'."
        )
        delete_branch_from_github(repo, args.current_branch)
    else:
        current_branch.merge(commit_message="Merge via Github Action")

if __name__ == "__main__":
    main()
