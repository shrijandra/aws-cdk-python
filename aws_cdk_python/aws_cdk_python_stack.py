from aws_cdk import (
    # Duration,
    Stack,
    # aws_sqs as sqs,
    Stage,
    Environment,
    pipelines,
    # aws_cdk_python as codepipeline
    aws_codepipeline as codepipeline
)
from constructs import Construct
from resource_stack.resource_stack import ResourceStack


class DeployStage(Stage):
    def __init__(self, scope: Construct, id: str, env: Environment, **kwargs) -> None:
        super().__init__(scope, id, env=env, **kwargs)
        ResourceStack(self, 'ResourceStack', env=env, stack_name="resource-stack-deploy")


class AwsCdkPythonStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        git_input = pipelines.CodePipelineSource.connection(
            repo_string="shrijandra/aws-cdk-python",
            branch="main",
            connection_arn="arn:aws:codestar-connections:us-east-2:728878640057:connection/c82fda4f-cc01-4b0b-a3f8-bdb97bc96c6d"
        )

        code_pipeline = codepipeline.Pipeline(
            self, "Pipeline",
            pipeline_name="new-pipeline",
            cross_account_keys=False    # if pipeline and resources are in different account make this true and billing will be charged
            #always set it to false if its in same account to avoid charges.
        )

        synth_step = pipelines.ShellStep(
            id="Synth",
            install_commands=[
                'pip install -r requirements.txt'  #install dependency
            ],
            commands=[
                'npx cdk synth'  #it will create CF stack
            ],
            input=git_input     # take input from Git
        )

        pipeline = pipelines.CodePipeline(
            self, 'CodePipeline',
            self_mutation=True,  #if there are any code changes then auto muted pipeline and redeploy
            code_pipeline=code_pipeline,
            synth=synth_step
        )
             
        deployment_wave = pipeline.add_wave("DeploymentWave")  #deploy resources to pipeline

        deployment_wave.add_stage(DeployStage(
            self, 'DeployStage',
            env=(Environment(account='728878640057', region='us-east-2'))
        ))