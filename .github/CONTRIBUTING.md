# Pull Request Process

Adhering to this process is the best way to get your work included in the
project:

1. [Fork](http://help.github.com/fork-a-repo/) the project, clone your fork,
   and configure the remotes:

   ```bash
   git clone https://github.com/andriyko/aiociscospark.git
   cd aiociscospark
   # Assign the original repo to a remote called "upstream"
   git remote add upstream https://github.com/andriyko/aiociscospark.git
   ```

2. Run the unit tests.  If you added new functionality, extend existing test cases or add new ones.
   ```bash
   make lint
   make test
   ```

3. If you cloned a while ago, get the latest changes from upstream:

   ```bash
   git checkout master
   git pull upstream master
   ```

4. Create a new branch (off the main project development branch) to
   contain your feature, change, or fix:

   ```bash
   git checkout -b <branch-name>
   ```

5. Commit your changes in logical chunks. For any Git project, some good rules
   for commit messages are
   * the first line is commit summary, 50 characters or less,
   * followed by an empty line
   * followed by an explanation of the commit, wrapped to 72 characters.

   The first line of a commit message becomes the **title** of a pull request on
   GitHub, like the subject line of an email. Including the key info in the
   first line will help us respond faster to your pull.

   If your pull request has multiple commits which revise the same lines of
   code, it is better to [squash](http://davidwalsh.name/squash-commits-git)
   those commits together into one logical unit.

   But you don't always have to squash &mdash; it is fine for a pull request to
   contain multiple commits when there is a logical reason for the separation.

6. Push your branch up to your fork:

   ```bash
   git push origin <branch-name>
   ```

7. [Open a Pull Request](https://help.github.com/articles/using-pull-requests/)
    with a clear title and description.

8. After your Pull Request is away, you might want to get yourself back onto
   `master` and delete the branch:

   ```bash
   git checkout master
   git branch -D <branch-name>
   ```

9. Increase the version numbers in any examples files and the README.md to the new version that this
   Pull Request would represent. The versioning scheme is [SemVer](http://semver.org/).
