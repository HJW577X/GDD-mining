# README
## Discovering Graph Differential Dependencies 
Graph differential dependencies (GDDs) provide a primitive form of integrity constraints to specify a fundamental part of the semantics of the data, which plays a key role in entity resolution. 
While several approaches for GED mining have been developed, existing methods cannot handle GDD mining efficiently. 
In this paper, we propose a novel GDD mining approach combining graph partitioning, frequent graph pattern mining, redundancy removal of graph patterns, homomorphic subgraphs matching, and differential dependency mining.
We implement the graph pattern mining and GDD mining respectively and simplify graph patterns and data graphs to improve its efficiency. 
Using real-life and synthetic datasets and comparing with the state-of-the-art approach of GDD mining, we experimentally verify the efficiency of the algorithm.
![pipeline](pipeline.jpg)

## System Requirements
- Java 1.8
- Python 3

## Python Dependencies
- pandas
- glob
- itertools
- Levenshtein
- multiprocessing

## Execution Steps
We divide the GDD mining process into the following three steps: 
1. **Frequent Subgraph Mining**:
   - input data in folder: `resource/`
   - output data in the folder: `test/process_1_producer/queryGraph`
   - run command: `java -jar GraMi_ExactSubgraphMatching-1.0-SNAPSHOT.jar filename=graph.lg datasetFolder=resource/ freq=20`
   - parameters: `filename` refers to the target graph data file, `datasetFolder` indicates the folder where the graph data is located, `freq` set frequency threshold.
2. **Homomorphic Subgraph Matching**:
   - input data in folder: `test/process_1_producer/purePattern2`
   - output data in the folder: `test/process_2_producer/pre_Table`
   - run command: `java -jar graphflow-0.1.0.jar`
3. **Dependency Mining**:
   - input data in folder: `test/process_2_producer/pre_Table`
   - output data in the folder: `result/`
   - run command: `java -jar GEDdependencyMining-1.0-SNAPSHOT.jar /path/to/python /path/to/dependency_mining.py /path/to/ -1 -1`
   - parameters: `/path/to/python` represents the current Python compiler path, `/path/to/dependency_mining.py` indicates the path to the dependency mining Python file, `/path/to` indicates the folder path where the current jar package is located, the first `-1` represents the limit on the number of attributes in the mining data table\[-1 represents unlimited\], the second `-1` represents the limit on the number of rows in the mining data table\[-1 represents unlimited\].

## Running Example
We provide an toy example dataset in the folder `resource/`, you can complete the above three steps by executing the following command: 
```
```
The following message appears to indicate that the entire process has been completed. 
```
```
You can change all the parameters in ``, and the mined GDD is recorded in the folder `result/`
## Dataset
The graph datasets used in our paper can be downloaded [here](https://drive.google.com/drive/folders/1VodFmIh5UZ4pShYM58x11iR_aRBD9PZ3?usp=drive_link).
