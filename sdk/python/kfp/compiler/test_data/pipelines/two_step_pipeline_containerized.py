# Copyright 2022 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from kfp import compiler
from kfp import dsl


@dsl.container_component
def component1(text: str, output_gcs: dsl.Output[dsl.Dataset]):
    return dsl.ContainerSpec(
        image='google/cloud-sdk:slim',
        command=[
            'sh -c | set -e -x', 'echo', text, '| gsutil cp -', output_gcs.uri
        ])


@dsl.container_component
def component2(input_gcs: dsl.Input[dsl.Dataset]):
    return dsl.ContainerSpec(
        image='google/cloud-sdk:slim',
        command=['sh', '-c', '|', 'set -e -x gsutil cat'],
        args=[input_gcs.uri])


@dsl.pipeline(name='containerized-two-step-pipeline')
def my_pipeline(text: str):
    component_1 = component1(text=text).set_display_name('Producer')
    component_2 = component2(input_gcs=component_1.outputs['output_gcs'])
    component_2.set_display_name('Consumer')


if __name__ == '__main__':
    compiler.Compiler().compile(
        pipeline_func=my_pipeline,
        package_path=__file__.replace('.py', '.yaml'))
