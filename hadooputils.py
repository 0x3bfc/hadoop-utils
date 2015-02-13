#!/usr/bin/python
import os
import sys
import subprocess
import getpass
import hdfsutil as hdfs
import hadoopcore as hcore

__author__ = "ahmedaabdulwahed@gmail.com (Ahmed Abdullah)"
"""
	This code is used to install and configure Apache Hadoop 2.6
	It is free and anyone can copy/distribute or modify this file
"""

_HADOOP_LINK="http://www.webhostingreviewjam.com/mirror/apache/hadoop/common/hadoop-2.6.0/hadoop-2.6.0.tar.gz"
_MAIN_PATH = "/usr/local/"
_HADOOP_ROOT_DIR="%shadoop/"%(_MAIN_PATH)
_USERNAME = getpass.getuser()
_PWD_ = os.path.dirname(os.path.abspath(__file__))
_HADOOP_VERSION = _HADOOP_LINK.split('/')[-1]

def __execute(command, option=None):
	pipe = subprocess.PIPE
	p = subprocess.Popen(command,stdout=pipe,stderr=pipe,shell=True)
	if option == 'wait':
		p.wait()
	return p.stdout.read()+"\n"+p.stderr.read()

def __install_java(installed=False):
	try:
		print "INFO -- Install OpenJDK 7"
		if 'java version' in  __execute('java -version'):
			installed = True
		if not installed:
			print "INFO -- update system"
			print __execute('sudo apt-get update')
			print __execute("sudo apt-get --assume-yes install openjdk-7-jdk")
		print "INFO -- Done"
	except:
		try:
			if 'ubuntu' not in __execute('cat /etc/*-release | grep DISTRIB_ID='):
				print __execute('sudo yum update')
				print __execute('sudo yum -y install java-1.7.0-openjdk java-1.7.0-openjdk-devel')
		except:
			print "ERROR: Try to install OpenJDK manually"
			sys.exit(0)
		print "ERROR: Unable to install OpenJDK"
		sys.exit(0)
		

def __download_hadoop(link, path, downloaded=False):
	try:
		if os.path.exists("%s/%s" %(_PWD_,_HADOOP_VERSION)):
			downloaded = True
		print "INFO -- Download Apache Hadoop 2.6 ..."
		if os.path.exists(path):
			if not downloaded:
				__execute('cd %s ; sudo wget %s' %(path, link))
		else:
			__execute('sudo mkdir -p %s; wget %s' %(path, link))
		print "INFO -- Done ..."
		print "INFO -- Etract Apache Hadoop 2.6 .."
		__execute("sudo tar xvzf %s;sudo  mv %s %s/hadoop;sudo chown -R %s:%s %s/hadoop/"%(_HADOOP_VERSION ,_HADOOP_VERSION.split('.tar')[0],path, _USERNAME, _USERNAME, path ))
		print "INFO -- Done ..."
	except:
		print "ERROR: Unable to download Hadoop please check internet access"

def __config_hdfs():
	try:
		# configure name and data directories
		__execute("mkdir -p %s/hdfs/name; mkdir %s/hdfs/data"%(_HADOOP_ROOT_DIR,_HADOOP_ROOT_DIR)) 
		hdfs_template = hdfs.__generate_hdfs_site()
		with open('%s/etc/hadoop/hdfs-site.xml'%(_HADOOP_ROOT_DIR), 'w') as hdfs_obj:
			hdfs_obj.write(hdfs_template)
	except:
		print "ERROR: unable to configure HDFS "
		sys.exit(0)
		
def __config_core(namenode):
	try:
		# configure core for main node
		__execute('mkdir -p %s/tmp'%(_HADOOP_ROOT_DIR))
		core_template = hcore.__generate_core_site(namenode)		
		with open('%s/etc/hadoop/core-site.xml'%(_HADOOP_ROOT_DIR), 'w') as core_obj:
			core_obj.write(core_template)
	except:
		print "ERROR: unable to configure core-site.xml"
		sys.exit(1)
			
def __config_mapreduce(node):
	try:
		mapreduce_template = hcore.__generate_mapreduce_site(node)
		with open('%s/etc/hadoop/mapred-site.xml'%(_HADOOP_ROOT_DIR), 'w') as mapreduce_obj:
			mapreduce_obj.write(mapreduce_template)
		return True
	except:
		print "ERROR: unable to configure hadoop mapreduce on %s"%(node)
		sys.exit(0)
		
