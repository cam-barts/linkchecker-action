# Link Checker
This action takes checks each link in a repository, and returns that link's status code if it isn't 200. 

## Example usage

- Run a cron every 5 minutes and on every push

\[ .gihub\workflows\myworkflow.yml \]

```yml
on:
  schedule:
  - cron: '*/5 * * * *'
  push:
name: Link Checker
jobs:
  linkchecker:
    name: linkchecker
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@master
    - name: linkchecker
      uses: cam-barts/linkchecker-action@master
```

## Example Output 
```
https://github.com/sdras/awesome-actions/actions?workflow=Lint+Awesome+List got status code 404 (./Readme.md)
```


## Known Issues
 - 404's on workflows (see above example)
 - No way to exclude links from output
 - No way to change verbosity
 - Only prints the output, doesn't do anything further (such as open an issue)
 - Not exactly beautiful

## PULL REQUESTS WELCOME
