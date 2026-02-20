# comands to use

## pylint

pylint --rcfile=.pylintrc src

## GIT

git add .
git commit -m "131952-add_pg_configs"
git push -u origin 131952-add_pg_configs

## Docker

- re-run & re-build your Docker Compose
docker-compose up --build
- shut down your Docker Compose
docker stop <container_id>
docker-compose down ?????????????

- check running dockers
docker ps
- check process
sudo lsof -i :4000
- kill process
kill -9 <PID>

docker exac -it <mycontainer> bash
