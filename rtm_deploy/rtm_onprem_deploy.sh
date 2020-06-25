#!/bin/bash
# This script needs to be run as sudo

RTM_USER="armand"
RTM_PASSWD="Rtm_login&password_secure"

echo ""
echo "*******************************************"
echo "********** RTM deployment script **********"
echo "*******************************************"
echo ""

# 0/ Check if the package sudo is installed on the host
echo "==> CHECK FOR SUDO PACKAGE <=="
echo ""
check_sudo_pkg=$(apt list sudo)
if [[ "$check_sudo_pkg" == *"[installed]"* ]]
then
    echo "SUCCESS ==> SUDO CORRECTLY INSTALLED"
    echo ""
else
    echo "FAILURE ==> SUDO PACKAGE NOT INSTALLED"
    echo ">> Please install the sudo package with the following command:"
    echo ">> apt-get install sudo"
    echo ""
    echo "Moreover, it is necessary to launch this script with \"sudo\" prefix"
    echo ""
fi

# 1/ Check if script run as sudo
echo "==> CHECK FOR ROOT PRIVILEGES <=="
echo ""
if [ "$EUID" -ne 0 ]
then
    echo "FAILURE ==> PLEASE RUN AS ROOT"
    exit 1
else
    echo "SUCCESS ==> WE HAVE ROOT PRIVILEGES"
    echo ""
fi

# 2/ Creation of the user "armand" used by RTMShip in Debian
echo "==> CREATION OF \"armand\" user in ProxMox host<=="
echo ""

# Add the user armand
useradd ${RTM_USER}

# Create its password
echo -e "${RTM_PASSWD}\n${RTM_PASSWD}" | passwd ${RTM_USER}

# Create the user directory
mkdir -p "/home/${RTM_USER}"

# Set the type of script used for this user
usermod --shell /bin/bash --home /home/${RTM_USER} ${RTM_USER}

# Set the ownership of the home directory to the user and fill it
chown -R ${RTM_USER}:${RTM_USER} /home/${RTM_USER}
cp /etc/skel/.* /home/${RTM_USER}/

# Add the user as sudo
adduser ${RTM_USER} sudo

# TO CONTINUE...

# X/ Set the /dev/kvm device to root:100000
echo "==> SET OWNERSHIP OF /dev/kvm <=="
echo ""

echo "KERNEL==\"kvm\", GROUP=\"100000\", MODE=\"0660\"" > /etc/udev/rules.d/99-rtm-kvm.rules
sleep 2
check_dev_kvm=$(ls -al /dev/kvm)

if [[ "$check_dev_kvm" == *"root 100000"* ]]
then
    echo "SUCCESS ==> /dev/kvm OWNERSHIP CORRECTLY SETTED"
    echo ""
else
    echo "FAILURE ==> /dev/kvm OWNERSHIP BADLY SETTED"
    echo ">> It could be necessary to restart the ProxMox host."
    echo ">> Afterwards, the result of \"ls -al\" command should be:"
    echo ">> crw-rw---- 1 root 100000 10, 232 Jun 25 11:35 /dev/kvm"
    echo ""
fi

echo ""
echo "*******************************************"
echo "******* End of RTM deployment script ******"
echo "*******************************************"
echo ""