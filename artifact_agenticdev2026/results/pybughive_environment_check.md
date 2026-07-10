# PyBugHive Environment Check

- PyBugHive tasks: 8
- Required Python versions: 3.7
- Ready: `false`
- Recommended path: `setup_required`

## Tools

| Tool | Available | Detail |
| --- | ---: | --- |
| git | True | `C:\Program Files\Git\cmd\git.EXE`: `git version 2.53.0.windows.1` |
| docker CLI | True | `C:\Program Files\Docker\Docker\resources\bin\docker.EXE`: `Docker version 29.4.3, build 055a478` |
| docker engine | False | `failed to connect to the docker API at npipe:////./pipe/dockerDesktopLinuxEngine; check if the path is correct and if the daemon is running: open //./pipe/dockerDesktopLinuxEngine: The system cannot find the file specified.` |
| pipenv | False | `pipenv`: `pipenv not found` |
| py launcher | True | `{'3.14': '<LOCAL_PYTHON>\\pythoncore-3.14-64\\python.exe', '3.13': '<LOCAL_PYTHON>\\Python313\\python.exe'}` |
| direct python | False | `{}` |

## Missing

- Python versions: 3.7

## Next Action

Install and start Docker Desktop, or provide `pipenv` plus the required Python versions before full reproducibility verification.
