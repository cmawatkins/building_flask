pipeline {
  agent any
  stages {
    stage('Build') {
      steps {
        echo 'Build test from laptop '
        sh 'git rev-parse --short HEAD > commit-id'
        sh '''tag = readFile(\'commit-id\').replace("\\n", "").replace("\\r", "")
'''
        sh 'imageName = "${registryHost}${appName}:${tag}"'
        sh 'docker build -t ${imageName} -f building_flask/Dockerfile building_flask'
      }
    }
    stage('Push') {
      steps {
        withCredentials(bindings: [usernamePassword(credentialsId: 'azure_acr', usernameVariable: 'USERNAME', passwordVariable: 'PASSWORD')]) {
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
  environment {
    appName = 'building-login'
    registryHost = 'pittcontainerreg.azurecr.io/'
  }
}