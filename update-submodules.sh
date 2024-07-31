#!/bin/bash

git submodule update --init --recursive
cd rag-infrastructure;git checkout main; git pull; cd ..
cd rag-core-library; git checkout main; git pull; cd ..
