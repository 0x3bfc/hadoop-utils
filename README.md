# hutils
Python project to install and configure Apache Hadoop 2.6.0 on ubuntu cluster 

Add Hosts to Hostsfile

Hosts file contains all hosts of your cluster as shown below 
    
    namenode
    slavenode1  
    slavenode2
    slavenode3
    .....

First you have to install Apache Hadoop on slaves before master node, for each slave node run the following command line:  

    ./hadooputils.py --install=slave --hostname=slavenode1 --namenode=namenode
    
    INFO -- Start Apache Hadoop Pre-Installation ....
    INFO -- Install OpenJDK 7
    INFO -- Done
    INFO -- Download Apache Hadoop 2.6 ...
    INFO -- Done ...
    INFO -- Etract Apache Hadoop 2.6 ..
    INFO -- Done ...
    INFO -- Install and Configure Hadoop Env
    INFO -- Configure Hadoop Distributed File System...
    INFO -- Configure Hadoop core
    INFO -- Configur Hadoop MapReduce

The following lines 'll be shown during Hadoop installation Master node, run this command
    
    ./hadooputils.py --install=master --hosts=hostsfile.txt
    
    INFO -- setup hadoop core
    INFO -- Start Apache Hadoop Pre-Installation ....
    INFO -- Install OpenJDK 7
    INFO -- Done
    INFO -- Download Apache Hadoop 2.6 ...
    INFO -- Done ...
    INFO -- Etract Apache Hadoop 2.6 ..
    INFO -- Done ...
    INFO -- Install and Configure Hadoop Env
    INFO -- Configure Hadoop Distributed File System...
    INFO -- Configure Hadoop core
    INFO -- Configur Hadoop MapReduce
    INFO -- setup slaves list
    INFO -- Start all Apache Hadoop Services

Help:
-----
    
    	install Apache Hadoop on namenode "Master node"
    	-----------------------------------------------
    	./hadooputils.py 
    		--install=master 
    		--hosts=<HOSTLIST>
    	
    	install hadoop on slave node
    	----------------------------
    	./hadooputils.py
    		--install=slave
    		--hostname=<HOSTNAME>
    		--namenode=<MASTER_NODE>
    	
    	uninstall hadoop
    	----------------
    	./hadooputils.py
    		--clear		
