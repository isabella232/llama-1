# (c) Copyright 2008 Cloudera, Inc.
#
# module: com.cloudera.distribution.hadoopconf
#
# Writes out properties in Hadoop XML Configuration format
# e.g., hadoop-site.xml



import time

from com.cloudera.distribution.constants import *


def writePropertiesBody(handle, dict, finalKeys):
  """ Given a handle to a file opened in write mode, write the body
      of the properties file out by dumping in the entire contents of
      'dict'. Any keys in 'dict' that are in the finalKeys list are
      marked as final. """

  def writeHadoopSiteKey(handle, key):
    try:
      finalKeys.index(key)
      # it's in the list of 'final' things. Mark is that way.
      finalStr = "\n  <final>true</final>"
    except ValueError:
      # not a final value, just a default.
      finalStr = ""

    handle.write("""<property>
  <name>%(name)s</name>
  <value>%(val)s</value>%(final)s
</property>
""" % {   "name"  : key,
          "val"   : dict[key],
          "final" : finalStr })


  # Write out everything the user configured for us.
  keys = dict.keys()
  keys.sort()
  for key in keys:
    writeHadoopSiteKey(handle, key)


def writePropertiesFooter(handle):
  """ Write out the closing lines of the properties file """

  # This must be the last line in the file.
  handle.write("</configuration>\n")


def writePropertiesHeader(handle):
  """ Write out the opening lines of the properties file """

  dateStr = time.asctime()
  handle.write("""<?xml version="1.0"?>
<?xml-stylesheet type="text/xsl" href="configuration.xsl"?>

<!--
     Autogenerated by Cloudera Hadoop Installer %(ver)s on
     %(thedate)s

     You *may* edit this file. Put site-specific property overrides below.
-->
<configuration>
""" % { "ver"     : DISTRIB_VERSION,
        "thedate" : dateStr })



