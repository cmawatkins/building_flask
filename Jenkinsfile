node {

    checkout scm

    env.DOCKER_API_VERSION="1.23"
    
    sh "git rev-parse --short HEAD > commit-id"

    tag = readFile('commit-id').replace("\n", "").replace("\r", "")
    appName = "building-login"
    registryHost = "pittcontainerreg.azurecr.io/"
    imageName = "${registryHost}${appName}:${tag}"
    env.BUILDIMG=imageName

    stage "Build"
    
        sh "docker build -t ${imageName} -f building_flask/Dockerfile building_flask"
    
    stage "Push"

        sh "docker push ${imageName}"

    stage "Deploy"

        sh "sed 's#pittcontainerreg.azurecr.io/building-login:latest#'$BUILDIMG'#' kubernetes/deployments/building-login-front.yaml | kubectl apply -f -"
        sh "kubectl rollout status deployment/building-login-front"
}
