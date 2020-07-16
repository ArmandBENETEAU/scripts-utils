#!/bin/bash
# This script needs to be run as sudo

WORKSPACE_DIR="/home/jenkins/workspace"
OLD_BCK_DIR="$WORKSPACE_DIR/src/git.ovh.iot/redpesk/rp-webserver"
OLD_BCK_BIN_DIR="$OLD_BCK_DIR/bin"
NEW_BCK_DIR="$WORKSPACE_DIR/redpesk-backend"
NEW_BCK_BIN_DIR="$NEW_BCK_DIR/bin"

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

# 2/ Stop redpesk if running
echo "==> STOP REDPESK BACKEND <=="
echo ""
systemctl stop redpesk

# 3/ Create the directory that will contain the binaries
echo "==> CREATE REDPESK BACKEND DIRECTORIES <=="
echo ""
rm -rf "$NEW_BCK_DIR"
mkdir -p "$NEW_BCK_BIN_DIR"

# 4/ Copy the necessary configuration files
echo "==> COPY THE CONFIGURATION FILES <=="
echo ""
cp -a "$OLD_BCK_DIR/database.yml" "$NEW_BCK_DIR/database.yml"
cp -a "$OLD_BCK_BIN_DIR/rbac_iotbzh.conf" "$NEW_BCK_BIN_DIR/rbac_iotbzh.conf"

# 5/ Copy the necessary binary files
echo "==> COPY THE BINARY FILES <=="
echo ""
cp -a "$OLD_BCK_BIN_DIR/casbin-server.sh" "$NEW_BCK_BIN_DIR/casbin-server.sh"
cp -a "$OLD_BCK_BIN_DIR/casbin-server" "$NEW_BCK_BIN_DIR/casbin-server"
cp -a "$OLD_BCK_BIN_DIR/rp-webserver" "$NEW_BCK_BIN_DIR/rp-webserver"

# /6 Modify the casbin_server.sh script to point to the right /bin directory
echo "==> MODIFY CASBIN-SERVER.SH <=="
echo ""
sed -i 's,BIN_DIR=$(git rev-parse --show-toplevel)/bin,'"BIN_DIR=${NEW_BCK_BIN_DIR}"',g' "$NEW_BCK_BIN_DIR/casbin-server.sh"

# 7/ Backup and then modify the start-rp-webserver script
echo "==> BACKUP AND MODIFY START-RP-WEBSERVER <=="
echo ""
cp "$WORKSPACE_DIR/start-rp-webserver" "$WORKSPACE_DIR/start-rp-webserver-backup"
rm "$WORKSPACE_DIR/start-rp-webserver"

cat << EOF > "$WORKSPACE_DIR/start-rp-webserver"
#!/bin/bash -x
source $WORKSPACE_DIR/rp-env
cd $NEW_BCK_BIN_DIR
./casbin-server.sh --database-config $NEW_BCK_DIR/database.yml --rpserver-config /etc/redpesk/webserver/server-config.json stop
sleep 0.5
./casbin-server.sh --database-config $NEW_BCK_DIR/database.yml --rpserver-config /etc/redpesk/webserver/server-config.json start
./rp-webserver
EOF

# 8/ Delete the go source for the webserver
# rm -rf "$OLD_BCK_DIR"
echo "==> END OF SCRIPT <=="
echo "Normally, everything is ready to run redpesk on one binary."
echo "Please check it and then run \"rm -rf $OLD_BCK_DIR\" to delete the source directory"
echo "Bye bye"
