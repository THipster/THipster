# Contributing

:+1::tada: Thanks for taking the time to contribute! :tada::+1:

#### Table of contents

[Code of Conduct](#code-of-conduct)

[GitHub Workflow](#github-worklow)

[Scope of Pull Requests](#scope-of-pull-requests)

[How to Contribute ?](#how-to-contribute)
* [Reporting Bugs](#reporting-bugs)
* [Suggesting Enhancements](#suggesting-enhancements)
* [Pull Requests](#pull-requests)

[Styleguides](#styleguides)
* [Git Commit Messages](#git-commit-messages)
* [Python Styleguide](#python-styleguide)
* [Documentation Styleguide](#documentation-styleguide)

[Additional Notes](#additional-notes)
* [Issue and Pull Request Labels](#issue-and-pull-request-labels)

## Code of Conduct

## GitHub Worklow
The recommended workflow is to fork the repository and open pull requests from your fork.

### 1. Fork, clone & configure THipster upstream

- Click on the _Fork_ button on GitHub
- Clone your fork
- Add the upstream repository as a new remote

```shell
# Clone repository
git clone https://github.com/$YOUR_GITHUB_USER/$REPOSITORY.git

# Add upstream origin
git remote add upstream git@github.com:THipster/$REPOSITORY.git
```

### 2. Create a pull request

```shell
# Create a new feature branch
git switch -c my_feature_branch

# Make changes to your branch
# ...

# Commit changes
git commit

# Push your new feature branch
git push my_feature_branch

# Create a new pull request from https://github.com/THipster/$REPOSITORY
```

### 3. Update your pull request with latest changes

```shell
# Checkout main branch
git switch main

# Update your fork's main branch from upstream
git pull upstream main

# Checkout your feature branch
git switch my_feature_branch

# Rebase your feature branch changes on top of the updated main branch
git rebase main

# Update your pull request with latest changes
git push -f my_feature_branch
```

## Scope of Pull Requests
We prefer small incremental changes that can be reviewed and merged quickly. It's OK if it takes multiple pull requests to close an issue.  

The idea is that each feature / improvement branch should only live a few hours and be merged in THipster's main branch whithin a day at most.

## How to Contribute ?

### Reporting Bugs
#### How to Submit A Good Bug Report
Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). Start by creating an issue on the thipster repository by filling in [the template](https://github.com/THipster/THipster/blob/main/.github/ISSUE_TEMPLATE/bug_report.yml)  

Explain the problem and include additional details to help maintainers reproduce the problem:

* **Use a clear and descriptive title** for the issue to identify the problem.
* **Describe the exact steps which reproduce the problem** in as many details as possible. For example, start by explaining how you started THipster, e.g. which command exactly you used in the terminal, or how you started THipster otherwise. When listing steps, **don't just say what you did, but explain how you did it**.
* **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples. If you're providing snippets in the issue, use [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
* **Explain which behavior you expected to see instead and why.**
* **Include screenshots and animated GIFs** which show you following the described steps and clearly demonstrate the problem. You can use [this tool](https://www.cockos.com/licecap/) to record GIFs on macOS and Windows, and [this tool](https://github.com/colinkeenan/silentcast) or [this tool](https://github.com/GNOME/byzanz) on Linux.
* **If the problem wasn't triggered by a specific action**, describe what you were doing before the problem happened and share more information using the guidelines below.

Provide more context by answering these questions:

* **Did the problem start happening recently** (e.g. after updating to a new version of THipster) or was this always a problem?
* If the problem started happening recently, **can you reproduce the problem in an older version of THipster?** What's the most recent version in which the problem doesn't happen? You can download older versions of THipster from [the releases page](https://github.com/THipster/THipster/releases).
* **Can you reliably reproduce the issue?** If not, provide details about how often the problem happens and under which conditions it normally happens.

Include details about your configuration and environment:

* **Which version of THipster are you using?** You can get the exact version by running `thipster -v` in your terminal
* **What's the name and version of the OS you're using**?
* **What's the specific version of Python you are using?**
* **Which pip packages have you installed?**
* **Are you running THipster in a virtual machine?** If so, which VM software are you using and which operating systems and versions are used for the host and the guest?

### Suggesting Enhancements
#### How to Submit A Good Enhancement Suggestion
Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/). Start by creating an issue on the thipster repository by filling in [the template](https://github.com/THipster/THipster/blob/main/.github/ISSUE_TEMPLATE/feature.yml) and provide the following information:  

* **Use a clear and descriptive title** for the issue to identify the suggestion.
* **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
* **Provide specific examples to demonstrate the steps**. Include copy/pasteable snippets which you use in those examples, as [Markdown code blocks](https://help.github.com/articles/markdown-basics/#multiple-lines).
* **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
* **Include screenshots and animated GIFs** which help you demonstrate the steps or point out the part of THipster which the suggestion is related to. You can use [this tool](https://www.cockos.com/licecap/) to record GIFs on macOS and Windows, and [this tool](https://github.com/colinkeenan/silentcast) or [this tool](https://github.com/GNOME/byzanz) on Linux.
* **Explain why this enhancement would be useful** to most THipster users
* **List some other tools or applications where this enhancement exists.**
* **Specify which version of THipster you're using.** You can get the exact version by running `thipster -v` in your terminal
* **Specify the name and version of the OS you're using.**

### Pull Requests

The process described here has several goals:

- Maintain THipster's quality
- Fix problems that are important to users

Please follow these steps to have your contribution considered by the maintainers:

1. Choose one of the [pull request template available](#pull-requests-templates)
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing <details><summary>What if the status checks are failing?</summary>If a status check is failing, and you believe that the failure is unrelated to your change, please leave a comment on the pull request explaining why you believe the failure is unrelated. A maintainer will re-run the status check for you. If we conclude that the failure was a false positive, then we will open an issue to track that problem with our status check suite.</details>

While the prerequisites above must be satisfied prior to having your pull request reviewed, the reviewer(s) may ask you to complete additional design work, tests, or other changes before your pull request can be ultimately accepted.

#### Pull Requests Templates

1. :bug: Fix a bug
2. :zap: Improve performance
3. :memo: Update documentation
4. :sparkles: Add a feature

## Styleguides

### Git Commit Messages

* Use this format `<gitmoji><type>(optional scope): <description>`\
  More examples [here](https://github.com/arvinxx/gitmoji-commit-workflow/tree/master/packages/commitlint-config)
* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line
* Consider starting the commit message with an applicable emoji:

    > **Major release emojis**
    * :boom: `:boom:` Introduce breaking changes.

    > **Minor release emojis**
    * :sparkles: `:sparkles:` - Introduce new features.

    > **Patch release emojis**
    * :ambulance: `:ambulance:` - Critical hotfix.
    * :bug: `:bug:` - Fix a bug.
    * :adhesive_bandage: `:adhesive_bandage:` - Simple fix for a non-critical issue.
    * :lock: `:lock:` - Fix security issues.
    * :arrow_up:  `:arrow_up:` - Upgrade dependencies.
    * :arrow_down: `:arrow_down:` - Downgrade dependencies.
    * :heavy_plus_sign: `:heavy_plus_sign:` - Add a dependency.
    * :heavy_minus_sign: `:heavy_minus_sign:` - Remove a dependency.
    * :rotating_light: `:rotating_light:` - Fix compiler / linter warnings.
    * :zap: `:zap:` - Improve performance.
    * :recycle: `:recycle:` - Refactor code.
    * :wrench: `:wrench:` - Add or update configuration files.
    * :loud_sound: `:loud_sound:` - Add or update logs.
    * :mute: `:mute:` - Remove logs.
    * :goal_net: `:goal_net:` - Catch errors.
    * :wastebasket: `:wastebasket:` - Deprecate code that needs to be cleaned up.
    * :coffin: `:coffin:` - Remove dead code.
    * :chart_with_upwards_trend: `:chart_with_upwards_trend:` - Add or update analytics or track code.  
    * :globe_with_meridians: `:globe_with_meridians:` - Internationalization and localization.
    * :alien: `:alien:` - Update code due to external API changes.
    * :wheelchair: `:wheelchair:` - Improve accessibility.
    * :children_crossing: `:children_crossing:` - Improve user experience / usability.
    * :bricks: `:bricks:` - Infrastructure related changes.

    > **Other emojis**
    * :tada: `:tada:` - Begin a project.
    * :memo: `:memo:` - Add or update documentation.
    * :pencil2: `:pencil2:` - Fix typos.
    * :construction_worker: `:construction_worker:` - Add or update CI build system.
    * :green_heart: `:green_heart:` - Fix CI Build.  
    * :closed_lock_with_key: `:closed_lock_with_key:` - Add or update secrets.
    * :white_check_mark: `:white_check_mark:` - Add, update or pass tests.
    * :test_tube: `:test_tube:` - Add a failing test.
    * :clown_face: `:clown_face:` - Mock things.
    * :safety_vest: `:safety_vest:` - Add or update code related to validation.
    * :hammer: `:hammer:` - Add or update development scripts.
    * :stethoscope: `:stethoscope:` - Add or update healthcheck.
    * :busts_in_silhouette: `:busts_in_silhouette:` - Add or update contributor(s).
    * :see_no_evil: `:see_no_evil:` - Add or update .gitignore file.
    * :package: `:package:` - Add or update compiled files or packages.
    * :art: `:art:` - Improve structure / format of the code.

### Python Styleguide

All python code is linted with [Ruff](https://github.com/charliermarsh/ruff).

### Documentation Styleguide

* Use [Markdown](https://daringfireball.net/projects/markdown).
* Reference methods and classes in markdown with the custom `{}` notation:
    * Reference classes with `{ClassName}`
    * Reference instance methods with `{ClassName::methodName}`
    * Reference class methods with `{ClassName.methodName}`

## Additional Notes
### Issue and Pull Request Labels
