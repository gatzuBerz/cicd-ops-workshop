# CI/CD and containers

> **MLOps & DevOps Workshop**

In this module, you change a small machine learning project and let the CI/CD pipeline check, build, train and deploy it for you.
You only need a browser and an account on GitHub.

## Exercises

1. [CI/CD: reading and changing a pipeline](exercises/01-cicd.md)
2. [Containers: build, push and train in an image](exercises/02-containers.md)
3. [Deployment: serve the model in a container](exercises/03-deployment.md)

Container demo located in the `docker_demo` directory in case you are curious.

## Setup

1. Fork this repository: on the repository page, click **Fork**.
2. In your fork, open the **Actions** tab, and enable workflows. The workflows only write to your fork.
3. You'll be editing file by file. If you need to create a new file, use the **Add File** button at the top of the interface.
4. For file edits, there is a pen at the top of each file, the shortcut for **Edit in Place** is `E`.

After making an edit you are asked if you want to commit and push the change you've made. Title the commit so you can return to it.

Then open the **Actions** tab of your fork to see the new workflow runs.

## Solutions

The exercise instructions contain both hints and solutions. You are kindly asked to attempt the problem yourself before copying the solution. This is meant to be there only so you do not get stuck!

## Repository

To change:

- `src/ci_cd/train.py`: trains the model and saves it to `model/`.
- `src/ci_cd/api.py`: serves the model with a web API.
- `Dockerfile`: builds the image that runs the training.
- `deployment.Dockerfile`: builds the image that serves the model.
- The CI configuration:
   - `.github/workflows/ci.yml`: checks the code, and trains the model on demand.
   - `.github/workflows/docker.yml`: builds the image on every push.
   - `.github/workflows/train-docker.yml`: trains the model in an image from the registry.
   - `.github/workflows/deploy.yml`: serves the model in a container, and checks that it answers.
   - `.gitlab-ci.yml`: the pipeline for GitLab CI/CD (if using GitLab).
- `tests/test_model.py`: checks the model accuracy.
- `tests/test_api.py`: checks the web API.

The other files are there to complete the repository (i.e. `uv.lock` for reproducibility, `.gitignore` to prevent committing local files, you have likely seen these before).

To see the pipelines/workflows made by this repository:

- **GitLab**: in your project, go to **Build -> Pipelines**.
- **GitHub**: in your repository, open the **Actions** tab.

## Exercise implementation and observations

### Exercise 1

The intentional failures were reproduced locally and on separate GitHub branches; `main` retains the corrected settings:

- [Tasks 1-2: unused import fails lint while tests and training pass](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40339670104).
- [Task 3: training reports 70% accuracy and the quality test fails](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40339904462).
- [Task 4: an empty test split fails tests and training](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40340088149).

- An unused `import os` fails lint with `F401`. Removing it restores lint.
- GitHub's `lint` and `test` jobs are independent because neither declares `needs`.
- One tree with depth one trains successfully with accuracy `0.7000`, but fails the test's `0.80` quality threshold.
- `TEST_SIZE = 0` raises `InvalidParameterError` at `train_test_split` in `load_data`, before training.
- Default settings remain `N_ESTIMATORS = 10`, `MAX_DEPTH = None`, and `TEST_SIZE = 0.2`. The optional extension reads the first two settings from environment variables.

### Exercise 2

- `.dockerignore` allows only `requirements.txt` and `src/` into the image, excluding Python caches.
- **Docker** publishes commit-SHA and branch tags to GHCR. Manual main-branch runs train with the exact commit tag. Push-triggered training is configured for source changes on `main` only.
- The branch tag moves with each build; the SHA tag identifies a specific commit. Branch-name slashes are replaced with hyphens for Docker tags.
- Training mounts `./model` at `/app/model` and uploads it as the `model` artifact for 30 days. Without the mount, removing the container also removes its model.

### Exercise 3

- `GET /health` returns `{"status": "ok"}` and has an API test. **Deploy** retries that endpoint before sending predictions.
- Manual **Deploy** defaults to training run `40336508685`, recorded in Git, rather than implicitly deploying `latest`. Its input can select another run or explicitly compare `latest`. The optional linked pipeline passes its own run ID instead.
- The deployment container downloads the selected model at startup, not during the image build. Its logs report the source run ID.
- A newer training run does not change an explicitly selected run ID. Once its artifact expires, a new deployment using that ID cannot download the model.
- The training image runs training; `deployment.Dockerfile` runs the API. `/health` is a machine-facing endpoint, unlike the human-facing `/docs` page.

Local validation passes formatting, lint, all six tests, and GitHub Actions workflow validation. A local pre-push hook now runs the tests before publishing changes.

Initial hosted validation was launched explicitly with `workflow_dispatch`; the final audit also verifies actual push-triggered runs:

- [CI: lint, tests, and training passed](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40336508685).
- [Docker: image publishing and container training passed](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40337071708), with accuracy `1.0000`.
- [Manual training with an older commit-tagged image passed](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40336995818).
- [Deploy: pinned model download, health check, and both predictions passed](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40336919485).

The downloaded container-trained model is in the ignored local directory `model/artifacts/40336529771/`. Deployment here is a smoke test on a temporary GitHub runner, not a persistent public API.

## Task-by-task completion audit

