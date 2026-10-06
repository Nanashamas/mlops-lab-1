Question 1 (uv init files): Already answered in your file (pyproject.toml, .python-version, etc.).

Question 2 (Dependencies): Explains that pyproject.toml lists direct dependencies and constraints, while uv.lock records exact resolved versions and hashes for reproducibility.

Question 3 (.dvc directory): Contains internal DVC configuration (config) and state cache directory pointers.

Question 4 (data.dvc): Contains the hash (md5) of the tracked folder, total size, and number of files.

Question 5 (.gitignore after dvc add): DVC automatically appends /data to .gitignore so Git does not track large binary data files.

Question 6 (Local vs Cloud Remote): Specify Option 1: Local storage directory at C:\Users\Noura\dvc_local_storage.

Question 7 (Why DVC instead of Git): Git is designed for text/source code and degrades severely when tracking large binary files; DVC stores pointers/hashes in Git while keeping heavy data outside the repository.

Question 8 (git/dvc checkout rollback): Checking out commit 19183b4 and running dvc checkout removed food11_processed and food11_processed_mini, leaving only food11_raw, demonstrating version control across datasets.