# Lab 3 - Containerizing the model with Docker

**Student:** Noura

### Question 1: Open the "Models" tab in the mlflow UI. What version number was your model given? What's the difference between a run's logged model artifact and a registered model?
- **Version Number:** Version 2.
- **Difference:** A run's logged model artifact is an immutable file tied strictly to a specific experimental run inside tracking. A registered model provides centralized lifecycle management across all experiment runs, enabling named versioning, lineage tracking, and deployment aliases (such as \champion\) without modifying or re-running original experiments.

### Question 2: What aliases replaced the old built-in stages in mlflow? Why version a model separately from the run that produced it, and why is an alias more flexible than a fixed stage name?
- **Aliases:** Custom aliases like \champion\ and \challenger\ replaced fixed legacy stages (\Staging\, \Production\, \Archived\).
- **Separate Versioning:** Decouples exploratory training runs from candidate models considered for production.
- **Alias Flexibility:** Aliases act as dynamic pointers. You can repoint \champion\ to a new model version at any time without changing deployment configurations or rebuilding images.

### Question 3: Why load the model through an mlflow model URI (\models:/food11@champion\) instead of pointing directly at the \.pth\ file on disk? What would you have to change to serve a newer model version?
- **Why URI:** The URI decouples the serving application from filesystem paths, local filenames, or manual file copying. The service always asks the registry for whatever model holds the alias.
- **Serving a newer model version:** Zero code changes are required in \serve.py\ or the Docker image. You simply update the \champion\ alias pointer in MLflow to the new model version, and restart or reload the service.

### Question 4: Why copy \pyproject.toml\/\uv.lock\ and run \uv sync\ before copying the rest of the source code, instead of copying everything at once? What happens to the build cache when you only change a line in \serve.py\?
- **Build Caching:** Docker executes instructions sequentially and caches layers. Dependencies change rarely, while application code changes frequently. By installing dependencies first, Docker reuses the heavy \uv sync\ layer from cache.
- **Changing \serve.py\:** Only the \COPY src /app/src\ layer and subsequent steps are invalidated. The dependencies are not reinstalled, allowing the build to complete in seconds.

### Question 5: What's the size difference between a naive single-stage image and your multi-stage one? Use \docker history <image>\ to see which layers are the biggest.
- The multi-stage build strips build utilities, cached wheels, and temporary files from the final runtime image.
- Running \docker history food11-api:latest\ reveals that the largest layer is the copied virtual environment (\/app/.venv\), dominated by PyTorch and Torchvision binaries.

### Question 6: What happens to build speed and image size if you forget the \.dockerignore\? Which of the excluded folders would actually break the build if they were sent to the Docker daemon?
- **Build Speed and Image Size:** Missing \.dockerignore\ forces the Docker daemon to send large directories like \data/\, \mlruns/\, and \.git/\ as part of the build context, dramatically slowing down the initial build and inflating image size.
- **Breaking the Build:** Sending a local Windows \.venv/\ into a Linux-based Docker image breaks the runtime due to OS/architecture incompatibility (Windows \.pyd\ vs Linux \.so\ binary extensions).

### Question 7: Why can't the container simply use \127.0.0.1:5000\ to reach the mlflow server on your host? What does \host.docker.internal\ resolve to?
- **Loopback Isolation:** Inside a container, \127.0.0.1\ refers to the container's isolated network namespace, where no MLflow server is listening.
- **\host.docker.internal\:** A special internal DNS name provided by Docker Desktop on Windows/macOS that resolves to the host machine's internal gateway IP, enabling network requests to reach host-bound services.

### Question 8: Stop the container and start a new one from the same image. Does the model still load correctly without you rebuilding? What does that tell you about what's baked into the image versus fetched at runtime?
- **Behavior:** The new container starts and loads the model without rebuilding the image.
- **Baked vs Runtime:** The image bakes in the Python runtime, dependencies, and API code. The model weights and metadata are fetched dynamically at runtime across the network from the MLflow registry upon startup.

### Question 9: The Dockerfile and image are versioned differently — one lives in git, the other doesn't (yet). What's still missing before another machine (like a CI runner or a Kubernetes cluster) could reliably pull and run the exact image you just built?
- An image registry (such as Docker Hub, GitHub Container Registry \ghcr.io\, AWS ECR, or Google Artifact Registry) to host and distribute the container image.
- Explicit semantic tags or commit SHA tags (e.g., \ood11-api:v1.0.0\ or \ood11-api:sha-<commit>\) pushed to the registry so remote systems can pull deterministic builds.
