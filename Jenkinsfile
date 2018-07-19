pipeline {
	agent any

    checkout scm

    env.DOCKER_API_VERSION="1.23"
    
    sh "git rev-parse --short HEAD > commit-id"

    tag = readFile('commit-id').replace("\n", "").replace("\r", "")
    appName = "building-login"
    registryHost = "pittcontainerreg.azurecr.io/"
    imageName = "${registryHost}${appName}:${tag}"
    env.BUILDIMG=imageName

    stages {

		stage('Build') {
			steps {
				sh "docker build -t ${imageName} -f building_flask/Dockerfile building_flask"
			}
		}
		
		stage('Push') {
			steps {
				withCredentials([usernamePassword(credentialsId: 'azure_acr', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
					sh "docker login pittcontainerreg.azurecr.io -u $USERNAME -p $PASSWORD"
					sh "docker push ${imageName}"
				}
			}
		}

		stage('Deliver') {
			steps {
				git config --global user.email "twc17@pitt.edu"
				git config --global user.name "Jenkins Automation"

				git clone "https://github.com/twc17/k8s-infrastructure.git"

				cd k8s-infrastructure
				
				cat <<EOF > patch.yaml
				spec:
				template:
					spec:
					containers:
						- name: building-login-front
						image: pittcontainerreg.azurecr.io/${imageName}
				EOF

				kubectl patch --local -o yaml -f apps/building-login/deployments/building-login-front.yaml -p "$(cat patch.yaml)" > output.yaml

				mv output.yaml apps/building-login/deployments/building-login-front.yaml

				git add apps/building-login/deployments/building-login-front.yaml

				git commit -F- <<EOF
				Update the building-login application

				This commit updates the building-login-front deployment container image to:
				
					pittcontainerreg.azurecr.io/${imageName}
				EOF

				git push origin master
			}
		}
	}
}
