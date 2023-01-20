# Create a docker container with all required elements
```
./docker_run.py build
```

# Inside the docker container, build litgen, srcml, etc. and run the tests
```
./docker_run.py exec "cd /dvp/sources && ci_scripts/ci_build_and_test.sh"
```
