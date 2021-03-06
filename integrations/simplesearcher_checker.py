#
# Pyserini: Python interface to the Anserini IR toolkit built on Lucene
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import filecmp
import os
from typing import List


class SimpleSearcherChecker:
    def __init__(self, anserini_root: str, index: str, topics: str, pyserini_topics: str, qrels: str):
        self.anserini_root = anserini_root
        self.index_path = index
        self.topics = topics
        self.qrels = qrels
        self.pyserini_topics = pyserini_topics

        self.anserini_base_cmd = os.path.join(self.anserini_root,
                                              'target/appassembler/bin/SearchCollection -topicreader Trec')
        self.pyserini_base_cmd = 'python3 -m pyserini.search'

        self.anserini_eval = os.path.join(self.anserini_root, 'eval/trec_eval.9.0.4/trec_eval -m map -m P.30')

    @staticmethod
    def _cleanup(files: List[str]):
        for file in files:
            if os.path.exists(file):
                os.remove(file)

    def run(self, runtag: str, anserini_extras: str, pyserini_extras: str):
        print('-------------------------')
        print(f'Running {runtag}:')

        anserini_output = f'verify.anserini.{runtag}.txt'
        pyserini_output = f'verify.pyserini.{runtag}.txt'

        anserini_cmd = f'{self.anserini_base_cmd} -index {self.index_path} ' \
                       + f'-topics {self.topics} -output {anserini_output} {anserini_extras}'
        pyserini_cmd = f'{self.pyserini_base_cmd} --index {self.index_path} ' \
                       + f'--topics {self.pyserini_topics} --output {pyserini_output} {pyserini_extras}'

        os.system(anserini_cmd)
        os.system(pyserini_cmd)
        print('-------------------------')

        res = filecmp.cmp(anserini_output, pyserini_output)
        if res is True:
            print(f'[SUCCESS] {runtag} results verified!')
            eval_cmd = f'{self.anserini_eval} {self.qrels} {anserini_output}'
            os.system(eval_cmd)
            self._cleanup([anserini_output, pyserini_output])
            return True
        else:
            print(f'[FAIL] {runtag} result do not match!')
            self._cleanup([anserini_output, pyserini_output])
            return False
