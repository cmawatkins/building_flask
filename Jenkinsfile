pipeline {
	agent any

    stages {

		stage('Build') {
			steps {
			}
		}
		
		stage('Push') {
			steps {
				withCredentials([usernamePassword(credentialsId: 'azure_acr', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
				}
			}
		}

		stage('Deliver') {
			steps {
			}
		}
	}
}
