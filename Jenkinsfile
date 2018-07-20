node {
	
	checkout scm

	sh "git rev-parse --short HEAD > commit-id"

	tag = readFile('commit-id').replace("\n", "").replace("r", "")
	appName = "building-login"
	registryHost = "pittcontainerreg.azurecr.io/"
	imageName = "${registryHost}${appName}:${tag}"

	stage('Build') {
		sh "docker build -t ${imageName} -f building_flask/Dockerfile building_flask"
	}

	stage('Push') {
		withCredentials([usernamePassword(credentialsId: 'azure_acr', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
			sh "docker login pittcontainerreg.azurecr.io -u $USERNAME -p $PASSWORD"
			sh "docker push ${imageName}"
		}
	}

	stage('Deliver') {
		echo("Deliver")
		git "https://github.com/twc17/k8s-infrastructure"
		sh """
		cat <<EOF > patch.yaml
		spec:
		  template:
		    spec:
		      containers:
		        - name: building-login-front
		          image: ${imageName}"""
		
		sh """kubectl patch --local -o yaml -f apps/building-login/deployments/building-login-front.yaml -p "$(cat patch.yaml)" > output.yaml"""
	}
}
