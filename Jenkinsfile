pipeline {
    agent any

    parameters {
        choice(
            name: 'TEST_ENV',
            choices: ['sit', 'uat', 'prod'],
            description: '选择测试环境'
        )
        choice(
            name: 'TEST_MARKER',
            choices: ['regression', 'smoke', 'security', 'performance'],
            description: '选择测试标签'
        )
    }

    environment {
        SIT_CREDS  = credentials('sit-api-credentials')
        UAT_CREDS  = credentials('uat-api-credentials')
        PROD_CREDS = credentials('prod-api-credentials')
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python') {
            steps {
                sh 'pip install -r requirements.txt'
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    def envCreds = [
                        sit : [user: "${SIT_CREDS_USR}",  pass: "${SIT_CREDS_PSW}"],
                        uat : [user: "${UAT_CREDS_USR}",  pass: "${UAT_CREDS_PSW}"],
                        prod: [user: "${PROD_CREDS_USR}", pass: "${PROD_CREDS_PSW}"],
                    ]
                    def creds = envCreds[params.TEST_ENV]

                    withEnv([
                        "TEST_ENV=${params.TEST_ENV}",
                        "${params.TEST_ENV.toUpperCase()}_USERNAME=${creds.user}",
                        "${params.TEST_ENV.toUpperCase()}_PASSWORD=${creds.pass}",
                    ]) {
                        sh """
                            pytest -m ${params.TEST_MARKER} \
                                --alluredir=reports/allure-results \
                                --html=reports/report.html \
                                --self-contained-html \
                                -v
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            allure([
                includeProperties: false,
                jdk              : '',
                reportBuildPolicy: 'ALWAYS',
                results          : [[path: 'reports/allure-results']]
            ])
            publishHTML(target: [
                allowMissing         : true,
                alwaysLinkToLastBuild: true,
                keepAll              : true,
                reportDir            : 'reports',
                reportFiles          : 'report.html',
                reportName           : 'Pytest HTML Report'
            ])
        }
        failure {
            echo "测试失败，请检查报告：${BUILD_URL}allure/"
        }
    }
}