Scope: all required tasks and all explicitly optional extensions, as requested. Expected red runs are isolated on demonstration branches; `main` keeps the working implementation.

| Requirement | Result and evidence |
| --- | --- |
| Setup: fork, clone, dependencies, enabled Actions, green baseline | Done; native fork and [successful baseline CI](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40336508685). |
| Exercise 1 Tasks 1-2: lint failure and independent tests | Done; [lint fails while tests and training pass](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40339670104). |
| Exercise 1 Task 3: weak model, failed quality gate, successful training | Done; [training reports 70%, tests reject it](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40339904462). |
| Exercise 1 Task 4: invalid test split and restoration | Done; [invalid split fails on GitHub](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40340088149); main retains the valid split. |
| Exercise 2 Task 1: inspect unrestricted image, then restrict it | Done; [original image includes Git history, tests, and docs](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40346796055); [corrected image contains only requirements and source](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40337071708). |
| Exercise 2 Task 2: registry login and commit/branch tags across builds | Done; [first image](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40336529771) and [second image](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40337071708) publish SHA tags and move `main`. |
| Exercise 2 Task 3: manual image training, older image, downloaded artifact | Done; [older SHA-tagged image trains successfully](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40336995818); artifact downloaded locally. |
| Exercise 2 Task 3: build then train automatically after a push | Done; the actual [source-changing main push builds, trains, and deploys](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40349959592). |
| Exercise 2 question: what happens without the volume mount? | Demonstrated; [training loses its output and artifact upload fails](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40348599125). The [original unfinished training workflow](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40346812224) is also visible before the fix. |
| Exercise 3 Task 1: initial latest-model deployment | Done; [original deployment downloads a model at startup and waits on docs](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40347000066). |
| Exercise 3 Task 2: pin model and redeploy after newer training | Done; [repeat deployment still selects run 40336508685](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40337317017). |
| Exercise 3 Task 3: tested health endpoint and container readiness | Done; API tests and [container deployment](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40346584678) check health and predictions. |

### Optional extensions

| Extension | Result and evidence |
| --- | --- |
| Run tests before pushing | Done locally: installed `pre-push`; a real push of `extension-pre-push-blocked` failed before publication because `TEST_SIZE = 0`. Intentional hosted failures explicitly skip this hook only for their demonstration push. |
| Select training settings when launching CI | Done; [manual inputs produce 70% without a source edit](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40347043685). Inputs affect the training job; tests independently validate the default model. |
| Compare model quality against a baseline | Done; default model passes; [baseline-only branch fails the required five-percentage-point margin](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40347670024). |
| Test Python 3.12, 3.13, and 3.14 | Done; [all three matrix jobs pass](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40346567680). |
| Compare cached and uncached CI | Done; [uncached](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40347026697) Python 3.12 job: 10 seconds; [cached](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40347043685): 13 seconds. Dependency sync took 1 second in both; cache restores are visible, but this measurement shows no speedup. |
| Train only for main-branch source changes | Done; the actual [source-changing push trains and deploys](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40349959592), while the [documentation-only push skips training and deployment](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40349204301). |
| Label image with its commit | Done; [build log](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40346584678) shows revision `212d88eb7e1bbd451e2b3ab88c8bdf27a4cae0fb`. Label placement after dependency installation avoids invalidating that expensive layer. |
| Let Docker check container health | Done; [deployment log](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40346584678) shows `docker ps` reporting `(healthy)`. |
| Deploy exactly the model just trained | Done on an actual push; [build -> train -> deploy](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40349959592) passes its own run ID to deployment, selecting that run's model artifact. |
| Run the serving container locally | Blocked: no Docker executable or usable WSL distribution was found. Hosted container tests do not replace this local-container requirement. A native API preview is available at `http://127.0.0.1:8765/docs`; health and setosa prediction were checked. This preview is not a container. |

### Answers and verification limits

- Full commit SHAs are on GitHub commit pages or available with `git rev-parse HEAD`. A branch tag tracks the newest published branch image; a SHA tag identifies a particular commit's image. Use a digest for strict image immutability.
- Omitting `-v` writes the model only inside the container; `--rm` then deletes it. A separate image-pull step makes its timing visible.
- The training and deployment images perform different jobs. Both install the same dependency versions so saved models remain compatible.
- Startup logs identify the selected model run. Startup downloads keep model versions and credentials out of the built image, but require GitHub availability when starting a container.
- Readiness retries allow model download and server startup. Health checks are a small machine-facing contract; docs are a human-facing page that can be disabled.
- A pinned model selection is unchanged by later training; `latest` can select a different model. Artifact retention is 30 days: new starts fail after expiration, while an already-running process keeps its loaded model. No artifacts were deleted to simulate expiration.
- Lint checks style and likely mistakes; accuracy and baseline tests check behavior. Training can complete without meeting either quality gate. Pre-push tests help prevent broken code from leaving the machine; branch protection is an additional repository policy, not enabled by this audit.
- GitHub Actions is enabled. Push-triggered runs were initially absent from the inspected history, but were subsequently verified explicitly: [source change runs the full pipeline](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40349959592); [documentation-only changes skip training and deployment](https://github.com/gatzuBerz/cicd-ops-workshop/actions/runs/40349204301). Manual dispatch was not used as a substitute for this proof.
- GitLab-specific instructions are alternatives, not additional requirements for this GitHub fork.
