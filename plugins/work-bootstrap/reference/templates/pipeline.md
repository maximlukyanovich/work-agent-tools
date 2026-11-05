# Templates — A pipeline that runs the gate

### A pipeline that runs the gate leaves the deploys alone

For `full gate: ci` on GitLab where no pipeline runs the gate yet, and the
runner is a shell runner shared with the deploys, with neither the toolchain
nor docker access. A runner with a container image drops the toolchain steps;
the rest holds. Observed on a live project: a check stage placed before the
deploy was rolled back the same day; as a job of merge request pipelines, its
first run caught a real defect in about three minutes on four cores.

- **The job runs in merge request pipelines only.** Branch pipelines that
  deploy are not touched, so a red check never stands between a merge and its
  deploy. That leaves two pipelines on one sha, which is why the merge reads
  the status by `merge.md`, "Waiting for CI".
- **The job brings its own toolchain into the runner's home** — the version
  the repository pins, and the package manager's store — so runs share them.
  `variables:` does not expand the shell's `$HOME`: the paths are set in the
  script.
- **A disk threshold comes first.** The same disk serves the deploys: below
  the threshold the job fails before it installs anything.
- **Merging on green is switched on last**, by a maintainer, after the first
  green run — "Pipelines must succeed". Read it with
  `glab api projects/:id --jq .only_allow_merge_if_pipeline_succeeds`. Under it
  a merge request with no pipeline cannot merge.

The skeleton, for Node; `<project>`, `<gate>` and `<runner tag>` are the
project's, and the threshold is a measured one:

```yaml
stages:
  - check
  # the project's deploying stages stay as they are

check:
  stage: check
  rules:
    - if: $CI_PIPELINE_SOURCE == "merge_request_event"
  interruptible: true
  timeout: 30m
  variables:
    MIN_FREE_KB: '2097152'
    COREPACK_ENABLE_DOWNLOAD_PROMPT: '0'
  script:
    - |
      export TOOLS_DIR="$HOME/.cache/<project>-ci"
      export COREPACK_HOME="$TOOLS_DIR/corepack"
      export npm_config_store_dir="$TOOLS_DIR/pnpm-store"
    - |
      free_kb=$(df --output=avail -k "$HOME" | tail -1)
      if [ "$free_kb" -lt "$MIN_FREE_KB" ]; then
        echo "Only $((free_kb / 1024)) MB free, $((MIN_FREE_KB / 1024)) MB needed"
        exit 1
      fi
    - |
      node_version=$(cat .nvmrc)
      node_dir="$TOOLS_DIR/node-v$node_version-linux-x64"
      if [ ! -x "$node_dir/bin/node" ]; then
        mkdir -p "$TOOLS_DIR"
        rm -rf "$TOOLS_DIR"/node-v*
        curl -fsSL "https://nodejs.org/dist/v$node_version/node-v$node_version-linux-x64.tar.gz" | tar -xz -C "$TOOLS_DIR"
      fi
      export PATH="$node_dir/bin:$PATH"
    - corepack enable
    - pnpm install --frozen-lockfile
    - <gate>
  tags:
    - <runner tag>
```

### A probe job says what the runner has

What the runner holds is read, not asked: a throwaway branch whose
`.gitlab-ci.yml` holds only this job, so no deploy runs. A push to the
project's remote, on the developer's word; the branch is deleted once the log
is read. The script stays a block: a plain YAML line holding `: ` is a
mapping, and such a pipeline fails with no job.

```yaml
probe:
  script:
    - |
      id -un; echo "$HOME"; nproc
      command -v node && node -v || echo 'node: none'
      command -v corepack || echo 'corepack: none'
      docker ps -q > /dev/null && echo 'docker: ok' || echo 'docker: no access'
      command -v curl; command -v tar
      df --output=avail -k "$HOME" | tail -1
  tags:
    - <runner tag>
```
