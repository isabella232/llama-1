# (c) Copyright 2008 Cloudera, Inc.
#
# module: distrotester.setup.fedora8
#
# Sets up expected/necessary packages on a Fedora Core 8 installation


import os

import com.cloudera.tools.shell as shell

from   distrotester.constants import *
from   distrotester.setup.platformsetup import PlatformSetup


class Fedora8Setup(PlatformSetup):
  """ Performs setup of packages on a Fedora Core 8 installation.
      Works on both i386 and x86_64 architectures; one of the
      strings "i386" or "x86_64" must be provided as the 'arch'
      parameter to the c'tor.
  """

  def __init__(self, arch, properties):
    PlatformSetup.__init__(self, properties)
    self.arch = arch

    self.bucket = properties.getProperty(PACKAGE_BUCKET_KEY, \
        PACKAGE_BUCKET_DEFAULT)


  def remoteBootstrap(self):
    """ Remote bootstrap for Fedora 8 """

    # Need to make sure we can use python!
    # Also, ruby for s3cmd
    return [
      "yum -y install python python-devel ruby rsync"
    ]

  def initProperties(self):
    """ Set any properties specific to this platform """

    # set the java home location
    if self.arch == "x86_64":
      self.properties.setProperty(JAVA_HOME_KEY, "/usr/java/jdk1.6.0_07")
    elif self.arch == "i386":
      self.properties.setProperty(JAVA_HOME_KEY, "/usr/java/jdk1.6.0_10")

  def writeSshConfig(self, handle):
    """ write an ssh config file for unattended use to the
        open file handle """

    handle.write("""
Host *
  StrictHostKeyChecking no
  PasswordAuthentication no
  GSSAPIAuthentication no
  NoHostAuthenticationForLocalhost yes
  ServerAliveInterval 60
  ServerAliveCountMax 60
""")



  def makeUser(self, username, rootSshKeys=True):
    """ Make a user account on the machine. if rootSshKeys is true,
        copy the authorized_keys and id_rsa files from /root/.ssh/ """

    try:
      # if we can get the user's passwd entry, we don't need to make it
      shell.sh("getent passwd " + username)
    except shell.CommandError, ce:
      # we do.
      shell.sh("useradd --create-home " + username)

    shell.sh("mkdir -p /home/" + username + "/.ssh")
    shell.sh("chmod 0755 /home/" + username)
    shell.sh("chmod 0750 /home/" + username + "/.ssh")

    if rootSshKeys:
      shell.sh("cp /root/.ssh/authorized_keys /home/" + username + "/.ssh")
      shell.sh("cp /root/.ssh/id_rsa /home/" + username + "/.ssh")
      shell.sh("chmod 0600 /home/" + username + "/.ssh/authorized_keys")
      shell.sh("chmod 0600 /home/" + username + "/.ssh/id_rsa")

    shell.sh("chown " + username + ":" + username \
        +" /home/" + username)

    handle = open("/home/" + username + "/.ssh/config", "w")
    self.writeSshConfig(handle)
    handle.close()

    shell.sh("chown " + username + ":" + username \
        +" -R /home/" + username + "/.ssh")


  def removePackage(self, package):
    shell.sh("yum -y remove " + package)

  def installPackage(self, package):
    shell.sh("yum -y install " + package)

  def setup(self):
    """ Install on Fedora 8. """

    # We download java with s3cmd. We need that first.
    s3dest = os.path.join(PACKAGE_TARGET, S3CMD_PACKAGE_NAME)
    self.wget(S3CMD_URL, s3dest)

    self.untar(s3dest, PACKAGE_TARGET)

    s3destDir = os.path.join(PACKAGE_TARGET, "s3sync/*.rb")
    shell.sh("cp " + s3destDir + " /usr/bin")

    # now install Java.
    if self.arch == "x86_64":
      jdkPackage = "jdk-6u7-linux-" + self.arch + "-rpm.bin"
    elif self.arch == "i386":
      jdkPackage = "jdk-6u10-linux-" + self.arch + "-rpm.bin"

    jdkPath = self.properties.getProperty(JAVA_HOME_KEY)
    jdkPackageDest = os.path.join(PACKAGE_TARGET, jdkPackage)

    self.s3get(self.bucket, "packages/" + jdkPackage, jdkPackageDest)
    shell.sh("yum -y install yum-allowdowngrade")
    shell.sh("yum -y remove \"java-*-icedtea\" \"java-*-icedtea-devel\" " \
        + "\"java-*-icedtea-plugin\"")
    shell.sh("yum -y install compat-libstdc++-33 compat-libstdc++-296")
    shell.sh("chmod 0700 \"" + jdkPackageDest + "\"")

    # do the "more hack" to deny Java the right to have user intervention.
    # We accept the license; we don't need to have someone sit here and type
    # it in every time.
    shell.sh("mv /bin/more /bin/no.more")

    # Actually install Java!
    shell.sh("yes | " + jdkPackageDest + " -noregister")

    handle = open("/etc/profile", "a")
    handle.write("\nexport JAVA_HOME=" + jdkPath + "\n")
    handle.close()

    # restore 'more' to where it should be.
    shell.sh("mv /bin/no.more /bin/more")

    # install other packages that make this a more sane system to use.
    shell.sh("yum -y install screen lzo")
    shell.sh("yum -y install xeyes xauth")
    shell.sh("yum -y install xml-commons-apis")

    # configure ssh so that it doesn't raise a fuss about unknwon hosts
    handle = open("/root/.ssh/config", "w")
    self.writeSshConfig(handle)
    handle.close()

    self.makeUser(HADOOP_USER)
    self.makeUser(CLIENT_USER)

    # Change the sudoers file to preserve environment variables we
    # care a lot about.
    # TODO(aaron): If you add an environment variable to the install plan,
    # you have to add it here. This is unfortunate; we shouldn't need to
    # list all this twice.
    handle = open("/etc/sudoers", "a")
    handle.write("""
Defaults  env_keep += "JAVA_HOME HADOOPDIR HADOOP_HOME PIGDIR PIG_CLASSPATH"
""")
    handle.close()

