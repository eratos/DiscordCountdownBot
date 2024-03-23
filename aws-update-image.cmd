aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 999172883125.dkr.ecr.us-west-2.amazonaws.com

docker build -t discordo .

docker tag discordo:latest 999172883125.dkr.ecr.us-west-2.amazonaws.com/discordo:latest

docker push 999172883125.dkr.ecr.us-west-2.amazonaws.com/discordo:latest