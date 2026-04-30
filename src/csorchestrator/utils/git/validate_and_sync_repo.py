from pathlib import Path
from tempfile import TemporaryDirectory

from git import GitCommandError, InvalidGitRepositoryError, NoSuchPathError, Repo

from csorchestrator.core.report import Report
from csorchestrator.utils.git.try_git_clone_checkout import RefKind, resolve_ref_type, try_git_clone_checkout


def validate_and_sync_repo(repo_url: str, repo_ref: str, target_path: Path) -> Report:
    report = Report()

    # --- 1. Validate repo exists ---
    try:
        repo = Repo(target_path)
    except (InvalidGitRepositoryError, NoSuchPathError):
        report.append_error(f"{target_path} is not a valid git repository")
        return report

    if repo.bare:
        report.append_error("Repository is bare, expected a working tree")
        return report

    # --- 2. Check dirty state ---
    if repo.is_dirty(untracked_files=True):
        report.append_error("Repository has uncommitted or untracked changes")
        return report

    # --- 3. Clone reference repo in temp dir ---
    with TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        clone_report = try_git_clone_checkout(repo_url, repo_ref, tmp_path, depth_one=True)
        if clone_report.has_errors():
            return clone_report

        tmp_repo = Repo(tmp_path)

        try:
            # --- 4. Compare remotes ---
            tmp_url = next(tmp_repo.remote().urls)
            try:
                local_url = next(repo.remote().urls)
            except Exception:
                report.append_error("Failed to read remote URL")
                return report

            if local_url != tmp_url:
                report.append_error(f"Remote URL mismatch: local={local_url}, expected={tmp_url}")
                return report

            # --- 5. Resolve commits ---
            try:
                local_commit = repo.head.commit
                tmp_commit = tmp_repo.head.commit
            except Exception:
                report.append_error("Failed to resolve HEAD commit")
                return report

            # --- 6. Detect ref type ---

            ref_type = resolve_ref_type(tmp_repo, repo_ref)

            # --- 7. Compare depending on ref type ---
            if ref_type == RefKind.COMMIT or ref_type == RefKind.TAG:
                if local_commit.hexsha != tmp_commit.hexsha:
                    report.append_error(
                        f"{ref_type} mismatch: local={local_commit.hexsha}, expected={tmp_commit.hexsha}"
                    )
                    return report

            elif ref_type == RefKind.BRANCH:
                # Check branch names
                try:
                    current_branch = repo.active_branch.name
                    tmp_branch = tmp_repo.active_branch.name
                except TypeError:
                    report.append_error("Detached HEAD, expected a branch")
                    return report

                if current_branch != tmp_branch:
                    report.append_error(f"Branch mismatch: local={current_branch}, expected={tmp_branch}")
                    return report

                # --- Fast-forward check ---
                try:
                    base = repo.git.merge_base(local_commit.hexsha, tmp_commit.hexsha).strip()
                except GitCommandError:
                    report.append_error("Failed to compute merge base")
                    return report

                if base != local_commit.hexsha:
                    report.append_error("Local branch is not fast-forwardable")
                    return report

                # --- Perform fast-forward ---
                try:
                    repo.git.merge("--ff-only", tmp_commit.hexsha)
                except GitCommandError:
                    report.append_error("Fast-forward merge failed")
                    return report

            else:
                report.append_error(f"Unknown ref type for {repo_ref}")
                return report

        finally:
            # ensure to close files, important in windows
            tmp_repo.close()

    return report
