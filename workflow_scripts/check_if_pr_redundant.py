import argparse
from github import Github
from github.GithubException import GithubException
import os


# Parse command-line arguments using argparse
def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Check for changes and manage PRs for generated Dockerfiles."
    )
    parser.add_argument(
        '--current-branch',
        required=True,
        help="The branch that contains the new changes (e.g., feature branch)."
    )
    parser.add_argument(
        '--base-branch',
        required=True,
        help="The base branch to compare against (e.g., main)."
    )
    return parser.parse_args()


def delete_remote_branch(repo, branch_name):
    """Delete a remote branch using GitHub API."""
    try:
        ref = repo.get_git_ref(f'heads/{branch_name}')
        ref.delete()
        print(f"Remote branch {branch_name} deleted.")
    except GithubException as e:
        print(f"Failed to delete remote branch {branch_name}: {e}")


def main():
    # Parse arguments
    args = parse_arguments()

    # Authenticate using GitHub token (you can set this in your environment or pass it directly)
    g = Github(os.getenv('GITHUB_TOKEN'))

    # Set the repository you want to interact with
    repo = g.get_repo("username/repo_name")

    # Get the current branch and base branch from the arguments
    current_branch = args.current_branch
    base_branch = args.base_branch

    # Step 1: Check for changes in the generated Dockerfiles folder
    for pr in repo.get_pulls(state='open'):
        pr_branch_name = pr.head.ref

        # Compare the base branch and PR branch
        diff = repo.compare(base_branch, pr_branch_name)

        # Check for diffs in the /generated_dockerfiles folder
        generated_dockerfiles_changes = [
            file for file in diff.files if file.filename.startswith('generated_dockerfiles/')
        ]

        if len(generated_dockerfiles_changes) == 0:
            # If there are no diffs for the generated_dockerfiles folder, no need to create a new PR
            print(f"PR {pr.number} already covers the changes for /generated_dockerfiles. "
                  f"Deleting the current branch: {current_branch}.")

            # Delete the remote branch that was checked out
            delete_remote_branch(repo, current_branch)

            return  # Exit the script since the PR already covers the changes

    # Step 2: If no PR with the same changes was found, create a new PR
    diff = repo.compare(base_branch, current_branch)
    if diff.ahead_by > 0:
        print(f"Changes detected for {current_branch}, creating a new PR.")

        try:
            pr = repo.create_pull(
                title="Auto-generate Dockerfiles",
                body="Automated update",
                head=current_branch,
                base=base_branch
            )
            print(f"Created PR: {pr.html_url}")
        except GithubException as e:
            print(f"Error creating PR: {e}")
    else:
        print("No changes detected, skipping PR creation.")


if __name__ == "__main__":
    main()