def __config_slaves(slaves, namenode):
	try:
		slaves.insert(0, namenode)
		slaves_obj = open('%s/etc/hadoop/slaves'%(_HADOOP_ROOT_DIR),'w')
		slaves_obj.writelines('\n'.join(slaves))
		slaves_obj.close()
	except:
		print "ERROR: Unable to create slaves file"
		sys.exit(0)

def __get_java_directory():
	result = __execute("update-java-alternatives -l").split('\n')
	java_dir = result[0].split(' ')[2]
	if java_dir !=None:
		return java_dir
	else:
		return False
	
def __config_hadoop_env():
	java_dir = __get_java_directory()
	if java_dir:
		env_template = hcore.__generate_hadoop_env(java_dir)
		with open('%s/etc/hadoop/hadoop-env.sh'%(_HADOOP_ROOT_DIR),'w') as hadoop_obj:
			hadoop_obj.write(env_template)
	else:
		print "ERROR: java is not configured, please check 'update-java-alternatives -l'"
		sys.exit(0)
			
def setup_core(node,namenode):
	try:
		# Hadoop pre-installation
		print "INFO -- Start Apache Hadoop Pre-Installation ...."
		__install_java()
		__download_hadoop(_HADOOP_LINK,_MAIN_PATH)
	except:
		print "ERROR: unable to pre-install packages .."
		sys.exit(0)
	
	# Install and Configure Hadoop Core
	print "INFO -- Install and Configure Hadoop Env"
	__config_hadoop_env()
	print "INFO -- Configure Hadoop Distributed File System..."
	__config_hdfs()
	print "INFO -- Configure Hadoop core"
	__config_core(namenode)
	print "INFO -- Configur Hadoop MapReduce"
	__config_mapreduce(node)

def clear(ALL=True):
	return __execute('sudo rm -rf %s/hadoop/' %(_MAIN_PATH))
					
def setup_namenode(namenode, slaves):
	# setup hadoop core
	print "INFO -- setup hadoop core"
	setup_core(namenode,namenode)
	# setup slaves list
	print "INFO -- setup slaves list"
	__config_slaves(slaves, namenode)

def setup_slave(node,namenode):
	return setup_core(node, namenode)

def start_hadoop_services():
	print "INFO -- Start all Apache Hadoop Services"
	return __execute('cd %s/sbin; ./start-all.sh;jps'%(_HADOOP_ROOT_DIR))
	
def hadooputils_help():
	return """
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
	"""
def check_hostname(node):
	hostname = __execute('hostname').split()[0]
	if hostname == node:
		return True
	else:
		return False
		
def install_master(hostsFile, hosts=[]):
	with open(hostsFile, 'r') as hosts_obj:
		hosts = hosts_obj.read().split()
	if len(hosts) >= 1:
		return setup_namenode(hosts[0], hosts[1:])
	else:
		print "ERROR: add slaves to the hosts file, only master node exists"
	
def setup_hadoop(args,node_type):
	hostsFile = hostname = namenode = None
	for arg in args:
		if '--hosts=' in arg:
			hostsFile = arg.split('=')[1]
		if '--hostname=' in arg:
			hostname = arg.split('=')[1]
		if '--namenode=' in arg:
			namenode = arg.split('=')[1]
	if node_type == 'master':
		if hostsFile !=None:
			if os.path.exists(hostsFile):
				install_master(hostsFile)
				print start_hadoop_services()
			else:
				print "ERROR: no such file or a directory %s"%(hostsFile)
				sys.exit(0)
		else:
			print "ERROR: please submit the hosts file"
			sys.exit(0)
			
	elif node_type == 'slave':
		if hostname !=None:
			if namenode !=None:
				if check_hostname(hostname):
					setup_slave(hostname,namenode)
				else:
					print "ERROR: please make sure that hostname is correct"
					sys.exit(0)
			else:
					print "ERROR: namenode is not found"
					sys.exit(0)
		else:
			print "ERROR: provide the proper hostname"
	else:
		print "ERROR node type '%s' is not found "%(node_type)
		sys.exit(0)
						
if __name__ == '__main__':
	if len(sys.argv)<=1:
		print hadooputils_help()
	else:
		if '--install=' in sys.argv[1]:
			setup_hadoop(sys.argv[2:], sys.argv[1].split('=')[1])
		elif '--clear' in sys.argv[1]:
			clear(True)
		elif '--help' in sys.argv[1]:
			print hadooputils_help()
		else:
			print hadooputils_help()
