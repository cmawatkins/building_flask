pipeline {
	agent any

    stages {

		stage('Build') {
			steps {
				echo 'Build'
			}
		}
		
		stage('Push') {
			steps {
				withCredentials([usernamePassword(credentialsId: 'azure_acr', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
					echo 'Push'
				}
			}
		}

		stage('Deliver') {
			steps {
				echo 'Deliver'
			}
		}
	}
}
